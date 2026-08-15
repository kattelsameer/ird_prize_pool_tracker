from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class ErrorResponse(BaseModel):
    """Structured, user-safe error body. Never includes stack traces or
    internal details (CLAUDE.md §43) -- those are logged server-side only.
    """

    detail: str
