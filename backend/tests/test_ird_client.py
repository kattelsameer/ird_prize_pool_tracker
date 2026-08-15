import json
import unittest
from urllib.parse import parse_qs, urlparse

import httpx

from app.integrations.ird.ird_client import (
    IrdClient,
    IrdClientConfig,
    IrdConnectionError,
    IrdHttpStatusError,
    IrdMalformedResponseError,
    IrdTimeoutError,
)
from tests.data_ird_client import SINGLE_EMPTY_PAGE, TWO_PAGE_RESPONSES_BY_OFFSET


def _offset_from_request(request: httpx.Request) -> int:
    qs = parse_qs(urlparse(str(request.url)).query)
    return int(qs["offset"][0])


def _client_with_handler(handler) -> IrdClient:
    transport = httpx.MockTransport(handler)
    config = IrdClientConfig(page_limit=2, max_retries=2)
    return IrdClient(config=config, transport=transport)


class IrdClientPaginationTests(unittest.TestCase):
    def test_fetches_all_pages_until_has_more_false(self):
        def handler(request: httpx.Request) -> httpx.Response:
            offset = _offset_from_request(request)
            return httpx.Response(200, json=TWO_PAGE_RESPONSES_BY_OFFSET[offset])

        with _client_with_handler(handler) as client:
            pages = client.fetch_all_pages()

        self.assertEqual(len(pages), 2)
        all_winners = [w for page in pages for w in page.winners]
        self.assertEqual(
            {w.prize_coupon_number for w in all_winners},
            {"111111111111", "222222222222"},
        )

    def test_idempotent_repeated_fetch_produces_same_result(self):
        def handler(request: httpx.Request) -> httpx.Response:
            offset = _offset_from_request(request)
            return httpx.Response(200, json=TWO_PAGE_RESPONSES_BY_OFFSET[offset])

        with _client_with_handler(handler) as client:
            first = client.fetch_all_pages()
            second = client.fetch_all_pages()

        first_ids = sorted(w.source_record_id for page in first for w in page.winners)
        second_ids = sorted(w.source_record_id for page in second for w in page.winners)
        self.assertEqual(first_ids, second_ids)

    def test_empty_response_returns_zero_winners_without_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json=SINGLE_EMPTY_PAGE)

        with _client_with_handler(handler) as client:
            pages = client.fetch_all_pages()

        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0].winners, [])


class IrdClientFailureTests(unittest.TestCase):
    def test_timeout_raises_ird_timeout_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectTimeout("simulated timeout", request=request)

        with _client_with_handler(handler) as client:
            with self.assertRaises(IrdTimeoutError):
                client.fetch_all_pages()

    def test_connection_error_raises_ird_connection_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("simulated connection failure", request=request)

        with _client_with_handler(handler) as client:
            with self.assertRaises(IrdConnectionError):
                client.fetch_all_pages()

    def test_non_200_status_raises_ird_http_status_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(503, text="service unavailable")

        with _client_with_handler(handler) as client:
            with self.assertRaises(IrdHttpStatusError) as ctx:
                client.fetch_all_pages()
        self.assertEqual(ctx.exception.status_code, 503)

    def test_malformed_non_json_response_raises_malformed_response_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, text="<html>not json</html>")

        with _client_with_handler(handler) as client:
            with self.assertRaises(IrdMalformedResponseError):
                client.fetch_all_pages()

    def test_structurally_invalid_json_raises_malformed_response_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"unexpected": "shape"})

        with _client_with_handler(handler) as client:
            with self.assertRaises(IrdMalformedResponseError):
                client.fetch_all_pages()

    def test_retries_then_succeeds_after_transient_failure(self):
        attempts = {"count": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise httpx.ConnectError("transient failure", request=request)
            return httpx.Response(200, json=SINGLE_EMPTY_PAGE)

        with _client_with_handler(handler) as client:
            pages = client.fetch_all_pages()

        self.assertEqual(attempts["count"], 2)
        self.assertEqual(len(pages), 1)

    def test_exhausts_retries_and_raises_last_error(self):
        def handler(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("always fails", request=request)

        config = IrdClientConfig(page_limit=2, max_retries=2)
        transport = httpx.MockTransport(handler)
        client = IrdClient(config=config, transport=transport)
        with client:
            with self.assertRaises(IrdConnectionError):
                client.fetch_all_pages()


if __name__ == "__main__":
    unittest.main()
