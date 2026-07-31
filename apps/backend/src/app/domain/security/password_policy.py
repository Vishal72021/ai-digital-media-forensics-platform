"""Canonical password acceptance policy."""

from app.domain.exceptions.security import PasswordPolicyViolation

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


class PasswordPolicy:
    """Validate candidate passwords against the canonical acceptance policy."""

    def validate(self, password: str) -> None:
        """Validate a candidate password.

        Args:
            password: Candidate plaintext password.

        Raises:
            PasswordPolicyViolation: If the candidate violates the password policy.
        """
        password_length = len(password)

        if password_length < MIN_PASSWORD_LENGTH:
            raise PasswordPolicyViolation(
                f"Password must contain at least {MIN_PASSWORD_LENGTH} characters."
            )

        if password_length > MAX_PASSWORD_LENGTH:
            raise PasswordPolicyViolation(
                f"Password must contain at most {MAX_PASSWORD_LENGTH} characters."
            )
