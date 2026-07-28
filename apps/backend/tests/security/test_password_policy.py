"""Verification for the canonical password acceptance policy."""

from __future__ import annotations

import pytest

from app.domain.exceptions import PasswordPolicyViolation
from app.domain.security import (
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    PasswordPolicy,
)


def test_password_policy_has_frozen_length_bounds() -> None:
    """The canonical password length bounds remain frozen."""

    assert MIN_PASSWORD_LENGTH == 12
    assert MAX_PASSWORD_LENGTH == 128


@pytest.mark.parametrize(
    "length",
    [
        MIN_PASSWORD_LENGTH,
        MIN_PASSWORD_LENGTH + 1,
        MAX_PASSWORD_LENGTH - 1,
        MAX_PASSWORD_LENGTH,
    ],
)
def test_password_policy_accepts_valid_boundary_lengths(length: int) -> None:
    """Passwords within the inclusive frozen bounds are accepted."""

    password = "a" * length

    PasswordPolicy().validate(password)


@pytest.mark.parametrize(
    "length",
    [
        MIN_PASSWORD_LENGTH - 1,
        MAX_PASSWORD_LENGTH + 1,
    ],
)
def test_password_policy_rejects_invalid_boundary_lengths(length: int) -> None:
    """Passwords outside the frozen bounds are rejected."""

    password = "a" * length

    with pytest.raises(PasswordPolicyViolation):
        PasswordPolicy().validate(password)


def test_password_policy_allows_unicode() -> None:
    """Unicode characters are valid password material."""

    password = "密码安全测试资料abcdef"

    assert len(password) >= MIN_PASSWORD_LENGTH
    PasswordPolicy().validate(password)


def test_password_policy_preserves_whitespace_semantics() -> None:
    """Whitespace remains valid password material and is not stripped."""

    password = "  abcdefgh  "

    assert len(password) == MIN_PASSWORD_LENGTH
    PasswordPolicy().validate(password)


@pytest.mark.parametrize(
    "password",
    [
        "abcdefghijkl",
        "ABCDEFGHIJKL",
        "123456789012",
        "!@#$%^&*()[]",
    ],
)
def test_password_policy_does_not_require_character_classes(password: str) -> None:
    """No arbitrary character-composition requirements are imposed."""

    assert len(password) == MIN_PASSWORD_LENGTH
    PasswordPolicy().validate(password)


def test_password_policy_does_not_mutate_candidate() -> None:
    """Validation does not normalize or otherwise transform the candidate."""

    password = "  AbCdEf12! "

    assert len(password) == MIN_PASSWORD_LENGTH

    original = password

    PasswordPolicy().validate(password)

    assert password == original


@pytest.mark.parametrize(
    "password",
    [
        "x" * (MIN_PASSWORD_LENGTH - 1),
        "x" * (MAX_PASSWORD_LENGTH + 1),
    ],
)
def test_password_policy_violation_does_not_disclose_candidate(password: str) -> None:
    """Policy failures never disclose plaintext password material."""

    with pytest.raises(PasswordPolicyViolation) as exception_info:
        PasswordPolicy().validate(password)

    assert password not in str(exception_info.value)
    assert password not in repr(exception_info.value)
