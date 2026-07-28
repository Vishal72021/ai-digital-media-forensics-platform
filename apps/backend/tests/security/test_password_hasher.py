"""Verification for the password hashing boundary."""

from argon2 import PasswordHasher as Argon2PasswordHasher

from app.security.password_hasher import PasswordHasher


def test_password_hasher_returns_encoded_hash() -> None:
    """Hashing returns a string distinct from the plaintext password."""

    password = "correct horse battery staple"

    encoded_hash = PasswordHasher().hash(password)

    assert isinstance(encoded_hash, str)
    assert encoded_hash != password


def test_password_hasher_uses_argon2id() -> None:
    """Encoded password hashes use the approved Argon2id algorithm."""

    encoded_hash = PasswordHasher().hash("correct horse battery staple")

    assert encoded_hash.startswith("$argon2id$")


def test_password_hasher_generates_unique_salted_hashes() -> None:
    """Repeated hashing of the same password produces distinct hashes."""

    password = "correct horse battery staple"
    hasher = PasswordHasher()

    first_hash = hasher.hash(password)
    second_hash = hasher.hash(password)

    assert first_hash != second_hash


def test_password_hasher_accepts_unicode_password_material() -> None:
    """Unicode password material can be hashed without normalization."""

    password = "密碼安全測試資料abcdef"

    encoded_hash = PasswordHasher().hash(password)

    assert encoded_hash.startswith("$argon2id$")


def test_password_hasher_preserves_whitespace_as_password_material() -> None:
    """Leading and trailing whitespace remains part of password material."""

    password = "  password material  "

    encoded_hash = PasswordHasher().hash(password)

    Argon2PasswordHasher().verify(encoded_hash, password)


def test_password_hasher_does_not_enforce_password_policy() -> None:
    """Password acceptance policy remains outside the hashing boundary."""

    encoded_hash = PasswordHasher().hash("")

    assert encoded_hash.startswith("$argon2id$")


def test_password_hasher_does_not_disclose_plaintext() -> None:
    """The encoded representation does not contain plaintext password material."""

    password = "sentinel-plaintext-secret"

    encoded_hash = PasswordHasher().hash(password)

    assert password not in encoded_hash
