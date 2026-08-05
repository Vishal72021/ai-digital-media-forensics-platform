"""Verification for authentication API endpoints."""

from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.api.dependencies.services import get_authentication_service
from app.domain.exceptions import (
    DuplicateEmailException,
    PasswordPolicyViolation,
)
from app.factory import create_application
from app.models.user import User
from app.services.authentication import AuthenticationService


@pytest.fixture
def authentication_service() -> Mock:
    """Provide a mocked authentication service."""

    return Mock(spec=AuthenticationService)


@pytest.fixture
def application(
    authentication_service: Mock,
) -> Iterator[FastAPI]:
    """Create an application with overridden dependencies."""

    application = create_application()

    application.dependency_overrides[get_authentication_service] = lambda: authentication_service

    try:
        yield application
    finally:
        application.dependency_overrides.clear()


@pytest.fixture
def client(
    application: FastAPI,
) -> Iterator[TestClient]:
    """Provide an HTTP client for endpoint testing."""

    with TestClient(
        application,
        raise_server_exceptions=False,
    ) as test_client:
        yield test_client


def test_register_returns_created_user(
    client: TestClient,
    authentication_service: Mock,
) -> None:
    """Successful registration returns the created user."""

    user = User(
        email="alice@example.com",
    )

    user.id = uuid4()
    user.created_at = datetime.now(UTC)
    user.updated_at = datetime.now(UTC)

    authentication_service.register.return_value = user

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == status.HTTP_201_CREATED

    payload = response.json()

    assert payload["id"] == str(user.id)
    assert payload["email"] == user.email

    assert "created_at" in payload
    assert "updated_at" in payload

    authentication_service.register.assert_called_once_with(
        email="alice@example.com",
        password="Password123!",
    )


def test_register_rejects_invalid_email(
    client: TestClient,
    authentication_service: Mock,
) -> None:
    """Registration rejects an invalid email address."""

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "Password123!",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    payload = response.json()

    assert "detail" in payload

    authentication_service.register.assert_not_called()


def test_register_requires_email(
    client: TestClient,
    authentication_service: Mock,
) -> None:
    """Registration requires an email address."""

    response = client.post(
        "/api/v1/auth/register",
        json={
            "password": "Password123!",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    payload = response.json()

    assert "detail" in payload

    authentication_service.register.assert_not_called()


def test_register_requires_password(
    client: TestClient,
    authentication_service: Mock,
) -> None:
    """Registration requires a password."""

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    payload = response.json()

    assert "detail" in payload

    authentication_service.register.assert_not_called()


def test_register_returns_conflict_for_duplicate_email(
    client: TestClient,
    authentication_service: Mock,
) -> None:
    """Duplicate email registration returns a conflict response."""

    authentication_service.register.side_effect = DuplicateEmailException(
        "alice@example.com",
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT

    payload = response.json()

    assert payload["title"] == "Conflict"
    assert payload["status"] == 409
    assert payload["detail"] == "Email 'alice@example.com' is already registered."
    assert payload["type"].endswith("/conflict")


def test_register_returns_validation_failure_for_password_policy_violation(
    client: TestClient,
    authentication_service: Mock,
) -> None:
    """Password policy violations return a validation response."""

    authentication_service.register.side_effect = PasswordPolicyViolation(
        "Password does not satisfy the password policy.",
    )

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "weak",
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    payload = response.json()

    assert payload["title"] == "Validation Failed"
    assert payload["status"] == 422
    assert payload["detail"] == "Password does not satisfy the password policy."
    assert payload["type"].endswith("/validation")


def test_register_returns_internal_server_error_for_unexpected_exception(
    client: TestClient,
    authentication_service: Mock,
) -> None:
    """Unexpected failures return a generic internal server error."""

    authentication_service.register.side_effect = RuntimeError("boom")

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "alice@example.com",
            "password": "Password123!",
        },
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    payload = response.json()

    assert payload["title"] == "Internal Server Error"
    assert payload["status"] == 500
    assert payload["detail"] == "An unexpected error occurred."
    assert payload["type"] == "about:blank"
