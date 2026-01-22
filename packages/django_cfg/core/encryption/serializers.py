"""
DRF serializer mixins for Django-CFG encryption.

Provides mixins and fields for encrypting serializer output.
"""

from __future__ import annotations

import base64
import json
import logging
from typing import Any, ClassVar

from rest_framework import serializers

from .ciphers import AES256GCMCipher, EncryptionError
from .keys import get_key_manager

logger = logging.getLogger(__name__)


def encode_base64(data: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.b64encode(data).decode("ascii")


def decode_base64(data: str) -> bytes:
    """Decode base64 string to bytes."""
    return base64.b64decode(data.encode("ascii"))


class EncryptableSerializerMixin:
    """
    Mixin for serializers that support field-level encryption.

    Add this mixin to any DRF serializer to enable optional encryption
    of specified fields. Encryption is triggered by request context.

    Attributes:
        encrypted_fields: List of field names to encrypt
        encryption_enabled: Whether encryption is enabled for this serializer

    Example:
        ```python
        class ProductSerializer(EncryptableSerializerMixin, serializers.ModelSerializer):
            encrypted_fields = ['price', 'cost', 'margin']

            class Meta:
                model = Product
                fields = ['id', 'name', 'price', 'cost', 'margin', 'category']

        # Usage in view
        class ProductViewSet(viewsets.ModelViewSet):
            serializer_class = ProductSerializer

        # Request with ?encrypt=true returns:
        # {
        #     "id": 1,
        #     "name": "Widget",
        #     "price": {
        #         "encrypted": true,
        #         "algorithm": "AES-256-GCM",
        #         "iv": "base64...",
        #         "data": "base64...",
        #         "auth_tag": "base64..."
        #     },
        #     "category": "Electronics"
        # }
        ```
    """

    encrypted_fields: ClassVar[list[str]] = []
    encryption_enabled: ClassVar[bool] = True

    def to_representation(self, instance: Any) -> dict[str, Any]:
        """
        Override to encrypt specified fields in the output.

        Args:
            instance: Model instance being serialized

        Returns:
            Serialized data with encrypted fields
        """
        # Get base representation
        result = super().to_representation(instance)  # type: ignore

        # Check if encryption should be applied
        if not self._should_encrypt():
            return result

        # Encrypt specified fields
        for field_name in self.encrypted_fields:
            if field_name in result and result[field_name] is not None:
                try:
                    result[field_name] = self._encrypt_field_value(
                        field_name, result[field_name]
                    )
                except EncryptionError as e:
                    logger.error(f"Failed to encrypt field {field_name}: {e}")
                    # Keep original value on error (configurable behavior)
                    pass

        return result

    def _should_encrypt(self) -> bool:
        """
        Check if encryption is enabled for this request.

        Returns:
            True if encryption should be applied
        """
        if not self.encryption_enabled:
            return False

        if not self.encrypted_fields:
            return False

        # Check request context
        request = self.context.get("request")  # type: ignore
        if not request:
            return False

        # Check for encryption flag set by middleware
        return getattr(request, "encryption_enabled", False)

    def _encrypt_field_value(self, field_name: str, value: Any) -> dict[str, Any]:
        """
        Encrypt a single field value.

        Args:
            field_name: Name of the field being encrypted
            value: Value to encrypt

        Returns:
            Encrypted field envelope
        """
        cipher = AES256GCMCipher()
        key_manager = get_key_manager()

        # Get key for current request
        request = self.context.get("request")  # type: ignore
        if request:
            key = key_manager.get_key_for_request(request)
        else:
            key = key_manager.get_encryption_key()

        # Serialize value to JSON bytes
        plaintext = json.dumps(value, ensure_ascii=False).encode("utf-8")

        # Encrypt
        result = cipher.encrypt(plaintext, key)

        return {
            "encrypted": True,
            "field": field_name,
            "algorithm": cipher.algorithm_name,
            "iv": encode_base64(result.iv),
            "data": encode_base64(result.ciphertext),
            "auth_tag": encode_base64(result.auth_tag),
        }


class EncryptedFieldMixin:
    """
    Mixin for individual serializer fields that support encryption.

    Add this mixin to any serializer field to enable encryption
    for that specific field.

    Example:
        ```python
        class EncryptedCharField(EncryptedFieldMixin, serializers.CharField):
            pass

        class ProductSerializer(serializers.ModelSerializer):
            price = EncryptedCharField(encrypted=True)
        ```
    """

    def __init__(self, *args: Any, encrypted: bool = False, **kwargs: Any):
        self.encrypted = encrypted
        super().__init__(*args, **kwargs)

    def to_representation(self, value: Any) -> Any:
        """
        Optionally encrypt the output value.

        Args:
            value: Value to represent

        Returns:
            Original or encrypted value
        """
        result = super().to_representation(value)  # type: ignore

        if self.encrypted and self._should_encrypt():
            return self._encrypt_value(result)

        return result

    def _should_encrypt(self) -> bool:
        """Check if encryption is enabled for this request."""
        # Access parent serializer context
        if hasattr(self, "context"):
            request = self.context.get("request")
            if request:
                return getattr(request, "encryption_enabled", False)
        return False

    def _encrypt_value(self, value: Any) -> dict[str, Any]:
        """Encrypt a value."""
        cipher = AES256GCMCipher()
        key_manager = get_key_manager()

        request = self.context.get("request") if hasattr(self, "context") else None
        if request:
            key = key_manager.get_key_for_request(request)
        else:
            key = key_manager.get_encryption_key()

        plaintext = json.dumps(value, ensure_ascii=False).encode("utf-8")
        result = cipher.encrypt(plaintext, key)

        return {
            "encrypted": True,
            "algorithm": cipher.algorithm_name,
            "iv": encode_base64(result.iv),
            "data": encode_base64(result.ciphertext),
            "auth_tag": encode_base64(result.auth_tag),
        }


# Pre-built encrypted field types
class EncryptedCharField(EncryptedFieldMixin, serializers.CharField):
    """CharField with optional encryption support."""

    pass


class EncryptedIntegerField(EncryptedFieldMixin, serializers.IntegerField):
    """IntegerField with optional encryption support."""

    pass


class EncryptedFloatField(EncryptedFieldMixin, serializers.FloatField):
    """FloatField with optional encryption support."""

    pass


class EncryptedDecimalField(EncryptedFieldMixin, serializers.DecimalField):
    """DecimalField with optional encryption support."""

    pass


class EncryptedJSONField(EncryptedFieldMixin, serializers.JSONField):
    """JSONField with optional encryption support."""

    pass
