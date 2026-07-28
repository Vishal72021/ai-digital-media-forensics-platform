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


def test_password_hasher_verifies_matching_password() -> None:
    """Verification succeeds for the password used to create the hash."""

    password = "correct horse battery staple"
    hasher = PasswordHasher()
    encoded_hash = hasher.hash(password)

    assert hasher.verify(password, encoded_hash) is True


def test_password_hasher_rejects_non_matching_password() -> None:
    """Verification fails when plaintext password material does not match."""

    hasher = PasswordHasher()
    encoded_hash = hasher.hash("correct horse battery staple")

    assert hasher.verify("incorrect horse battery staple", encoded_hash) is False


def test_password_hasher_rejects_malformed_encoded_hash() -> None:
    """Malformed stored hash material is rejected without leaking Argon2 errors."""

    hasher = PasswordHasher()

    assert hasher.verify("correct horse battery staple", "not-an-argon2-hash") is False


def test_password_verification_preserves_whitespace_semantics() -> None:
    """Verification does not trim or normalize password material."""

    password = "  password material  "
    hasher = PasswordHasher()
    encoded_hash = hasher.hash(password)

    assert hasher.verify(password, encoded_hash) is True
    assert hasher.verify(password.strip(), encoded_hash) is False


def test_password_verification_accepts_unicode_password_material() -> None:
    """Unicode password material is verified without normalization."""

    password = "密碼安全測試資料abcdef"
    hasher = PasswordHasher()
    encoded_hash = hasher.hash(password)

    assert hasher.verify(password, encoded_hash) is True


def test_current_password_hash_does_not_need_rehash() -> None:
    """Hashes produced by the current configuration remain current."""

    hasher = PasswordHasher()
    encoded_hash = hasher.hash("correct horse battery staple")

    assert hasher.needs_rehash(encoded_hash) is False


def test_outdated_password_hash_needs_rehash() -> None:
    """Hashes using different Argon2 parameters are identified for replacement."""

    outdated_hasher = Argon2PasswordHasher(time_cost=1)
    encoded_hash = outdated_hasher.hash("correct horse battery staple")

    assert PasswordHasher().needs_rehash(encoded_hash) is True


def test_verification_does_not_replace_encoded_hash() -> None:
    """Verification remains read-only and does not implicitly rotate hashes."""

    password = "correct horse battery staple"
    hasher = PasswordHasher()
    encoded_hash = hasher.hash(password)

    original_hash = encoded_hash

    assert hasher.verify(password, encoded_hash) is True
    assert encoded_hash == original_hash
