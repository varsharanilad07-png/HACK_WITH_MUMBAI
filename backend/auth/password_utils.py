"""Password hashing and verification using argon2."""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

_pwd_hasher = PasswordHasher()

MAX_PASSWORD_LENGTH = 128  # argon2 limit is much higher


def hash_password(plain: str) -> str:
    """Return argon2 hash of a plain-text password."""
    if len(plain) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Password cannot exceed {MAX_PASSWORD_LENGTH} characters")
    return _pwd_hasher.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored hash."""
    if len(plain) > MAX_PASSWORD_LENGTH:
        return False
    try:
        _pwd_hasher.verify(hashed, plain)
        return True
    except (VerifyMismatchError, InvalidHashError):
        return False
