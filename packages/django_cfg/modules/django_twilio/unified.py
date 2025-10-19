"""
Unified OTP service with multi-channel support and DjangoTwilioService.

Provides intelligent channel selection and automatic fallback based on
configuration and delivery success rates.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from asgiref.sync import sync_to_async

from .base import BaseTwilioService
from .email_otp import EmailOTPService
from .exceptions import (
    TwilioConfigurationError,
    TwilioSendError,
    TwilioVerificationError,
)
from .models import TwilioChannelType, TwilioConfig
from .sms import SMSOTPService
from .whatsapp import WhatsAppOTPService

logger = logging.getLogger(__name__)


class UnifiedOTPService(BaseTwilioService):
    """
    Unified OTP service that handles all channels with smart fallbacks.

    Provides intelligent channel selection and automatic fallback
    based on configuration and delivery success rates.
    """

    def __init__(self):
        """Initialize with specialized service instances."""
        super().__init__()
        self._whatsapp_service = WhatsAppOTPService()
        self._email_service = EmailOTPService()
        self._sms_service = SMSOTPService()

    def send_otp(
        self,
        identifier: str,
        preferred_channel: Optional[TwilioChannelType] = None,
        enable_fallback: bool = True
    ) -> Tuple[bool, str, TwilioChannelType]:
        """
        Send OTP using the best available channel.

        Args:
            identifier: Phone number (E.164) or email address
            preferred_channel: Preferred delivery channel
            enable_fallback: Whether to try fallback channels

        Returns:
            Tuple[bool, str, TwilioChannelType]: (success, message, used_channel)
        """
        config = self.get_twilio_config()

        # Determine identifier type
        is_email = "@" in identifier

        # Get available channels
        available_channels = self._get_available_channels(is_email, config)

        if not available_channels:
            raise TwilioConfigurationError(
                "No channels configured for OTP delivery",
                suggestions=["Configure at least one channel (WhatsApp, SMS, or Email)"]
            )

        # Determine channel order
        channel_order = self._get_channel_order(
            available_channels, preferred_channel, is_email, config
        )

        last_error = None

        for channel in channel_order:
            try:
                success, message = self._send_via_channel(identifier, channel)
                if success:
                    return True, message, channel

            except Exception as e:
                last_error = e
                logger.warning(f"Channel {channel.value} failed for {self._mask_identifier(identifier)}: {e}")

                if not enable_fallback:
                    raise

        # All channels failed
        raise TwilioSendError(
            f"All configured channels failed for {self._mask_identifier(identifier)}",
            context={"tried_channels": [ch.value for ch in channel_order]},
            suggestions=["Check service configurations", "Verify recipient details"]
        ) from last_error

    async def asend_otp(
        self,
        identifier: str,
        preferred_channel: Optional[TwilioChannelType] = None,
        enable_fallback: bool = True
    ) -> Tuple[bool, str, TwilioChannelType]:
        """Async version of send_otp."""
        return await sync_to_async(self.send_otp)(identifier, preferred_channel, enable_fallback)

    def verify_otp(self, identifier: str, code: str) -> Tuple[bool, str]:
        """
        Verify OTP code for any channel.

        Args:
            identifier: Phone number or email used for OTP
            code: OTP code to verify

        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        config = self.get_twilio_config()

        # For Twilio Verify channels (WhatsApp, SMS), use Twilio verification
        if "@" not in identifier and config.verify:
            return self._verify_twilio_otp(identifier, code, config)

        # For email or custom verification, use stored OTP
        return self._verify_stored_otp(identifier, code)

    async def averify_otp(self, identifier: str, code: str) -> Tuple[bool, str]:
        """Async version of verify_otp."""
        return await sync_to_async(self.verify_otp)(identifier, code)

    def _get_available_channels(self, is_email: bool, config: TwilioConfig) -> List[TwilioChannelType]:
        """Get list of available channels based on configuration."""
        channels = []

        if config.verify:
            if not is_email:  # Phone number - can use WhatsApp/SMS
                channels.extend([TwilioChannelType.WHATSAPP, TwilioChannelType.SMS])

        if config.sendgrid:  # Email available
            channels.append(TwilioChannelType.EMAIL)

        return channels

    def _get_channel_order(
        self,
        available_channels: List[TwilioChannelType],
        preferred_channel: Optional[TwilioChannelType],
        is_email: bool,
        config: TwilioConfig
    ) -> List[TwilioChannelType]:
        """Determine optimal channel order for delivery attempts."""

        # If preferred channel is specified and available, try it first
        if preferred_channel and preferred_channel in available_channels:
            ordered_channels = [preferred_channel]
            remaining = [ch for ch in available_channels if ch != preferred_channel]
            ordered_channels.extend(remaining)
            return ordered_channels

        # Default ordering based on identifier type and configuration
        if is_email:
            return [TwilioChannelType.EMAIL]

        # For phone numbers, prefer WhatsApp -> SMS
        phone_channels = []
        if TwilioChannelType.WHATSAPP in available_channels:
            phone_channels.append(TwilioChannelType.WHATSAPP)
        if TwilioChannelType.SMS in available_channels:
            phone_channels.append(TwilioChannelType.SMS)

        return phone_channels

    def _send_via_channel(self, identifier: str, channel: TwilioChannelType) -> Tuple[bool, str]:
        """Send OTP via specific channel."""
        if channel == TwilioChannelType.WHATSAPP:
            return self._whatsapp_service.send_otp(identifier, fallback_to_sms=False)
        elif channel == TwilioChannelType.SMS:
            return self._sms_service.send_otp(identifier)
        elif channel == TwilioChannelType.EMAIL:
            success, message, _ = self._email_service.send_otp(identifier)
            return success, message
        else:
            raise TwilioSendError(f"Unsupported channel: {channel.value}")

    def _verify_twilio_otp(self, phone_number: str, code: str, config: TwilioConfig) -> Tuple[bool, str]:
        """Verify OTP using Twilio Verify API."""
        try:
            client = self.get_twilio_client()

            verification_check = client.verify.v2.services(
                config.verify.service_sid
            ).verification_checks.create(
                to=phone_number,
                code=code
            )

            if verification_check.status == 'approved':
                logger.info(f"OTP verified successfully for {self._mask_identifier(phone_number)}")
                return True, "OTP verified successfully"
            else:
                return False, f"Invalid OTP code: {verification_check.status}"

        except TwilioException as e:
            raise TwilioVerificationError(
                f"OTP verification failed: {e}",
                phone_number=phone_number,
                twilio_error_code=getattr(e, 'code', None),
                twilio_error_message=str(e)
            ) from e

    def _verify_stored_otp(self, identifier: str, code: str) -> Tuple[bool, str]:
        """Verify OTP using stored codes (for email)."""
        stored_data = self._get_stored_otp(identifier)

        if not stored_data:
            return False, "OTP not found. Please request a new code."

        if datetime.now() > stored_data['expires_at']:
            self._remove_otp(identifier)
            return False, "OTP expired. Please request a new code."

        # Increment attempt counter
        stored_data['attempts'] += 1

        if stored_data['attempts'] > 5:  # Max attempts
            self._remove_otp(identifier)
            return False, "Too many attempts. Please request a new code."

        if stored_data['code'] == code:
            self._remove_otp(identifier)
            logger.info(f"Stored OTP verified successfully for {self._mask_identifier(identifier)}")
            return True, "OTP verified successfully"
        else:
            return False, f"Invalid OTP code. {5 - stored_data['attempts']} attempts remaining."


