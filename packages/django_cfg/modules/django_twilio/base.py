"""
Base service class for all Twilio operations.

Provides auto-configuration from DjangoConfig and common utilities
for all Twilio services including error handling and logging.
"""

import asyncio
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

# Django CFG imports
from django_cfg.modules.base import BaseCfgModule
from django_cfg.modules.django_twilio.exceptions import (
    TwilioConfigurationError,
)
from django_cfg.modules.django_twilio.models import TwilioConfig

# Third-party imports (optional)
from ._imports import (
    Client,
    SendGridAPIClient,
    TwilioException,
)

logger = logging.getLogger(__name__)


def is_async_context() -> bool:
    """Detect if running in async context."""
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


class BaseTwilioService(BaseCfgModule):
    """
    Base service class for all Twilio operations.

    Provides auto-configuration from DjangoConfig and common utilities
    for all Twilio services including error handling and logging.
    """

    def __init__(self):
        """Initialize with auto-discovered configuration."""
        super().__init__()
        self._config: Optional[TwilioConfig] = None
        self._twilio_client: Optional[Client] = None
        self._sendgrid_client: Optional[SendGridAPIClient] = None
        self._otp_storage: Dict[str, Dict[str, Any]] = {}  # In-memory storage for development

    def get_twilio_config(self) -> TwilioConfig:
        """
        Get Twilio configuration from DjangoConfig.

        Returns:
            TwilioConfig instance

        Raises:
            TwilioConfigurationError: If configuration is missing or invalid
        """
        if self._config is None:
            django_config = self.get_config()
            if not django_config:
                raise TwilioConfigurationError(
                    "DjangoConfig instance not found",
                    suggestions=["Ensure DjangoConfig is properly initialized"]
                )

            twilio_config = getattr(django_config, 'twilio', None)
            if not twilio_config:
                raise TwilioConfigurationError(
                    "Twilio configuration not found in DjangoConfig",
                    missing_fields=["twilio"],
                    suggestions=["Add TwilioConfig to your DjangoConfig class"]
                )

            self._config = twilio_config

        return self._config

    def get_twilio_client(self) -> Client:
        """
        Get initialized Twilio client.

        Returns:
            Twilio Client instance

        Raises:
            TwilioConfigurationError: If client cannot be initialized
        """
        if self._twilio_client is None:
            config = self.get_twilio_config()

            try:
                client_config = config.get_client_config()
                self._twilio_client = Client(
                    client_config["username"],
                    client_config["password"],
                    region=client_config.get("region")
                )

                # Test connection with a simple API call
                try:
                    self._twilio_client.api.v2010.accounts(config.account_sid).fetch()
                except TwilioException as e:
                    raise TwilioConfigurationError(
                        f"Failed to authenticate with Twilio: {e}",
                        error_code=getattr(e, 'code', None),
                        suggestions=[
                            "Verify TWILIO_ACCOUNT_SID is correct",
                            "Verify TWILIO_AUTH_TOKEN is correct",
                            "Check Twilio account status"
                        ]
                    ) from e

            except Exception as e:
                raise TwilioConfigurationError(
                    f"Failed to initialize Twilio client: {e}",
                    suggestions=["Check Twilio configuration parameters"]
                ) from e

        return self._twilio_client

    def get_sendgrid_client(self) -> Optional[SendGridAPIClient]:
        """
        Get initialized SendGrid client.

        Returns:
            SendGrid client instance or None if not configured

        Raises:
            TwilioConfigurationError: If client cannot be initialized
        """
        config = self.get_twilio_config()

        if not config.sendgrid:
            return None

        if self._sendgrid_client is None:
            try:
                sendgrid_config = config.get_sendgrid_config()
                if sendgrid_config:
                    self._sendgrid_client = SendGridAPIClient(
                        api_key=sendgrid_config["api_key"]
                    )

            except Exception as e:
                raise TwilioConfigurationError(
                    f"Failed to initialize SendGrid client: {e}",
                    suggestions=["Check SendGrid API key configuration"]
                ) from e

        return self._sendgrid_client

    def _generate_otp(self, length: int = 6) -> str:
        """Generate numeric OTP code."""
        return ''.join(random.choices(string.digits, k=length))

    def _store_otp(self, identifier: str, code: str, ttl_seconds: int = 600) -> None:
        """Store OTP code with expiration (in-memory for development)."""
        self._otp_storage[identifier] = {
            'code': code,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=ttl_seconds),
            'attempts': 0,
        }

    def _get_stored_otp(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Get stored OTP data."""
        return self._otp_storage.get(identifier)

    def _remove_otp(self, identifier: str) -> None:
        """Remove OTP from storage."""
        self._otp_storage.pop(identifier, None)

    def _mask_identifier(self, identifier: str) -> str:
        """Mask identifier for security in logs."""
        if "@" in identifier:  # Email
            parts = identifier.split("@")
            if len(parts) == 2:
                return f"{parts[0][:2]}***@{parts[1]}"
        else:  # Phone number
            return f"***{identifier[-4:]}" if len(identifier) > 4 else "***"
        return "***"


__all__ = [
    "is_async_context",
    "BaseTwilioService",
]
