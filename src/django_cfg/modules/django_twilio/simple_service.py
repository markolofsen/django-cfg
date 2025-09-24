"""
Simplified Twilio service for basic messaging.

This module provides a simple interface for sending WhatsApp and SMS messages
without the complexity of the OTP system.
"""

import logging
from typing import Optional, Dict, Any
from twilio.rest import Client
from twilio.base.exceptions import TwilioException

from django_cfg.modules.base import BaseCfgModule
from django_cfg.modules.django_twilio.models import TwilioConfig
from django_cfg.modules.django_twilio.exceptions import (
    TwilioError,
    TwilioConfigurationError,
    TwilioSendError,
)

logger = logging.getLogger(__name__)


class SimpleTwilioService(BaseCfgModule):
    """
    Simplified Twilio service for basic messaging operations.
    
    Provides easy-to-use methods for sending WhatsApp and SMS messages
    without the complexity of OTP verification systems.
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
    
    def send_whatsapp_message(
        self, 
        to: str, 
        body: str, 
        from_number: Optional[str] = None,
        content_sid: Optional[str] = None,
        content_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message.
        
        Args:
            to: Recipient phone number (with whatsapp: prefix)
            body: Message text (ignored if content_sid is provided)
            from_number: Sender number (defaults to sandbox number)
            content_sid: Content template SID for approved templates
            content_variables: Variables for content template
            
        Returns:
            Dictionary with message details
            
        Raises:
            TwilioSendError: If message sending fails
        """
        try:
            client = self.get_client()
            config = self.get_config()
            
            # Ensure to number has whatsapp prefix
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'
            
            # Use default from number if not provided
            if not from_number:
                from_number = 'whatsapp:+14155238886'  # Twilio sandbox
            elif not from_number.startswith('whatsapp:'):
                from_number = f'whatsapp:{from_number}'
            
            # Prepare message parameters
            message_params = {
                'to': to,
                'from_': from_number,
            }
            
            # Use content template if provided
            if content_sid:
                message_params['content_sid'] = content_sid
                if content_variables:
                    import json
                    message_params['content_variables'] = json.dumps(content_variables)
            else:
                message_params['body'] = body
            
            if config.debug_logging:
                logger.info(f"Sending WhatsApp message to {to[:15]}...")
            
            # Send message
            message = client.messages.create(**message_params)
            
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
            
        Raises:
            TwilioSendError: If message sending fails
        """
        try:
            client = self.get_client()
            config = self.get_config()
            
            # Use default from number if not provided
            if not from_number:
                from_number = '+12297021650'  # Your SMS number
            
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
            raise TwilioError(f"Failed to get message status: {str(e)}")


# Convenience functions
def send_whatsapp(to: str, body: str, **kwargs) -> Dict[str, Any]:
    """Send WhatsApp message using simplified service."""
    service = SimpleTwilioService()
    return service.send_whatsapp_message(to, body, **kwargs)


def send_sms(to: str, body: str, **kwargs) -> Dict[str, Any]:
    """Send SMS message using simplified service."""
    service = SimpleTwilioService()
    return service.send_sms_message(to, body, **kwargs)


def get_message_status(message_sid: str) -> Dict[str, Any]:
    """Get message status using simplified service."""
    service = SimpleTwilioService()
    return service.get_message_status(message_sid)
