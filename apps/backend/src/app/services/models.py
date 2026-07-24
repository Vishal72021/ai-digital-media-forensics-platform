"""Application service result models."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.user import User


@dataclass(frozen=True, slots=True)
class UserPage:
    """Paginated user collection."""

    items: list[User]
    total_items: int
    page: int
    page_size: int
