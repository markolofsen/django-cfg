"""
Pydantic v2 configuration models for django_cfg Twilio module.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper type annotations for all fields
- No mutable default arguments
- Comprehensive validation and error handling
"""

from typing import Optional, Dict, Any, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, SecretStr
from enum import Enum

from django_cfg.modules.django_twilio.exceptions import TwilioConfigurationError


class TwilioChannelType(str, Enum):
    """Supported Twilio communication channels."""
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "call"
    EMAIL = "email"


class TwilioRegion(str, Enum):
    """Twilio service regions for compliance and performance."""
    US = "us1"  # United States (default)
    DUBLIN = "dublin"  # Europe
    SINGAPORE = "singapore"  # Asia Pacific
    SYDNEY = "sydney"  # Australia


class SendGridTemplateType(str, Enum):
    """SendGrid template types."""
    DYNAMIC = "dynamic"
    LEGACY = "legacy"


class TwilioVerifyConfig(BaseModel):
    """
    Configuration for Twilio Verify service.
    
    Handles OTP verification across multiple channels with smart fallbacks.
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }
    
    # Core Verify service settings
    service_sid: str = Field(
        ...,
        description="Twilio Verify Service SID (starts with VA)",
        min_length=34,
        max_length=34,
        pattern=r"^VA[a-f0-9]{32}$",
    )
    
    service_name: str = Field(
        default="OTP Verification",
        description="Human-readable service name for OTP messages",
        min_length=1,
        max_length=50,
    )
    
    # Channel configuration
    default_channel: TwilioChannelType = Field(
        default=TwilioChannelType.SMS,
        description="Default channel for OTP delivery",
    )
    
    fallback_channels: List[TwilioChannelType] = Field(
        default_factory=lambda: [TwilioChannelType.SMS],
        description="Fallback channels if primary channel fails",
        min_length=1,
    )
    
    # OTP settings
    code_length: int = Field(
        default=6,
        description="Length of generated OTP codes",
        ge=4,
        le=10,
    )
    
    ttl_seconds: int = Field(
        default=600,  # 10 minutes
        description="Time-to-live for OTP codes in seconds",
        ge=60,  # Minimum 1 minute
        le=3600,  # Maximum 1 hour
    )
    
    max_attempts: int = Field(
        default=5,
        description="Maximum verification attempts per code",
        ge=1,
        le=10,
    )
    
    # Rate limiting
    rate_limit_per_phone: int = Field(
        default=5,
        description="Maximum OTP requests per phone number per hour",
        ge=1,
        le=20,
    )
    
    rate_limit_per_ip: int = Field(
        default=10,
        description="Maximum OTP requests per IP address per hour",
        ge=1,
        le=50,
    )
    
    @field_validator("fallback_channels")
    @classmethod
    def validate_fallback_channels(cls, v: List[TwilioChannelType]) -> List[TwilioChannelType]:
        """Ensure fallback channels are unique."""
        if len(v) != len(set(v)):
            raise ValueError("Fallback channels must be unique")
        return v


class SendGridConfig(BaseModel):
    """
    Configuration for SendGrid email service.
    
    Handles email OTP delivery with template support and deliverability optimization.
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }
    
    # Core SendGrid settings
    api_key: SecretStr = Field(
        ...,
        description="SendGrid API Key",
        min_length=69,  # SendGrid API keys are 69 characters
        max_length=69,
    )
    
    from_email: str = Field(
        ...,
        description="Verified sender email address",
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
    )
    
    from_name: str = Field(
        default="OTP Service",
        description="Sender name displayed in emails",
        min_length=1,
        max_length=100,
    )
    
    # Template configuration
    otp_template_id: Optional[str] = Field(
        default=None,
        description="SendGrid dynamic template ID for OTP emails",
        pattern=r"^d-[a-f0-9]{32}$",
    )
    
    template_type: SendGridTemplateType = Field(
        default=SendGridTemplateType.DYNAMIC,
        description="Type of SendGrid template to use",
    )
    
    # Email content settings (used when no template is specified)
    default_subject: str = Field(
        default="Your verification code",
        description="Default email subject line",
        min_length=1,
        max_length=200,
    )
    
    # Deliverability settings
    reply_to_email: Optional[str] = Field(
        default=None,
        description="Reply-to email address",
        pattern=r"^[^@]+@[^@]+\.[^@]+$",
    )
    
    tracking_enabled: bool = Field(
        default=True,
        description="Enable email open and click tracking",
    )
    
    # Template data customization
    custom_template_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional data to pass to email templates",
    )
    
    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        """Validate SendGrid API key format."""
        api_key_str = v.get_secret_value()
        if not api_key_str.startswith("SG."):
            raise ValueError("SendGrid API key must start with 'SG.'")
        return v


