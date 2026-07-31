"""Password hashing and verification primitives."""

from argon2 import PasswordHasher as Argon2PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from argon2.low_level import Type

_DUMMY_PASSWORD = "sentinel-ai-internal-dummy-credential"


class PasswordHasher:
    """Hash and verify passwords using the approved Argon2id algorithm."""

    def __init__(
        self,
        *,
        time_cost: int = 3,
        memory_cost: int = 65536,
        parallelism: int = 4,
        hash_len: int = 32,
        salt_len: int = 16,
    ) -> None:
        """Initialize the Argon2id password hasher."""
        self._hasher = Argon2PasswordHasher(
            time_cost=time_cost,
            memory_cost=memory_cost,
            parallelism=parallelism,
            hash_len=hash_len,
            salt_len=salt_len,
            type=Type.ID,
        )
        self._dummy_password_hash = self._hasher.hash(_DUMMY_PASSWORD)

    def hash(self, password: str) -> str:
        """Hash a plaintext password.

        Args:
            password: Plaintext password material.

        Returns:
            Argon2id encoded password hash.
        """
        return self._hasher.hash(password)

    def verify_dummy(self, password: str) -> None:
        """Perform password verification work against a non-user credential.

        Args:
            password: Supplied plaintext password material.
        """
        self.verify(password, self._dummy_password_hash)

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
