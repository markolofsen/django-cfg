"""
Base cipher interface for Django-CFG encryption.

Provides abstract base class for implementing encryption ciphers.
"""

from __future__ import annotations

import secrets
from abc import ABC, abstractmethod
from typing import NamedTuple


class EncryptionResult(NamedTuple):
    """Result of encryption operation."""

    ciphertext: bytes
    iv: bytes
    auth_tag: bytes


class CipherBase(ABC):
    """
    Abstract base class for encryption ciphers.

    All cipher implementations must inherit from this class and implement
    the encrypt() and decrypt() methods.

    Example:
        ```python
        class MyCipher(CipherBase):
            @property
            def algorithm_name(self) -> str:
                return "MY-CIPHER"

            @property
            def key_size(self) -> int:
                return 32  # 256 bits

            @property
            def iv_size(self) -> int:
                return 12

            def encrypt(self, plaintext: bytes, key: bytes) -> EncryptionResult:
                # Implementation
                pass

            def decrypt(self, ciphertext: bytes, key: bytes, iv: bytes, auth_tag: bytes) -> bytes:
                # Implementation
                pass
        ```
    """

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Return the algorithm identifier (e.g., 'AES-256-GCM')."""
        pass

    @property
    @abstractmethod
    def key_size(self) -> int:
        """Return required key size in bytes."""
        pass

    @property
    @abstractmethod
    def iv_size(self) -> int:
        """Return IV/nonce size in bytes."""
        pass

    @property
    def auth_tag_size(self) -> int:
        """Return authentication tag size in bytes. Default: 16 (128 bits)."""
        return 16

    @abstractmethod
    def encrypt(self, plaintext: bytes, key: bytes) -> EncryptionResult:
        """
        Encrypt plaintext with the given key.

        Args:
            plaintext: Data to encrypt
            key: Encryption key (must match key_size)

        Returns:
            EncryptionResult containing ciphertext, IV, and auth tag

        Raises:
            EncryptionError: If encryption fails
            InvalidKeyLengthError: If key length is incorrect
        """
        pass

    @abstractmethod
    def decrypt(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
        auth_tag: bytes,
    ) -> bytes:
        """
        Decrypt ciphertext with the given key.

        Args:
            ciphertext: Encrypted data
            key: Decryption key (must match key_size)
            iv: Initialization vector used during encryption
            auth_tag: Authentication tag for verification

        Returns:
            Decrypted plaintext

        Raises:
            DecryptionError: If decryption fails
            AuthenticationError: If auth tag verification fails
            InvalidKeyLengthError: If key length is incorrect
            InvalidIVLengthError: If IV length is incorrect
        """
        pass

    def generate_iv(self) -> bytes:
        """
        Generate a cryptographically secure random IV/nonce.

        Returns:
            Random bytes of length iv_size
        """
        return secrets.token_bytes(self.iv_size)

    def validate_key(self, key: bytes) -> None:
        """
        Validate that key has correct length.

        Args:
            key: Key to validate

        Raises:
            InvalidKeyLengthError: If key length is incorrect
        """
        from .exceptions import InvalidKeyLengthError

        if len(key) != self.key_size:
            raise InvalidKeyLengthError(expected=self.key_size, actual=len(key))

    def validate_iv(self, iv: bytes) -> None:
        """
        Validate that IV has correct length.

        Args:
            iv: IV to validate

        Raises:
            InvalidIVLengthError: If IV length is incorrect
        """
        from .exceptions import InvalidIVLengthError

        if len(iv) != self.iv_size:
            raise InvalidIVLengthError(expected=self.iv_size, actual=len(iv))
