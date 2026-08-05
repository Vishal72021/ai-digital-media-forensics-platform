"""Authentication API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.api.dependencies.services import AuthenticationServiceDependency
from app.api.schemas.authentication import RegisterUserRequest
from app.api.schemas.user import UserResponse

authentication_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@authentication_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterUserRequest,
    service: AuthenticationServiceDependency,
) -> UserResponse:
    """Register a new platform user."""

    user = service.register(
        email=request.email,
        password=request.password,
    )

    return UserResponse.model_validate(user)
