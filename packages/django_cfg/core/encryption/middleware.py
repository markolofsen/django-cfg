"""
Django middleware for encryption detection.

Detects encryption requests and sets flags for serializers/renderers.
"""

from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

logger = logging.getLogger(__name__)


class EncryptionMiddleware:
    """
    Middleware to detect encryption requests and set flags.

    Checks for encryption triggers:
        1. Query parameter: ?encrypt=true
        2. Request header: X-Encrypt-Response: true
        3. Accept header: application/json+encrypted
        4. Endpoint override patterns (from settings)

    Sets `request.encryption_enabled = True` when encryption is requested.

    Configuration via DjangoConfig:
        ```python
        config = DjangoConfig(
            encryption=EncryptionConfig(
                enabled=True,
                response_encryption=ResponseEncryptionConfig(
                    query_param="encrypt",
                    header_name="X-Encrypt-Response",
                ),
                endpoint_overrides={
                    r"^/api/prices/": "field",  # Always encrypt prices
                    r"^/api/admin/": "none",    # Never encrypt admin
                },
            ),
        )
        ```

    Example:
        ```python
        # In Django settings
        MIDDLEWARE = [
            ...
            'django_cfg.core.encryption.middleware.EncryptionMiddleware',
            ...
        ]

        # Request with encryption
        GET /api/products/?encrypt=true
        # or
        GET /api/products/
        X-Encrypt-Response: true
        ```
    """

    def __init__(self, get_response: Callable[["HttpRequest"], "HttpResponse"]):
        self.get_response = get_response
        self._config_loaded = False
        self._enabled = False
        self._query_param = "encrypt"
        self._header_name = "X-Encrypt-Response"
        self._endpoint_overrides: dict = {}

    def _load_config(self) -> None:
        """Load encryption configuration from DjangoConfig."""
        if self._config_loaded:
            return

        try:
            from django_cfg.core.state import get_current_config

            config = get_current_config()
            if config and hasattr(config, "encryption") and config.encryption:
                enc_config = config.encryption
                self._enabled = enc_config.enabled
                self._query_param = enc_config.response_encryption.query_param
                self._header_name = enc_config.response_encryption.header_name
                self._endpoint_overrides = enc_config.endpoint_overrides
        except Exception as e:
            logger.debug(f"Could not load encryption config: {e}")
            # Fall back to defaults, allow encryption to be triggered manually
            self._enabled = True

        self._config_loaded = True

    def __call__(self, request: "HttpRequest") -> "HttpResponse":
        """
        Process the request and set encryption flag.

        Args:
            request: Django HttpRequest

        Returns:
            HttpResponse from the view
        """
        self._load_config()

        # Set encryption flag on request
        request.encryption_enabled = self._should_encrypt(request)  # type: ignore

        if request.encryption_enabled:  # type: ignore
            logger.debug(f"Encryption enabled for request: {request.path}")

        response = self.get_response(request)
        return response

    def _should_encrypt(self, request: "HttpRequest") -> bool:
        """
        Determine if response should be encrypted for this request.

        Args:
            request: Django HttpRequest

        Returns:
            True if encryption should be applied
        """
        # Check if encryption feature is enabled
        if not self._enabled:
            return False

        # Check for explicit opt-out
        opt_out = request.GET.get(self._query_param, "").lower()
        if opt_out == "false":
            return False

        # Check query parameter
        query_value = request.GET.get(self._query_param, "").lower()
        if query_value == "true":
            return True

        # Check request header
        header_value = request.headers.get(self._header_name, "").lower()
        if header_value == "true":
            return True

        # Check Accept header for encrypted content type
        accept = request.headers.get("Accept", "")
        if "application/json+encrypted" in accept:
            return True

        # Check endpoint overrides
        path = request.path
        for pattern, level in self._endpoint_overrides.items():
            try:
                if re.match(pattern, path):
                    # "none" means no encryption for this endpoint
                    if level == "none":
                        return False
                    # Any other level means encrypt
                    return True
            except re.error:
                logger.warning(f"Invalid regex pattern in endpoint_overrides: {pattern}")

        return False


def encryption_enabled(request: "HttpRequest") -> bool:
    """
    Check if encryption is enabled for the current request.

    Utility function for use in views.

    Args:
        request: Django HttpRequest

    Returns:
        True if encryption is enabled

    Example:
        ```python
        def my_view(request):
            if encryption_enabled(request):
                # Handle encrypted response
                pass
        ```
    """
    return getattr(request, "encryption_enabled", False)
