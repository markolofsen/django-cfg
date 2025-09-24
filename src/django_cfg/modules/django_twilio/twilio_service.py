"""
Twilio service for WhatsApp, SMS, and Verify API.

Handles all Twilio-specific functionality including:
- WhatsApp messaging
- SMS messaging  
- OTP via Twilio Verify API
"""

import logging
import random
import string
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from asgiref.sync import sync_to_async

from django_cfg.modules.base import BaseCfgModule
from django_cfg.modules.django_twilio.models import TwilioConfig, TwilioVerifyConfig
from django_cfg.modules.django_twilio.exceptions import (
    TwilioConfigurationError,
    TwilioSendError,
)

logger = logging.getLogger(__name__)


class TwilioService(BaseCfgModule):
    """
    Unified Twilio service for WhatsApp, SMS, and OTP.
    
    Handles all Twilio operations with auto-configuration from DjangoConfig.
    """
    
    def __init__(self):
        """Initialize with auto-discovered configuration."""
        super().__init__()
        self._config: Optional[TwilioConfig] = None
        self._client: Optional[Client] = None
    
    def get_config(self) -> TwilioConfig:
        """Get Twilio configuration from DjangoConfig."""
        if self._config is None:
            django_config = super().get_config()
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
    
    def get_client(self) -> Client:
        """Get or create Twilio client."""
        if self._client is None:
            config = self.get_config()
            try:
                self._client = Client(
                    config.account_sid,
                    config.auth_token.get_secret_value()
                )
                
                if config.debug_logging:
                    logger.info(f"Twilio client initialized for account: {config.account_sid[:8]}...")
                    
            except Exception as e:
                raise TwilioConfigurationError(
                    f"Failed to initialize Twilio client: {str(e)}",
                    context={"account_sid": config.account_sid[:8] + "..."},
                    suggestions=["Verify your Twilio credentials"]
                )
        
        return self._client
    
    # === WhatsApp Methods ===
    
    def send_whatsapp_message(
        self, 
        to: str, 
        body: str, 
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message.
        
        Args:
            to: Recipient phone number
            body: Message text
            from_number: Sender number (defaults to sandbox)
            
        Returns:
            Dictionary with message details
        """
        try:
            client = self.get_client()
            config = self.get_config()
            
            # Ensure to number has whatsapp prefix
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            # Use default from number if not provided
            if not from_number:
                if config.whatsapp_from:
                    from_number = f'whatsapp:{config.whatsapp_from}'
                else:
                    from_number = 'whatsapp:+14155238886'  # Twilio sandbox fallback
            elif not from_number.startswith('whatsapp:'):
                from_number = f'whatsapp:{from_number}'
            
            if config.debug_logging:
                logger.info(f"Sending WhatsApp message to {to[:15]}...")
            
            # Send message
            message = client.messages.create(
                to=to,
                from_=from_number,
                body=body
            )
            
            result = {
                'sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'date_created': message.date_created,
                'price': message.price,
                'price_unit': message.price_unit,
            }
            
            if config.debug_logging:
                logger.info(f"WhatsApp message sent successfully: {message.sid}")
            
            return result
            
        except TwilioException as e:
            logger.error(f"Twilio API error: {e}")
            raise TwilioSendError(
                f"Failed to send WhatsApp message: {str(e)}",
                context={
                    'to': to,
                    'from': from_number,
                    'error_code': getattr(e, 'code', None),
                    'error_message': getattr(e, 'msg', str(e))
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {e}")
            raise TwilioSendError(f"Unexpected error: {str(e)}")
    
    # === SMS Methods ===
    
    def send_sms_message(
        self, 
        to: str, 
        body: str, 
        from_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send an SMS message.
        
        Args:
            to: Recipient phone number
            body: Message text
            from_number: Sender number
            
        Returns:
            Dictionary with message details
        """
        try:
            client = self.get_client()
            config = self.get_config()
            
            # Use default from number if not provided
            if not from_number:
                if config.sms_from:
                    from_number = config.sms_from
                else:
                    raise TwilioConfigurationError(
                        "SMS from number not configured",
                        missing_fields=["sms_from"],
                        suggestions=["Set sms_from in your TwilioConfig"]
                    )
            
            if config.debug_logging:
                logger.info(f"Sending SMS to {to[:10]}...")
            
            # Send message
            message = client.messages.create(
                to=to,
                from_=from_number,
                body=body
            )
            
            result = {
                'sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'date_created': message.date_created,
                'price': message.price,
                'price_unit': message.price_unit,
            }
            
            if config.debug_logging:
                logger.info(f"SMS sent successfully: {message.sid}")
            
            return result
            
        except TwilioException as e:
            logger.error(f"Twilio API error: {e}")
            raise TwilioSendError(
                f"Failed to send SMS: {str(e)}",
                context={
                    'to': to,
                    'from': from_number,
                    'error_code': getattr(e, 'code', None),
                    'error_message': getattr(e, 'msg', str(e))
                }
            )
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {e}")
            raise TwilioSendError(f"Unexpected error: {str(e)}")
    
    # === OTP Methods (Twilio Verify API) ===
    
    def send_whatsapp_otp_hybrid(self, phone_number: str, otp_code: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
        """
        HYBRID APPROACH: Send OTP via Direct WhatsApp first, then fallback to Verify API.
        
        Args:
            phone_number: Phone number in E.164 format
            otp_code: The OTP code to send
            fallback_to_sms: Whether to fallback to SMS if WhatsApp fails
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        success = False
        final_message = ""
        method_used = ""
        
        # STEP 1: Try Direct WhatsApp with custom OTP
        try:
            from django_cfg.core.config import get_current_config
            django_config = get_current_config()
            site_name = django_config.project_name if django_config else "Django CFG"
            
            # Create beautiful WhatsApp message
            whatsapp_message = f"""🔐 *{site_name} Verification*

Your verification code: *{otp_code}*

⏰ Expires in 10 minutes
🔒 Keep this code secure

_Powered by {site_name}_"""
            
            logger.info(f"🎯 Attempting Direct WhatsApp OTP to {self._mask_phone(phone_number)}...")
            result = self.send_whatsapp_message(phone_number, whatsapp_message)
            
            if result.get('sid'):  # If we got a message SID, it was sent successfully
                success = True
                method_used = "Direct WhatsApp"
                final_message = f"OTP sent via WhatsApp to {self._mask_phone(phone_number)}"
                logger.info(f"✅ Direct WhatsApp OTP sent successfully: {result.get('sid', 'N/A')}")
            else:
                logger.warning(f"❌ Direct WhatsApp failed: No SID returned")
                
        except Exception as e:
            logger.warning(f"❌ Direct WhatsApp error: {e}")
        
        # STEP 2: Fallback to Verify API if Direct WhatsApp failed
        if not success:
            try:
                logger.info(f"🔄 Fallback: Trying Verify API for {self._mask_phone(phone_number)}...")
                verify_success, verify_message = self.send_whatsapp_otp_verify(phone_number, fallback_to_sms)
                
                if verify_success:
                    success = True
                    method_used = "Verify API"
                    final_message = verify_message
                    logger.info(f"✅ Verify API fallback successful")
                else:
                    logger.error(f"❌ Verify API fallback failed: {verify_message}")
                    
            except Exception as e:
                logger.error(f"❌ Verify API fallback error: {e}")
        
        # STEP 3: Final check
        if not success:
            logger.error(f"❌ All WhatsApp methods failed for {self._mask_phone(phone_number)}")
            return False, "All WhatsApp delivery methods failed"
        
        logger.info(f"🎉 Phone OTP sent via {method_used} to {self._mask_phone(phone_number)}")
        return True, f"{final_message} ({method_used})"

    def send_whatsapp_otp_verify(self, phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
        """
        Send OTP via WhatsApp using Twilio Verify API.
        
        Args:
            phone_number: Phone number in E.164 format
            fallback_to_sms: Whether to fallback to SMS if WhatsApp fails
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        config = self.get_config()
        
        if not config.verify:
            raise TwilioConfigurationError(
                "Twilio Verify service not configured",
                missing_fields=["verify"],
                suggestions=["Configure TwilioVerifyConfig in your Twilio settings"]
            )
        
        client = self.get_client()
        
        try:
            # Try WhatsApp first
            logger.info(f"🚀 Sending WhatsApp OTP to {self._mask_phone(phone_number)} via Verify API")
            verification = client.verify.v2.services(
                config.verify.service_sid
            ).verifications.create(
                to=phone_number,
                channel='whatsapp'
            )
            
            # Log detailed Twilio response
            logger.info(f"📱 Twilio Verify Response: status={verification.status}, sid={verification.sid}, channel={verification.channel}, to={verification.to}")
            
            if verification.status == 'pending':
                logger.info(f"✅ WhatsApp OTP sent successfully to {self._mask_phone(phone_number)}")
                return True, f"OTP sent via WhatsApp to {self._mask_phone(phone_number)}"
            
            # If WhatsApp failed and fallback is enabled, try SMS
            if fallback_to_sms and verification.status != 'pending':
                logger.warning(f"WhatsApp failed for {self._mask_phone(phone_number)}, trying SMS fallback")
                return self.send_sms_otp(phone_number)
            
            raise TwilioSendError(
                f"WhatsApp OTP failed with status: {verification.status}",
                context={'phone': phone_number, 'status': verification.status}
            )
            
        except TwilioException as e:
            if fallback_to_sms:
                logger.warning(f"WhatsApp error for {self._mask_phone(phone_number)}: {e}, trying SMS")
                return self.send_sms_otp(phone_number)
            
            raise TwilioSendError(
                f"WhatsApp OTP failed: {e}",
                context={
                    'phone': phone_number,
                    'error_code': getattr(e, 'code', None),
                    'error_message': str(e)
                }
            ) from e
    
    def send_sms_otp(self, phone_number: str) -> Tuple[bool, str]:
        """
        Send OTP via SMS using Twilio Verify API.
        
        Args:
            phone_number: Phone number in E.164 format
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        config = self.get_config()
        
        if not config.verify:
            raise TwilioConfigurationError(
                "Twilio Verify service not configured",
                missing_fields=["verify"],
                suggestions=["Configure TwilioVerifyConfig in your Twilio settings"]
            )
        
        client = self.get_client()
        
        try:
            logger.info(f"📱 Sending SMS OTP to {self._mask_phone(phone_number)} via Verify API")
            verification = client.verify.v2.services(
                config.verify.service_sid
            ).verifications.create(
                to=phone_number,
                channel='sms'
            )
            
            # Log detailed Twilio response
            logger.info(f"📱 Twilio SMS Response: status={verification.status}, sid={verification.sid}, channel={verification.channel}, to={verification.to}")
            
            if verification.status == 'pending':
                logger.info(f"✅ SMS OTP sent successfully to {self._mask_phone(phone_number)}")
                return True, f"OTP sent via SMS to {self._mask_phone(phone_number)}"
            else:
                raise TwilioSendError(
                    f"SMS OTP failed with status: {verification.status}",
                    context={'phone': phone_number, 'status': verification.status}
                )
                
        except TwilioException as e:
            raise TwilioSendError(
                f"SMS OTP failed: {e}",
                context={
                    'phone': phone_number,
                    'error_code': getattr(e, 'code', None),
                    'error_message': str(e)
                }
            ) from e
    
    def verify_otp(self, phone_number: str, code: str) -> Tuple[bool, str]:
        """
        Verify OTP code using Twilio Verify API.
        
        Args:
            phone_number: Phone number used for OTP
            code: OTP code to verify
            
        Returns:
            Tuple[bool, str]: (is_valid, message)
        """
        config = self.get_config()
        
        if not config.verify:
            raise TwilioConfigurationError("Twilio Verify service not configured")
        
        try:
            client = self.get_client()
            
            verification_check = client.verify.v2.services(
                config.verify.service_sid
            ).verification_checks.create(
                to=phone_number,
                code=code
            )
            
            if verification_check.status == 'approved':
                logger.info(f"OTP verified successfully for {self._mask_phone(phone_number)}")
                return True, "OTP verified successfully"
            else:
                return False, f"Invalid OTP code: {verification_check.status}"
                
        except TwilioException as e:
            raise TwilioSendError(
                f"OTP verification failed: {e}",
                context={
                    'phone': phone_number,
                    'error_code': getattr(e, 'code', None),
                    'error_message': str(e)
                }
            ) from e
    
    # === Utility Methods ===
    
    def _mask_phone(self, phone: str) -> str:
        """Mask phone number for security in logs."""
        return f"***{phone[-4:]}" if len(phone) > 4 else "***"
    
    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get status of a sent message.
        
        Args:
            message_sid: Message SID to check
            
        Returns:
            Dictionary with message status
        """
        try:
            client = self.get_client()
            message = client.messages(message_sid).fetch()
            
            return {
                'sid': message.sid,
                'status': message.status,
                'to': message.to,
                'from': message.from_,
                'body': message.body,
                'date_created': message.date_created,
                'date_sent': message.date_sent,
                'date_updated': message.date_updated,
                'price': message.price,
                'price_unit': message.price_unit,
                'error_code': message.error_code,
                'error_message': message.error_message,
            }
            
        except TwilioException as e:
            raise TwilioSendError(f"Failed to get message status: {str(e)}")


# === Convenience Functions ===

def send_whatsapp(to: str, body: str, **kwargs) -> Dict[str, Any]:
    """Send WhatsApp message using Twilio service."""
    service = TwilioService()
    return service.send_whatsapp_message(to, body, **kwargs)


def send_sms(to: str, body: str, **kwargs) -> Dict[str, Any]:
    """Send SMS message using Twilio service."""
    service = TwilioService()
    return service.send_sms_message(to, body, **kwargs)


def send_whatsapp_otp_hybrid(phone_number: str, otp_code: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
    """Send WhatsApp OTP using hybrid approach (Direct WhatsApp first, then Verify API)."""
    service = TwilioService()
    return service.send_whatsapp_otp_hybrid(phone_number, otp_code, fallback_to_sms)


def send_whatsapp_otp(phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
    """Send WhatsApp OTP with optional SMS fallback using Verify API only."""
    service = TwilioService()
    return service.send_whatsapp_otp_verify(phone_number, fallback_to_sms)


def send_sms_otp(phone_number: str) -> Tuple[bool, str]:
    """Send SMS OTP."""
    service = TwilioService()
    return service.send_sms_otp(phone_number)


def verify_otp(phone_number: str, code: str) -> Tuple[bool, str]:
    """Verify OTP code."""
    service = TwilioService()
    return service.verify_otp(phone_number, code)


def get_message_status(message_sid: str) -> Dict[str, Any]:
    """Get message status."""
    service = TwilioService()
    return service.get_message_status(message_sid)
