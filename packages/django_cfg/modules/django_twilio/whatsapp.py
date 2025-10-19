"""
WhatsApp OTP service using Twilio Verify API.

Provides OTP delivery via WhatsApp with automatic SMS fallback.
Supports both sync and async operations.
"""

import logging
from typing import Tuple

from asgiref.sync import sync_to_async

from ._imports import Client, TwilioException
from .base import BaseTwilioService
from .exceptions import (
    TwilioConfigurationError,
    TwilioSendError,
)
from .models import TwilioVerifyConfig

logger = logging.getLogger(__name__)


class WhatsAppOTPService(BaseTwilioService):
    """
    WhatsApp OTP service using Twilio Verify API.

    Provides OTP delivery via WhatsApp with automatic SMS fallback.
    Supports both sync and async operations.
    """

    def send_otp(self, phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
        """
        Send OTP via WhatsApp with optional SMS fallback.

        Args:
            phone_number: Phone number in E.164 format (e.g., +1234567890)
            fallback_to_sms: Whether to fallback to SMS if WhatsApp fails

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            TwilioConfigurationError: If service is not configured
            TwilioSendError: If sending fails
        """
        config = self.get_twilio_config()

        if not config.verify:
            raise TwilioConfigurationError(
                "Twilio Verify service not configured",
                missing_fields=["verify"],
                suggestions=["Configure TwilioVerifyConfig in your Twilio settings"]
            )

        client = self.get_twilio_client()

        try:
            # Try WhatsApp first
            verification = client.verify.v2.services(
                config.verify.service_sid
            ).verifications.create(
                to=phone_number,
                channel='whatsapp'
            )

            if verification.status == 'pending':
                logger.info(f"WhatsApp OTP sent successfully to {self._mask_identifier(phone_number)}")
                return True, f"OTP sent via WhatsApp to {self._mask_identifier(phone_number)}"

            # If WhatsApp failed and fallback is enabled, try SMS
            if fallback_to_sms and verification.status != 'pending':
                logger.warning(f"WhatsApp failed for {self._mask_identifier(phone_number)}, trying SMS fallback")
                return self._send_sms_otp(phone_number, client, config.verify)

            raise TwilioSendError(
                f"WhatsApp OTP failed with status: {verification.status}",
                channel="whatsapp",
                recipient=phone_number,
                suggestions=["Check if recipient has WhatsApp Business account", "Try SMS fallback"]
            )

        except TwilioException as e:
            if fallback_to_sms:
                logger.warning(f"WhatsApp error for {self._mask_identifier(phone_number)}: {e}, trying SMS")
                return self._send_sms_otp(phone_number, client, config.verify)

            raise TwilioSendError(
                f"WhatsApp OTP failed: {e}",
                channel="whatsapp",
                recipient=phone_number,
                twilio_error_code=getattr(e, 'code', None),
                twilio_error_message=str(e)
            ) from e
        except Exception as e:
            raise TwilioSendError(
                f"Unexpected error sending WhatsApp OTP: {e}",
                channel="whatsapp",
                recipient=phone_number
            ) from e

    async def asend_otp(self, phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
        """Async version of send_otp."""
        return await sync_to_async(self.send_otp)(phone_number, fallback_to_sms)

    def _send_sms_otp(self, phone_number: str, client: Client, verify_config: TwilioVerifyConfig) -> Tuple[bool, str]:
        """Internal SMS fallback method."""
        try:
            verification = client.verify.v2.services(
                verify_config.service_sid
            ).verifications.create(
                to=phone_number,
                channel='sms'
            )

            if verification.status == 'pending':
                logger.info(f"SMS fallback OTP sent to {self._mask_identifier(phone_number)}")
                return True, f"OTP sent via SMS to {self._mask_identifier(phone_number)} (WhatsApp fallback)"

            raise TwilioSendError(
                f"SMS fallback failed with status: {verification.status}",
                channel="sms",
                recipient=phone_number
            )

        except TwilioException as e:
            raise TwilioSendError(
                f"SMS fallback failed: {e}",
                channel="sms",
                recipient=phone_number,
                twilio_error_code=getattr(e, 'code', None),
                twilio_error_message=str(e)
            ) from e


__all__ = [
    "WhatsAppOTPService",
]
