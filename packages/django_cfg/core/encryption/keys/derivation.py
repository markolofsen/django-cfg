"""
Key derivation functions for Django-CFG encryption.

Provides PBKDF2-based key derivation for generating encryption keys.
"""

from __future__ import annotations

import hashlib
import secrets
from typing import Literal

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def derive_key_pbkdf2(
    password: str | bytes,
    salt: bytes,
    iterations: int = 100_000,
    key_length: int = 32,
    hash_algorithm: Literal["SHA-256", "SHA-512"] = "SHA-256",
) -> bytes:
    """
    Derive an encryption key using PBKDF2.

    Args:
        password: Password or secret to derive key from
        salt: Random salt (should be at least 16 bytes)
        iterations: Number of iterations (default: 100,000)
        key_length: Desired key length in bytes (default: 32 for AES-256)
        hash_algorithm: Hash algorithm to use (SHA-256 or SHA-512)

    Returns:
        Derived key of specified length

    Example:
        ```python
        salt = generate_salt()
        key = derive_key_pbkdf2("my_secret", salt)
        # key is 32 bytes suitable for AES-256
        ```
    """
    if isinstance(password, str):
        password = password.encode("utf-8")

    # Select hash algorithm
    if hash_algorithm == "SHA-512":
        algorithm = hashes.SHA512()
    else:
        algorithm = hashes.SHA256()

    kdf = PBKDF2HMAC(
        algorithm=algorithm,
        length=key_length,
        salt=salt,
        iterations=iterations,
    )

    return kdf.derive(password)


def generate_salt(length: int = 16) -> bytes:
    """
    Generate a cryptographically secure random salt.

    Args:
        length: Salt length in bytes (default: 16)

    Returns:
        Random salt bytes
    """
    return secrets.token_bytes(length)


def derive_key_from_components(
    *components: str | bytes,
    salt: bytes | None = None,
    iterations: int = 100_000,
    key_length: int = 32,
) -> bytes:
    """
    Derive a key from multiple components.

    Combines multiple strings/bytes into a single key using PBKDF2.
    Useful for deriving user-specific keys from (SECRET_KEY, user_id, etc.)

    Args:
        *components: Variable number of strings or bytes to combine
        salt: Optional salt (generated if not provided)
        iterations: PBKDF2 iterations
        key_length: Desired key length

    Returns:
        Derived key

    Example:
        ```python
        key = derive_key_from_components(
            settings.SECRET_KEY,
            str(user.id),
            "encryption",
            salt=user_salt,
        )
        ```
    """
    # Combine components with a separator
    combined_parts = []
    for component in components:
        if isinstance(component, str):
            combined_parts.append(component.encode("utf-8"))
        else:
            combined_parts.append(component)

    combined = b":".join(combined_parts)

    # Use deterministic salt from combined if not provided
    if salt is None:
        salt = hashlib.sha256(combined).digest()[:16]

    return derive_key_pbkdf2(
        password=combined,
        salt=salt,
        iterations=iterations,
        key_length=key_length,
    )
