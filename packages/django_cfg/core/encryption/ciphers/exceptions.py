"""
Encryption exceptions for Django-CFG.

Custom exceptions for encryption and decryption operations.
"""

from __future__ import annotations


class EncryptionException(Exception):
    """Base exception for all encryption-related errors."""

    def __init__(self, message: str, context: dict | None = None):
        self.message = message
        self.context = context or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.context:
            return f"{self.message} | Context: {self.context}"
        return self.message


class EncryptionError(EncryptionException):
    """Raised when encryption fails."""

    pass


class DecryptionError(EncryptionException):
    """Raised when decryption fails."""

    pass


class KeyError(EncryptionException):
    """Raised when key operations fail."""

    pass


class InvalidKeyLengthError(KeyError):
    """Raised when key length is invalid."""

    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"Invalid key length: expected {expected} bytes, got {actual} bytes",
            context={"expected": expected, "actual": actual},
        )


class InvalidIVLengthError(EncryptionException):
    """Raised when IV/nonce length is invalid."""

    def __init__(self, expected: int, actual: int):
        super().__init__(
            f"Invalid IV length: expected {expected} bytes, got {actual} bytes",
            context={"expected": expected, "actual": actual},
        )


class AuthenticationError(DecryptionError):
    """Raised when authentication tag verification fails."""

    def __init__(self):
        super().__init__(
            "Authentication failed: data may have been tampered with",
            context={"reason": "auth_tag_mismatch"},
        )
