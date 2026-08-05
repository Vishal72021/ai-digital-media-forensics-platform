"""Verification for the user service."""

from __future__ import annotations

from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.domain.exceptions import (
    DuplicateEmailException,
    UserNotFoundException,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.user import UserService


def test_create_user_persists_without_committing() -> None:
    """User creation leaves transaction ownership to the caller."""

    repository = Mock(spec=UserRepository)
    service = UserService(repository)

    user = User(email="alice@example.com")

    repository.get_by_email.return_value = None
    repository.create.return_value = user

    created_user = service.create_user(user)

    assert created_user is user

    repository.get_by_email.assert_called_once_with(user.email)
    repository.create.assert_called_once_with(user)
    repository.commit.assert_not_called()


def test_create_user_rejects_duplicate_email() -> None:
    """Duplicate email detection remains unchanged."""

    repository = Mock(spec=UserRepository)
    service = UserService(repository)

    user = User(email="alice@example.com")

    repository.get_by_email.return_value = user

    with pytest.raises(DuplicateEmailException):
        service.create_user(user)

    repository.create.assert_not_called()
    repository.commit.assert_not_called()


def test_delete_user_marks_user_for_deletion_without_committing() -> None:
    """User deletion leaves transaction ownership to the caller."""

    repository = Mock(spec=UserRepository)
    service = UserService(repository)

    user = User(email="alice@example.com")

    repository.get_by_id.return_value = user

    service.delete_user(user.id)

    repository.delete.assert_called_once_with(user)
    repository.commit.assert_not_called()


def test_delete_user_raises_when_user_missing() -> None:
    """Deleting a missing user preserves existing behavior."""

    repository = Mock(spec=UserRepository)
    service = UserService(repository)

    repository.get_by_id.return_value = None

    with pytest.raises(UserNotFoundException):
        service.delete_user(uuid4())

    repository.delete.assert_not_called()
    repository.commit.assert_not_called()
