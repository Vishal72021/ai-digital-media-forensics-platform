"""Verification for password credential lifecycle orchestration."""

from __future__ import annotations

import uuid
from unittest.mock import Mock

import pytest

from app.domain.exceptions.security import PasswordPolicyViolation
from app.domain.security.password_policy import PasswordPolicy
from app.models.password_credential import PasswordCredential
from app.repositories.security.credential_repository import CredentialRepository
from app.security.credential_service import CredentialService
from app.security.password_hasher import PasswordHasher


def _build_service(
    repository: CredentialRepository,
) -> CredentialService:
    """Build a credential service using production password primitives."""
    return CredentialService(
        repository=repository,
        password_policy=PasswordPolicy(),
        password_hasher=PasswordHasher(),
    )


def test_create_adds_hashed_password_credential() -> None:
    """Credential creation hashes accepted password material before persistence."""
    repository = Mock(spec=CredentialRepository)
    repository.add.side_effect = lambda credential: credential

    service = _build_service(repository)
    user_id = uuid.uuid4()
    password = "correct horse battery staple"

    credential = service.create(user_id, password)

    assert credential.user_id == user_id
    assert credential.password_hash != password
    assert credential.password_hash.startswith("$argon2id$")
    repository.add.assert_called_once_with(credential)


def test_create_rejects_password_that_violates_policy() -> None:
    """Credential creation rejects password material outside canonical policy."""
    repository = Mock(spec=CredentialRepository)
    service = _build_service(repository)

    with pytest.raises(PasswordPolicyViolation):
        service.create(uuid.uuid4(), "short")

    repository.add.assert_not_called()


def test_create_does_not_persist_plaintext_password() -> None:
    """The persistence boundary receives only the encoded password representation."""
    repository = Mock(spec=CredentialRepository)
    repository.add.side_effect = lambda credential: credential

    service = _build_service(repository)
    password = "sentinel-password-material"

    credential = service.create(uuid.uuid4(), password)

    persisted_credential = repository.add.call_args.args[0]

    assert persisted_credential is credential
    assert persisted_credential.password_hash != password
    assert password not in persisted_credential.password_hash


def test_verify_returns_true_for_matching_password() -> None:
    """Verification succeeds when supplied material matches stored credential state."""
    user_id = uuid.uuid4()
    password = "correct horse battery staple"
    password_hash = PasswordHasher().hash(password)

    repository = Mock(spec=CredentialRepository)
    repository.get_by_user_id.return_value = PasswordCredential(
        user_id=user_id,
        password_hash=password_hash,
    )

    service = _build_service(repository)

    assert service.verify(user_id, password) is True
    repository.get_by_user_id.assert_called_once_with(user_id)


def test_verify_returns_false_for_non_matching_password() -> None:
    """Verification fails when supplied material does not match stored state."""
    user_id = uuid.uuid4()
    password_hash = PasswordHasher().hash("correct horse battery staple")

    repository = Mock(spec=CredentialRepository)
    repository.get_by_user_id.return_value = PasswordCredential(
        user_id=user_id,
        password_hash=password_hash,
    )

    service = _build_service(repository)

    assert service.verify(user_id, "different password material") is False


def test_verify_returns_false_when_credential_does_not_exist() -> None:
    """Verification fails when the user has no password credential."""
    repository = Mock(spec=CredentialRepository)
    repository.get_by_user_id.return_value = None

    service = _build_service(repository)
    user_id = uuid.uuid4()

    assert service.verify(user_id, "correct horse battery staple") is False
    repository.get_by_user_id.assert_called_once_with(user_id)


def test_verify_performs_dummy_verification_when_credential_is_missing() -> None:
    """Missing credentials still perform password verification work."""

    repository = Mock(spec=CredentialRepository)
    repository.get_by_user_id.return_value = None

    password_hasher = Mock(spec=PasswordHasher)

    service = CredentialService(
        repository=repository,
        password_policy=PasswordPolicy(),
        password_hasher=password_hasher,
    )

    service.verify(uuid.uuid4(), "supplied password")

    password_hasher.verify_dummy.assert_called_once_with(
        "supplied password",
    )


def test_verify_does_not_perform_dummy_verification_when_credential_exists() -> None:
    """Dummy verification is skipped when a credential exists."""

    user_id = uuid.uuid4()

    repository = Mock(spec=CredentialRepository)
    repository.get_by_user_id.return_value = PasswordCredential(
        user_id=user_id,
        password_hash=PasswordHasher().hash("correct horse battery staple"),
    )

    password_hasher = Mock(spec=PasswordHasher)
    password_hasher.verify.return_value = True

    service = CredentialService(
        repository=repository,
        password_policy=PasswordPolicy(),
        password_hasher=password_hasher,
    )

    assert service.verify(user_id, "correct horse battery staple")

    password_hasher.verify_dummy.assert_not_called()
