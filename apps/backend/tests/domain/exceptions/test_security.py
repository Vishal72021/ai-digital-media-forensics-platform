"""Verification for security domain exceptions."""

from app.domain.exceptions import (
    AuthenticationException,
    BusinessRuleException,
    InvalidCredentialsException,
    PasswordPolicyViolation,
    ValidationException,
)


def test_authentication_exception_inherits_business_rule_exception() -> None:
    """Authentication exceptions remain business rule failures."""

    exception = AuthenticationException("authentication failed")

    assert isinstance(exception, BusinessRuleException)


def test_invalid_credentials_exception_inherits_authentication_exception() -> None:
    """Invalid credentials are authentication failures."""

    exception = InvalidCredentialsException()

    assert isinstance(exception, AuthenticationException)


def test_invalid_credentials_exception_uses_canonical_message() -> None:
    """Invalid credentials expose the approved domain message."""

    exception = InvalidCredentialsException()

    assert str(exception) == "The supplied credentials are invalid."


def test_password_policy_violation_inherits_validation_exception() -> None:
    """Password policy violations remain validation failures."""

    exception = PasswordPolicyViolation("Password is too short.")

    assert isinstance(exception, ValidationException)


def test_password_policy_violation_preserves_message() -> None:
    """Password policy violations preserve the supplied message."""

    exception = PasswordPolicyViolation("Password is too short.")

    assert str(exception) == "Password is too short."
