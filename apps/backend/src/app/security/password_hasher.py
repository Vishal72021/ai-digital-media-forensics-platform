"""Password hashing and verification primitives."""

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from argon2.low_level import Type


class PasswordHasher:
    """Hash and verify passwords using the approved Argon2id algorithm."""

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

    def verify(self, password: str, encoded_hash: str) -> bool:
        """Verify plaintext password material against an encoded hash.

        Args:
            password: Plaintext password material.
            encoded_hash: Previously encoded password hash.

        Returns:
            True when the password matches the encoded hash; otherwise False.
        """
        try:
            return self._hasher.verify(encoded_hash, password)
        except (VerificationError, InvalidHashError):
            return False

    def needs_rehash(self, encoded_hash: str) -> bool:
        """Determine whether an encoded hash uses outdated parameters.

        Args:
            encoded_hash: Previously encoded password hash.

        Returns:
            True when the hash should be replaced using current parameters.
        """
        return self._hasher.check_needs_rehash(encoded_hash)
