"""Verification for the authentication service."""

from __future__ import annotations

from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.domain.exceptions import (
    DuplicateEmailException,
    PasswordPolicyViolation,
)
from app.models.user import User
from app.services.authentication import AuthenticationService


def create_service():
    """Create a fully mocked authentication service."""

    user_service = Mock()
    credential_service = Mock()
    transaction_manager = Mock()

    service = AuthenticationService(
        user_service=user_service,
        credential_service=credential_service,
        transaction_manager=transaction_manager,
    )

    return (
        service,
        user_service,
        credential_service,
        transaction_manager,
    )


def test_register_creates_user_and_password_credential() -> None:
    """Registration orchestrates both user and credential creation."""

    (
        service,
        user_service,
        credential_service,
        transaction_manager,
    ) = create_service()

    created_user = User(email="alice@example.com")
    created_user.id = uuid4()

    user_service.create_user.return_value = created_user

    result = service.register(
        email="alice@example.com",
        password="correct horse battery staple",
    )

    assert result is created_user

    user_service.create_user.assert_called_once()

    credential_service.create.assert_called_once_with(
        created_user.id,
        "correct horse battery staple",
    )

    transaction_manager.commit.assert_called_once()
    transaction_manager.rollback.assert_not_called()


def test_register_rolls_back_duplicate_email() -> None:
    """Duplicate registration rolls back the transaction."""

    (
        service,
        user_service,
        credential_service,
        transaction_manager,
    ) = create_service()

    user_service.create_user.side_effect = DuplicateEmailException(
        "alice@example.com",
    )

    with pytest.raises(DuplicateEmailException):
        service.register(
            email="alice@example.com",
            password="password",
        )

    credential_service.create.assert_not_called()

    transaction_manager.commit.assert_not_called()
    transaction_manager.rollback.assert_called_once()


def test_register_rolls_back_password_policy_violation() -> None:
    """Credential creation failure rolls back registration."""

    (
        service,
        user_service,
        credential_service,
        transaction_manager,
    ) = create_service()

    created_user = User(email="alice@example.com")
    created_user.id = uuid4()

    user_service.create_user.return_value = created_user

    credential_service.create.side_effect = PasswordPolicyViolation(
        "Invalid password.",
    )

    with pytest.raises(PasswordPolicyViolation):
        service.register(
            email="alice@example.com",
            password="short",
        )

    transaction_manager.commit.assert_not_called()
    transaction_manager.rollback.assert_called_once()


def test_register_rolls_back_unexpected_exception() -> None:
    """Unexpected failures also roll back the transaction."""

    (
        service,
        user_service,
        credential_service,
        transaction_manager,
    ) = create_service()

    created_user = User(email="alice@example.com")
    created_user.id = uuid4()

    user_service.create_user.return_value = created_user

    credential_service.create.side_effect = RuntimeError("boom")

    with pytest.raises(RuntimeError):
        service.register(
            email="alice@example.com",
            password="password",
        )

    transaction_manager.commit.assert_not_called()
    transaction_manager.rollback.assert_called_once()


def test_register_commits_exactly_once() -> None:
    """Successful registration commits exactly once."""

    (
        service,
        user_service,
        credential_service,
        transaction_manager,
    ) = create_service()

    created_user = User(email="alice@example.com")
    created_user.id = uuid4()

    user_service.create_user.return_value = created_user

    service.register(
        email="alice@example.com",
        password="password",
    )

    transaction_manager.commit.assert_called_once()
    transaction_manager.rollback.assert_not_called()
