"""Password hashing primitives."""

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.low_level import Type


class PasswordHasher:
    """Hash passwords using the approved Argon2id algorithm."""

    def __init__(self) -> None:
        """Initialize the Argon2id password hasher."""
        self._hasher = Argon2PasswordHasher(type=Type.ID)

    def hash(self, password: str) -> str:
        """Hash a plaintext password.

        Args:
            password: Plaintext password material.

        Returns:
            Argon2id encoded password hash.
        """
        return self._hasher.hash(password)
