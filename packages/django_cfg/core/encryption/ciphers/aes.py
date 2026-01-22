"""
AES cipher implementations for Django-CFG encryption.

Provides AES-256-GCM authenticated encryption cipher.
"""

from __future__ import annotations

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .base import CipherBase, EncryptionResult
from .exceptions import AuthenticationError, DecryptionError, EncryptionError


class AES256GCMCipher(CipherBase):
    """
    AES-256-GCM authenticated encryption cipher.

    This is the recommended cipher for API encryption as it provides
    both confidentiality and integrity (authenticated encryption).

    Features:
        - 256-bit key (32 bytes)
        - 96-bit nonce/IV (12 bytes) - recommended for GCM
        - 128-bit authentication tag (16 bytes)
        - AEAD (Authenticated Encryption with Associated Data)

    Example:
        ```python
        cipher = AES256GCMCipher()
        key = secrets.token_bytes(32)  # 256-bit key

        # Encrypt
        result = cipher.encrypt(b"secret data", key)
        print(result.ciphertext, result.iv, result.auth_tag)

        # Decrypt
        plaintext = cipher.decrypt(
            result.ciphertext,
            key,
            result.iv,
            result.auth_tag
        )
        ```
    """

    @property
    def algorithm_name(self) -> str:
        return "AES-256-GCM"

    @property
    def key_size(self) -> int:
        return 32  # 256 bits

    @property
    def iv_size(self) -> int:
        return 12  # 96 bits (recommended for GCM)

    def encrypt(self, plaintext: bytes, key: bytes) -> EncryptionResult:
        """
        Encrypt data using AES-256-GCM.

        Args:
            plaintext: Data to encrypt
            key: 32-byte encryption key

        Returns:
            EncryptionResult with ciphertext, IV, and authentication tag

        Raises:
            EncryptionError: If encryption fails
            InvalidKeyLengthError: If key is not 32 bytes
        """
        self.validate_key(key)

        try:
            iv = self.generate_iv()
            aesgcm = AESGCM(key)

            # GCM mode appends auth tag to ciphertext
            ciphertext_with_tag = aesgcm.encrypt(iv, plaintext, None)

            # Split ciphertext and tag (tag is last 16 bytes)
            ciphertext = ciphertext_with_tag[:-self.auth_tag_size]
            auth_tag = ciphertext_with_tag[-self.auth_tag_size:]

            return EncryptionResult(
                ciphertext=ciphertext,
                iv=iv,
                auth_tag=auth_tag,
            )

        except Exception as e:
            raise EncryptionError(
                f"AES-256-GCM encryption failed: {e}",
                context={"plaintext_length": len(plaintext)},
            ) from e

    def decrypt(
        self,
        ciphertext: bytes,
        key: bytes,
        iv: bytes,
        auth_tag: bytes,
    ) -> bytes:
        """
        Decrypt data using AES-256-GCM.

        Args:
            ciphertext: Encrypted data
            key: 32-byte decryption key
            iv: 12-byte initialization vector
            auth_tag: 16-byte authentication tag

        Returns:
            Decrypted plaintext

        Raises:
            DecryptionError: If decryption fails
            AuthenticationError: If auth tag verification fails
            InvalidKeyLengthError: If key is not 32 bytes
            InvalidIVLengthError: If IV is not 12 bytes
        """
        self.validate_key(key)
        self.validate_iv(iv)

        try:
            aesgcm = AESGCM(key)

            # GCM expects ciphertext + tag concatenated
            ciphertext_with_tag = ciphertext + auth_tag

            return aesgcm.decrypt(iv, ciphertext_with_tag, None)

        except InvalidTag as e:
            # Authentication failed - data may have been tampered with
            raise AuthenticationError() from e

        except Exception as e:
            raise DecryptionError(
                f"AES-256-GCM decryption failed: {e}",
                context={"ciphertext_length": len(ciphertext)},
            ) from e


# Convenience function
def get_default_cipher() -> AES256GCMCipher:
    """Get the default cipher instance (AES-256-GCM)."""
    return AES256GCMCipher()
