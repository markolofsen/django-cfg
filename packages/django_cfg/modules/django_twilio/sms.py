"""
SMS OTP service using Twilio Verify API.

Provides reliable SMS OTP delivery with comprehensive
error handling and international support.
"""

import logging
from typing import Tuple

from asgiref.sync import sync_to_async

from .base import BaseTwilioService
from .exceptions import (
    TwilioConfigurationError,
    TwilioSendError,
)

logger = logging.getLogger(__name__)


class SMSOTPService(BaseTwilioService):
    """
    SMS OTP service using Twilio Verify API.

    Provides reliable SMS OTP delivery with comprehensive
    error handling and international support.
    """

    def send_otp(self, phone_number: str) -> Tuple[bool, str]:
        """
        Send OTP via SMS.

        Args:
            phone_number: Phone number in E.164 format

        Returns:
            Tuple[bool, str]: (success, message)

        Raises:
            TwilioConfigurationError: If Verify service not configured
            TwilioSendError: If SMS sending fails
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
            verification = client.verify.v2.services(
                config.verify.service_sid
            ).verifications.create(
                to=phone_number,
                channel='sms'
            )

            if verification.status == 'pending':
                logger.info(f"SMS OTP sent successfully to {self._mask_identifier(phone_number)}")
                return True, f"OTP sent via SMS to {self._mask_identifier(phone_number)}"
            else:
                raise TwilioSendError(
                    f"SMS OTP failed with status: {verification.status}",
                    channel="sms",
                    recipient=phone_number
                )

        except TwilioException as e:
            raise TwilioSendError(
                f"SMS OTP failed: {e}",
                channel="sms",
                recipient=phone_number,
                twilio_error_code=getattr(e, 'code', None),
                twilio_error_message=str(e)
            ) from e
        except Exception as e:
            raise TwilioSendError(
                f"Unexpected error sending SMS OTP: {e}",
                channel="sms",
                recipient=phone_number
            ) from e

    async def asend_otp(self, phone_number: str) -> Tuple[bool, str]:
        """Async version of send_otp."""
        return await sync_to_async(self.send_otp)(phone_number)


__all__ = [
    "SMSOTPService",
]
