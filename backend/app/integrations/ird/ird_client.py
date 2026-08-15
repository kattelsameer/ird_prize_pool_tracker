"""HTTP client for the public IRD winners API (CLAUDE.md §8, §37, §39).

This is the ONLY module allowed to know the IRD HTTP endpoint shape. Everything
downstream consumes `NormalizedSyncPage`/`NormalizedWinnerRecord` from
`app.integrations.ird.adapter`.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass

import httpx

from app.integrations.ird.adapter import (
    IrdResponseValidationError,
    NormalizedSyncPage,
    adapt_winners_response,
)

logger = logging.getLogger("app.integrations.ird")

DEFAULT_BASE_URL = "https://prize.ird.gov.np/api/v1/public"
DEFAULT_PAGE_LIMIT = 100
DEFAULT_TIMEOUT_SECONDS = 15.0
MAX_RETRIES = 3
BACKOFF_BASE_SECONDS = 1.0


class IrdClientError(Exception):
    """Base class for all IRD client failures (network, timeout, malformed data)."""


class IrdTimeoutError(IrdClientError):
    pass


class IrdConnectionError(IrdClientError):
    pass


class IrdHttpStatusError(IrdClientError):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


class IrdMalformedResponseError(IrdClientError):
    pass


@dataclass
class IrdClientConfig:
    base_url: str = DEFAULT_BASE_URL
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    page_limit: int = DEFAULT_PAGE_LIMIT
    max_retries: int = MAX_RETRIES
    max_pages: int = 200  # self-limit: never page unboundedly (CLAUDE.md §39)


class IrdClient:
    """Thin, retrying HTTP client for the public winners endpoint.

    A single `httpx.Client` (or an injected transport, for tests) is used for
    all requests. Retries use exponential backoff and are capped at
    `max_retries` attempts per page -- this client never retries indefinitely
    and never hammers the government service (CLAUDE.md §39).
    """

    def __init__(
        self,
        config: IrdClientConfig | None = None,
        transport: httpx.BaseTransport | None = None,
    ):
        self.config = config or IrdClientConfig()
        self._client = httpx.Client(
            base_url=self.config.base_url,
            timeout=self.config.timeout_seconds,
            transport=transport,
            headers={"Accept": "application/json"},
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "IrdClient":
        return self

    def __exit__(self, *exc_info) -> None:
        self.close()

    def _get_page(self, *, limit: int, offset: int) -> dict:
        last_error: Exception | None = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                response = self._client.get(
                    "/winners", params={"limit": limit, "offset": offset}
                )
            except httpx.TimeoutException as exc:
                last_error = IrdTimeoutError(f"IRD request timed out: {exc}")
            except httpx.ConnectError as exc:
                last_error = IrdConnectionError(f"IRD connection failed: {exc}")
            except httpx.HTTPError as exc:
                last_error = IrdConnectionError(f"IRD request failed: {exc}")
            else:
                if response.status_code != 200:
                    last_error = IrdHttpStatusError(
                        response.status_code,
                        f"IRD returned HTTP {response.status_code}",
                    )
                else:
                    try:
                        return response.json()
                    except ValueError as exc:
                        last_error = IrdMalformedResponseError(
                            f"IRD response was not valid JSON: {exc}"
                        )

            if attempt < self.config.max_retries:
                backoff = BACKOFF_BASE_SECONDS * (2 ** (attempt - 1))
                logger.warning(
                    "IRD request attempt %s/%s failed (%s); retrying in %.1fs",
                    attempt,
                    self.config.max_retries,
                    last_error,
                    backoff,
                )
                time.sleep(backoff)

        assert last_error is not None
        raise last_error

    def fetch_all_pages(self) -> list[NormalizedSyncPage]:
        """Fetch every page of winners, offset-paginating until `has_more` is
        False or the self-limit `max_pages` is reached. Raises IrdClientError
        subclasses on any failure; caller (sync service) must catch these and
        preserve existing data (CLAUDE.md §68).
        """
        pages: list[NormalizedSyncPage] = []
        offset = 0
        for _ in range(self.config.max_pages):
            raw = self._get_page(limit=self.config.page_limit, offset=offset)
            try:
                page = adapt_winners_response(raw)
            except IrdResponseValidationError as exc:
                raise IrdMalformedResponseError(str(exc)) from exc
            pages.append(page)
            if not page.has_more:
                break
            offset += self.config.page_limit
        return pages
