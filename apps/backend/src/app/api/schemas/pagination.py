"""Pagination API schemas."""

from __future__ import annotations

from pydantic import Field

from app.api.schemas.common import BaseSchema


class PageMetadata(BaseSchema):
    """Pagination metadata."""

    page: int = Field(ge=1)
    page_size: int = Field(ge=1, le=100)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class PaginatedResponse[T](BaseSchema):
    """Generic paginated response."""

    items: list[T]

    page: PageMetadata
