"""
DRF renderers for encrypted responses.

Provides renderers that encrypt entire JSON responses.
"""

from __future__ import annotations

import base64
import json
import logging
from typing import TYPE_CHECKING, Any

from rest_framework.renderers import JSONRenderer

from .ciphers import AES256GCMCipher
from .keys import get_key_manager

if TYPE_CHECKING:
    from rest_framework.request import Request

logger = logging.getLogger(__name__)


class EncryptedJSONRenderer(JSONRenderer):
    """
    JSON renderer that encrypts the entire response.

    Use this renderer for full response encryption (not field-level).
    Encryption is triggered by request context (set by middleware).

    Response format:
        ```json
        {
            "encrypted": true,
            "algorithm": "AES-256-GCM",
            "salt": "base64_encoded_salt",
            "iv": "base64_encoded_iv",
            "data": "base64_encoded_ciphertext",
            "auth_tag": "base64_encoded_auth_tag"
        }
        ```

    Example:
        ```python
        # In settings
        REST_FRAMEWORK = {
            'DEFAULT_RENDERER_CLASSES': [
                'django_cfg.core.encryption.renderers.EncryptedJSONRenderer',
                'rest_framework.renderers.JSONRenderer',
            ]
        }

        # Or per-view
        class MyViewSet(viewsets.ModelViewSet):
            renderer_classes = [EncryptedJSONRenderer]
        ```
    """

    media_type = "application/json+encrypted"
    format = "json+encrypted"

    def render(
        self,
        data: Any,
        accepted_media_type: str | None = None,
        renderer_context: dict[str, Any] | None = None,
    ) -> bytes:
        """
        Render data to optionally encrypted JSON.

        Args:
            data: Data to render
            accepted_media_type: Accepted media type
            renderer_context: Renderer context with request

        Returns:
            Rendered JSON bytes (encrypted or plain)
        """
        request = renderer_context.get("request") if renderer_context else None

        if not self._should_encrypt(request, renderer_context):
            # Fall back to regular JSON rendering
            return super().render(data, accepted_media_type, renderer_context)

        # First render to JSON
        json_bytes = super().render(data, accepted_media_type, renderer_context)

        # Then encrypt
        try:
            return self._encrypt_response(json_bytes, request)
        except Exception as e:
            logger.error(f"Failed to encrypt response: {e}")
            # Return unencrypted on error
            return json_bytes

    def _should_encrypt(
        self,
        request: "Request | None",
        renderer_context: dict[str, Any] | None,
    ) -> bool:
        """
        Determine if response should be encrypted.

        Args:
            request: DRF Request
            renderer_context: Renderer context

        Returns:
            True if encryption should be applied
        """
        if not request:
            return False

        # Check request attribute (set by middleware)
        if getattr(request, "encryption_enabled", False):
            return True

        # Check view attribute
        view = renderer_context.get("view") if renderer_context else None
        if view and getattr(view, "encrypt_response", False):
            return True

        return False

    def _encrypt_response(
        self,
        json_bytes: bytes,
        request: "Request | None",
    ) -> bytes:
        """
        Encrypt the JSON response.

        Args:
            json_bytes: JSON data to encrypt
            request: DRF Request for key derivation

        Returns:
            Encrypted response as JSON bytes
        """
        cipher = AES256GCMCipher()
        key_manager = get_key_manager()

        # Get key (optionally user-specific)
        if request:
            key = key_manager.get_key_for_request(request._request)
        else:
            key = key_manager.get_encryption_key()

        # Generate client salt for key derivation hint
        client_salt = key_manager.generate_client_salt()

        # Encrypt
        result = cipher.encrypt(json_bytes, key)

        # Build encrypted response envelope
        encrypted_response = {
            "encrypted": True,
            "algorithm": cipher.algorithm_name,
            "salt": base64.b64encode(client_salt).decode("ascii"),
            "iv": base64.b64encode(result.iv).decode("ascii"),
            "data": base64.b64encode(result.ciphertext).decode("ascii"),
            "auth_tag": base64.b64encode(result.auth_tag).decode("ascii"),
        }

        return json.dumps(encrypted_response).encode("utf-8")


class OptionalEncryptedJSONRenderer(EncryptedJSONRenderer):
    """
    JSON renderer with optional encryption using standard media type.

    Same as EncryptedJSONRenderer but uses 'application/json' as media type.
    Use this when encryption should be transparent to the Accept header.

    Example:
        ```python
        REST_FRAMEWORK = {
            'DEFAULT_RENDERER_CLASSES': [
                'django_cfg.core.encryption.renderers.OptionalEncryptedJSONRenderer',
            ]
        }

        # Client requests:
        GET /api/products/
        Accept: application/json

        # With ?encrypt=true, response is encrypted
        # Without, response is plain JSON
        ```
    """

    media_type = "application/json"
    format = "json"