class DjangoTwilioService(UnifiedOTPService):
    """
    Main Twilio service for django_cfg integration.

    Provides unified access to all Twilio services with auto-configuration
    and comprehensive error handling. This is the primary service class
    that should be used in most applications.
    """

    def __init__(self):
        """Initialize with all service capabilities."""
        super().__init__()
        logger.info("DjangoTwilioService initialized with auto-configuration")

    def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of all Twilio services.

        Returns:
            Dictionary with service status information
        """
        try:
            config = self.get_twilio_config()

            status = {
                "twilio_configured": True,
                "account_sid": config.account_sid,
                "region": config.region.value,
                "services": {},
                "enabled_channels": [ch.value for ch in config.get_enabled_channels()],
                "test_mode": config.test_mode,
            }

            # Check Verify service
            if config.verify:
                status["services"]["verify"] = {
                    "enabled": True,
                    "service_sid": config.verify.service_sid,
                    "default_channel": config.verify.default_channel.value,
                    "fallback_channels": [ch.value for ch in config.verify.fallback_channels],
                    "code_length": config.verify.code_length,
                    "ttl_seconds": config.verify.ttl_seconds,
                }
            else:
                status["services"]["verify"] = {"enabled": False}

            # Check SendGrid service
            if config.sendgrid:
                status["services"]["sendgrid"] = {
                    "enabled": True,
                    "from_email": config.sendgrid.from_email,
                    "from_name": config.sendgrid.from_name,
                    "template_configured": config.sendgrid.otp_template_id is not None,
                    "tracking_enabled": config.sendgrid.tracking_enabled,
                }
            else:
                status["services"]["sendgrid"] = {"enabled": False}

            return status

        except Exception as e:
            return {
                "twilio_configured": False,
                "error": str(e),
                "services": {},
            }


__all__ = [
    "UnifiedOTPService",
    "DjangoTwilioService",
]
