"""
Cipher implementations for Django-CFG encryption.

Available ciphers:
    - AES256GCMCipher: AES-256 in GCM mode (recommended)
"""

from .aes import AES256GCMCipher, get_default_cipher
from .base import CipherBase, EncryptionResult
from .exceptions import (
    AuthenticationError,
    DecryptionError,
    EncryptionError,
    EncryptionException,
    InvalidIVLengthError,
    InvalidKeyLengthError,
    KeyError,
)

__all__ = [
    # Base
    "CipherBase",
    "EncryptionResult",
    # Implementations
    "AES256GCMCipher",
    "get_default_cipher",
    # Exceptions
    "EncryptionException",
    "EncryptionError",
    "DecryptionError",
    "KeyError",
    "InvalidKeyLengthError",
    "InvalidIVLengthError",
    "AuthenticationError",
]
