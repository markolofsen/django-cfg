"""
Auto-configuring Twilio services for django_cfg.

This module provides comprehensive OTP and messaging services via WhatsApp, Email, and SMS.
Supports both synchronous and asynchronous operations following Django 5.2+ patterns.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper type annotations for all fields
- Comprehensive error handling with specific exceptions
- Full async/await support with context detection
"""

import asyncio
import logging
import random
import string
from typing import Optional, Tuple, Dict, Any, List, Union
from datetime import datetime, timedelta
from contextlib import asynccontextmanager

# Third-party imports
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from asgiref.sync import sync_to_async, async_to_sync

# Django CFG imports
from django_cfg.modules.base import BaseCfgModule
from django_cfg.modules.django_twilio.models import (
    TwilioConfig,
    TwilioChannelType,
    TwilioVerifyConfig,
    SendGridConfig,
)
from django_cfg.modules.django_twilio.exceptions import (
    TwilioError,
    TwilioConfigurationError,
    TwilioVerificationError,
    TwilioSendError,
    TwilioRateLimitError,
    TwilioNetworkError,
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


class EmailOTPService(BaseTwilioService):
    """
    Email OTP service using SendGrid.
    
    Provides OTP delivery via email with template support and
    comprehensive deliverability optimization.
    """
    
    def send_otp(
        self, 
        email: str, 
        subject: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, str]:
        """
        Send OTP via email.
        
        Args:
            email: Recipient email address
            subject: Custom email subject (uses default if not provided)
            template_data: Additional data for email template
            
        Returns:
            Tuple[bool, str, str]: (success, message, otp_code)
            
        Raises:
            TwilioConfigurationError: If SendGrid is not configured
            TwilioSendError: If email sending fails
        """
        config = self.get_twilio_config()
        
        if not config.sendgrid:
            raise TwilioConfigurationError(
                "SendGrid configuration not found",
                missing_fields=["sendgrid"],
                suggestions=["Configure SendGridConfig in your Twilio settings"]
            )
        
        sendgrid_client = self.get_sendgrid_client()
        if not sendgrid_client:
            raise TwilioConfigurationError("SendGrid client not initialized")
        
        try:
            # Generate OTP code
            otp_code = self._generate_otp(6)
            
            # Store OTP for verification
            self._store_otp(email, otp_code, config.verify.ttl_seconds if config.verify else 600)
            
            # Prepare email content
            if config.sendgrid.otp_template_id:
                # Use dynamic template
                success, message = self._send_template_email(
                    sendgrid_client, config.sendgrid, email, otp_code, template_data
                )
            else:
                # Use simple HTML email
                success, message = self._send_simple_email(
                    sendgrid_client, config.sendgrid, email, otp_code, subject
                )
            
            if success:
                logger.info(f"Email OTP sent successfully to {self._mask_identifier(email)}")
                return True, message, otp_code
            else:
                raise TwilioSendError(message, channel="email", recipient=email)
                
        except Exception as e:
            if isinstance(e, TwilioSendError):
                raise
            raise TwilioSendError(
                f"Failed to send email OTP: {e}",
                channel="email",
                recipient=email
            ) from e
    
    async def asend_otp(
        self, 
        email: str, 
        subject: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str, str]:
        """Async version of send_otp."""
        return await sync_to_async(self.send_otp)(email, subject, template_data)
    
    def _send_template_email(
        self, 
        client: SendGridAPIClient, 
        config: SendGridConfig, 
        email: str, 
        otp_code: str,
        template_data: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Send email using SendGrid dynamic template."""
        try:
            # Prepare template data
            dynamic_data = {
                'verification_code': otp_code,
                'user_email': email,
                'expiry_minutes': 10,
                'company_name': config.from_name,
                **config.custom_template_data,
                **(template_data or {})
            }
            
            message = Mail(
                from_email=(config.from_email, config.from_name),
                to_emails=email
            )
            
            message.template_id = config.otp_template_id
            message.dynamic_template_data = dynamic_data
            
            if config.reply_to_email:
                message.reply_to = config.reply_to_email
            
            response = client.send(message)
            
            if response.status_code in [200, 201, 202]:
                return True, f"OTP sent via email template to {self._mask_identifier(email)}"
            else:
                return False, f"SendGrid API error: {response.status_code}"
                
        except Exception as e:
            return False, f"Template email error: {e}"
    
    def _send_simple_email(
        self, 
        client: SendGridAPIClient, 
        config: SendGridConfig, 
        email: str, 
        otp_code: str,
        subject: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Send simple HTML email without template."""
        try:
            html_content = self._generate_html_content(otp_code, config.from_name)
            plain_content = self._generate_plain_content(otp_code)
            
            message = Mail(
                from_email=(config.from_email, config.from_name),
                to_emails=email,
                subject=subject or config.default_subject,
                html_content=html_content,
                plain_text_content=plain_content
            )
            
            if config.reply_to_email:
                message.reply_to = config.reply_to_email
            
            response = client.send(message)
            
            if response.status_code in [200, 201, 202]:
                return True, f"OTP sent via email to {self._mask_identifier(email)}"
            else:
                return False, f"SendGrid API error: {response.status_code}"
                
        except Exception as e:
            return False, f"Simple email error: {e}"
    
    def _generate_html_content(self, otp_code: str, company_name: str) -> str:
        """Generate HTML email content."""
        return f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; text-align: center;">
                <h1 style="color: #333; margin-bottom: 20px;">Verification Code</h1>
                <p style="color: #666; font-size: 16px; margin-bottom: 30px;">
                    Your verification code is:
                </p>
                <div style="background-color: #007bff; color: white; font-size: 32px; font-weight: bold; 
                     padding: 20px; border-radius: 8px; letter-spacing: 5px; margin: 30px 0;">
                    {otp_code}
                </div>
                <p style="color: #999; font-size: 14px;">
                    This code expires in 10 minutes<br>
                    If you didn't request this code, please ignore this email
                </p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                <p style="color: #999; font-size: 12px;">
                    Sent by {company_name}
                </p>
            </div>
        </div>
        """
    
    def _generate_plain_content(self, otp_code: str) -> str:
        """Generate plain text email content."""
        return f"""
Your verification code: {otp_code}

This code expires in 10 minutes.
If you didn't request this code, please ignore this email.
        """.strip()


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
        if not "@" in identifier and config.verify:
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


# Convenience functions for direct usage
def send_whatsapp_otp(phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
    """Send WhatsApp OTP with optional SMS fallback."""
    service = WhatsAppOTPService()
    return service.send_otp(phone_number, fallback_to_sms)


def send_email_otp(email: str, subject: Optional[str] = None) -> Tuple[bool, str, str]:
    """Send email OTP."""
    service = EmailOTPService()
    return service.send_otp(email, subject)


def send_sms_otp(phone_number: str) -> Tuple[bool, str]:
    """Send SMS OTP."""
    service = SMSOTPService()
    return service.send_otp(phone_number)


def verify_otp(identifier: str, code: str) -> Tuple[bool, str]:
    """Verify OTP code for any channel."""
    service = UnifiedOTPService()
    return service.verify_otp(identifier, code)


# Async convenience functions
async def asend_whatsapp_otp(phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
    """Async send WhatsApp OTP."""
    service = WhatsAppOTPService()
    return await service.asend_otp(phone_number, fallback_to_sms)


async def asend_email_otp(email: str, subject: Optional[str] = None) -> Tuple[bool, str, str]:
    """Async send email OTP."""
    service = EmailOTPService()
    return await service.asend_otp(email, subject)


async def asend_sms_otp(phone_number: str) -> Tuple[bool, str]:
    """Async send SMS OTP."""
    service = SMSOTPService()
    return await service.asend_otp(phone_number)


async def averify_otp(identifier: str, code: str) -> Tuple[bool, str]:
    """Async verify OTP code."""
    service = UnifiedOTPService()
    return await service.averify_otp(identifier, code)


# Export all service classes and functions
__all__ = [
    # Service classes
    "DjangoTwilioService",
    "WhatsAppOTPService",
    "EmailOTPService", 
    "SMSOTPService",
    "UnifiedOTPService",
    "BaseTwilioService",
    
    # Sync convenience functions
    "send_whatsapp_otp",
    "send_email_otp",
    "send_sms_otp", 
    "verify_otp",
    
    # Async convenience functions
    "asend_whatsapp_otp",
    "asend_email_otp",
    "asend_sms_otp",
    "averify_otp",
    
    # Utility functions
    "is_async_context",
]
