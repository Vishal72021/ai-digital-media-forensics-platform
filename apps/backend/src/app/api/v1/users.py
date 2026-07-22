"""User API endpoints."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from fastapi import APIRouter, status

from app.api.dependencies.services import UserServiceDependency
from app.api.schemas.user import (
    CreateUserRequest,
    UserResponse,
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

    return cast(
        UserResponse,
        UserResponse.model_validate(created_user),
    )


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

    return cast(
        UserResponse,
        UserResponse.model_validate(user),
    )