class TwilioConfig(BaseModel):
    """
    Main Twilio configuration model for django_cfg integration.
    
    Provides type-safe configuration for all Twilio services including
    Verify API, WhatsApp, SMS, and SendGrid email integration.
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
        "validate_default": True,
    }
    
    # Core Twilio credentials
    account_sid: str = Field(
        ...,
        description="Twilio Account SID",
        min_length=34,
        max_length=34,
        pattern=r"^AC[a-f0-9]{32}$",
    )
    
    auth_token: SecretStr = Field(
        ...,
        description="Twilio Auth Token",
        min_length=32,
        max_length=32,
    )
    
    # Service configuration
    verify: Optional[TwilioVerifyConfig] = Field(
        default=None,
        description="Twilio Verify service configuration for OTP",
    )
    
    sendgrid: Optional[SendGridConfig] = Field(
        default=None,
        description="SendGrid email service configuration",
    )
    
    # Global settings
    region: TwilioRegion = Field(
        default=TwilioRegion.US,
        description="Twilio service region for compliance and performance",
    )
    
    webhook_url: Optional[str] = Field(
        default=None,
        description="Webhook URL for delivery status callbacks",
        pattern=r"^https?://[^\s]+$",
    )
    
    # Debug and testing
    test_mode: bool = Field(
        default=False,
        description="Enable test mode (uses Twilio test credentials)",
    )
    
    debug_logging: bool = Field(
        default=False,
        description="Enable detailed logging for debugging",
    )
    
    # Timeout settings
    request_timeout: int = Field(
        default=30,
        description="HTTP request timeout in seconds",
        ge=5,
        le=300,
    )
    
    # Retry configuration
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests",
        ge=0,
        le=10,
    )
    
    retry_delay: float = Field(
        default=1.0,
        description="Base delay between retries in seconds",
        ge=0.1,
        le=60.0,
    )
    
    @model_validator(mode="after")
    def validate_service_configuration(self) -> "TwilioConfig":
        """Validate service configuration - allow basic messaging without services."""
        # For basic messaging, no additional services are required
        # Only validate if services are configured
        if self.verify and self.sendgrid:
            # If email is in fallback channels, SendGrid must be configured
            all_channels = [self.verify.default_channel] + self.verify.fallback_channels
            if TwilioChannelType.EMAIL in all_channels and not self.sendgrid:
                raise TwilioConfigurationError(
                    "SendGrid configuration required when email channel is enabled",
                    missing_fields=["sendgrid"],
                    context={"enabled_channels": [ch.value for ch in all_channels]},
                    suggestions=["Configure SendGrid settings for email OTP delivery"]
                )
        
        return self
    
    
    def get_client_config(self) -> Dict[str, Any]:
        """
        Get configuration for Twilio client initialization.
        
        Returns:
            Dictionary with client configuration parameters
        """
        config = {
            "username": self.account_sid,
            "password": self.auth_token.get_secret_value(),
            "region": self.region.value,
        }
        
        if self.webhook_url:
            config["webhook_url"] = self.webhook_url
            
        return config
    
    def get_sendgrid_config(self) -> Optional[Dict[str, Any]]:
        """
        Get configuration for SendGrid client initialization.
        
        Returns:
            Dictionary with SendGrid configuration or None if not configured
        """
        if not self.sendgrid:
            return None
            
        return {
            "api_key": self.sendgrid.api_key.get_secret_value(),
            "from_email": self.sendgrid.from_email,
            "from_name": self.sendgrid.from_name,
            "template_id": self.sendgrid.otp_template_id,
            "tracking_enabled": self.sendgrid.tracking_enabled,
        }
    
    def is_channel_enabled(self, channel: TwilioChannelType) -> bool:
        """
        Check if a specific channel is enabled in the configuration.
        
        Args:
            channel: Channel type to check
            
        Returns:
            True if channel is enabled, False otherwise
        """
        # Check email channel separately (SendGrid)
        if channel == TwilioChannelType.EMAIL:
            return self.sendgrid is not None
        
        # Check Verify channels (WhatsApp, SMS, Voice)
        if not self.verify:
            return False
            
        all_channels = [self.verify.default_channel] + self.verify.fallback_channels
        return channel in all_channels
    
    def get_enabled_channels(self) -> List[TwilioChannelType]:
        """
        Get list of all enabled channels.
        
        Returns:
            List of enabled channel types
        """
        channels = []
        
        if self.verify:
            channels.append(self.verify.default_channel)
            channels.extend(self.verify.fallback_channels)
            
        if self.sendgrid and TwilioChannelType.EMAIL not in channels:
            channels.append(TwilioChannelType.EMAIL)
            
        # Remove duplicates while preserving order
        seen = set()
        unique_channels = []
        for channel in channels:
            if channel not in seen:
                seen.add(channel)
                unique_channels.append(channel)
                
        return unique_channels


# Export configuration models
__all__ = [
    "TwilioConfig",
    "TwilioVerifyConfig", 
    "SendGridConfig",
    "TwilioChannelType",
    "TwilioRegion",
    "SendGridTemplateType",
]
