"""Pagination schemas and helpers.

Defines a generic, offset-based page envelope and validated page parameters.
"""

from __future__ import annotations

from math import ceil
from typing import Generic, Optional, Sequence, TypeVar

from pydantic import BaseModel, Field, field_validator

from app.core.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar("T")


class PageParams(BaseModel):
    """Validated pagination query parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE)

    @field_validator("page_size")
    @classmethod
    def _cap_page_size(cls, value: int) -> int:
        return min(value, MAX_PAGE_SIZE)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class Page(BaseModel, Generic[T]):
    """A page of results."""

    items: list[T] = Field(default_factory=list)
    total: int = Field(default=0, ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=DEFAULT_PAGE_SIZE, ge=1)
    pages: int = Field(default=0, ge=0)
    has_next: bool = False
    has_previous: bool = False

    @classmethod
    def create(
        cls,
        items: Sequence[T],
        *,
        total: int,
        page: int,
        page_size: int,
    ) -> "Page[T]":
        pages = ceil(total / page_size) if page_size else 0
        return cls(
            items=list(items),
            total=total,
            page=page,
            page_size=page_size,
            pages=pages,
            has_next=page < pages,
            has_previous=page > 1,
        )


def pagination_meta(
    *, total: int, page: int, page_size: int
) -> dict[str, Optional[int] | bool]:
    """Return pagination metadata as a plain dict."""
    pages = ceil(total / page_size) if page_size else 0
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "has_next": page < pages,
        "has_previous": page > 1,
    }
