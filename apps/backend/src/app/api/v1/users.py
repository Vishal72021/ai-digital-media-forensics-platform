"""User API endpoints."""

from __future__ import annotations

from math import ceil
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status

from app.api.dependencies.services import UserServiceDependency
from app.api.schemas.pagination import PageMetadata, PaginatedResponse
from app.api.schemas.user import (
    CreateUserRequest,
    UserResponse,
    UserSummary,
)
from app.models.user import User

users_router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@users_router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    request: CreateUserRequest,
    service: UserServiceDependency,
) -> UserResponse:
    """Create a new user."""

    user = User(
        email=request.email,
    )

    created_user = service.create_user(user)

    response: UserResponse = UserResponse.model_validate(created_user)

    return response


@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
)
def get_user(
    user_id: UUID,
    service: UserServiceDependency,
) -> UserResponse:
    """Retrieve a user by identifier."""

    user = service.get_user(user_id)

    response: UserResponse = UserResponse.model_validate(user)

    return response


@users_router.get(
    "",
    response_model=PaginatedResponse[UserSummary],
)
def list_users(
    service: UserServiceDependency,
    page: Annotated[
        int,
        Query(
            ge=1,
            description="One-based page number.",
        ),
    ] = 1,
    page_size: Annotated[
        int,
        Query(
            ge=1,
            le=100,
            description="Number of users per page.",
        ),
    ] = 20,
) -> PaginatedResponse[UserSummary]:
    """Retrieve a paginated collection of users."""

    user_page = service.list_users(
        page=page,
        page_size=page_size,
    )

    items = [UserSummary.model_validate(user) for user in user_page.items]

    total_pages = (
        ceil(user_page.total_items / user_page.page_size) if user_page.total_items > 0 else 0
    )

    return PaginatedResponse[UserSummary](
        items=items,
        page=PageMetadata(
            page=user_page.page,
            page_size=user_page.page_size,
            total_items=user_page.total_items,
            total_pages=total_pages,
        ),
    )


@users_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(
    user_id: UUID,
    service: UserServiceDependency,
) -> Response:
    """Delete a user by identifier."""

    service.delete_user(user_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
