"""
Custom exceptions for django_cfg Twilio module.

Following CRITICAL_REQUIREMENTS.md - proper exception handling with specific types.
No exception suppression, all errors must be properly typed and handled.
"""

from typing import Optional, Dict, Any, List


class TwilioError(Exception):
    """
    Base exception for all Twilio-related errors.
    
    All Twilio module exceptions inherit from this base class to allow
    for specific exception handling patterns.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None
    ) -> None:
        """
        Initialize exception with detailed context.
        
        Args:
            message: Human-readable error message
            error_code: Twilio-specific error code (if available)
            context: Additional context information for debugging
            suggestions: List of suggested fixes or actions
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.suggestions = suggestions or []
    
    def __str__(self) -> str:
        """Return formatted error message with context."""
        parts = [self.message]
        
        if self.error_code:
            parts.append(f"Error Code: {self.error_code}")
        
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        
        if self.suggestions:
            suggestions_str = "; ".join(self.suggestions)
            parts.append(f"Suggestions: {suggestions_str}")
        
        return " | ".join(parts)


class TwilioConfigurationError(TwilioError):
    """
    Configuration-related errors in Twilio module.
    
    Raised when:
    - Missing required credentials (account_sid, auth_token, etc.)
    - Invalid configuration values
    - Missing environment variables
    - Incorrect service setup
    """
    
    def __init__(
        self,
        message: str,
        missing_fields: Optional[List[str]] = None,
        invalid_fields: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Initialize configuration error.
        
        Args:
            message: Error description
            missing_fields: List of missing required fields
            invalid_fields: List of fields with invalid values
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        
        if missing_fields:
            context["missing_fields"] = missing_fields
        if invalid_fields:
            context["invalid_fields"] = invalid_fields
        
        kwargs["context"] = context
        
        # Add default suggestions for configuration errors
        suggestions = kwargs.get("suggestions", [])
        if missing_fields:
            suggestions.append(f"Set environment variables: {', '.join(missing_fields)}")
        if invalid_fields:
            suggestions.append(f"Check configuration for fields: {', '.join(invalid_fields)}")
        
        kwargs["suggestions"] = suggestions
        
        super().__init__(message, **kwargs)


class TwilioVerificationError(TwilioError):
    """
    OTP verification-related errors.
    
    Raised when:
    - Invalid OTP code provided
    - OTP code expired
    - Too many verification attempts
    - Verification service unavailable
    """
    
    def __init__(
        self,
        message: str,
        verification_sid: Optional[str] = None,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        attempts_remaining: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Initialize verification error.
        
        Args:
            message: Error description
            verification_sid: Twilio verification SID (if available)
            phone_number: Phone number being verified (masked for security)
            email: Email being verified (masked for security)
            attempts_remaining: Number of attempts remaining
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        
        if verification_sid:
            context["verification_sid"] = verification_sid
        if phone_number:
            # Mask phone number for security (show only last 4 digits)
            masked_phone = f"***{phone_number[-4:]}" if len(phone_number) > 4 else "***"
            context["phone_number"] = masked_phone
        if email:
            # Mask email for security
            email_parts = email.split("@")
            if len(email_parts) == 2:
                masked_email = f"{email_parts[0][:2]}***@{email_parts[1]}"
                context["email"] = masked_email
        if attempts_remaining is not None:
            context["attempts_remaining"] = attempts_remaining
        
        kwargs["context"] = context
        
        super().__init__(message, **kwargs)


class TwilioSendError(TwilioError):
    """
    Message sending-related errors.
    
    Raised when:
    - Failed to send WhatsApp message
    - Failed to send SMS
    - Failed to send email via SendGrid
    - Network connectivity issues
    - Service rate limits exceeded
    """
    
    def __init__(
        self,
        message: str,
        channel: Optional[str] = None,
        recipient: Optional[str] = None,
        twilio_error_code: Optional[int] = None,
        twilio_error_message: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize send error.
        
        Args:
            message: Error description
            channel: Communication channel (whatsapp, sms, email)
            recipient: Recipient identifier (masked for security)
            twilio_error_code: Twilio API error code
            twilio_error_message: Twilio API error message
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        
        if channel:
            context["channel"] = channel
        if recipient:
            # Mask recipient for security
            if "@" in recipient:  # Email
                email_parts = recipient.split("@")
                if len(email_parts) == 2:
                    masked_recipient = f"{email_parts[0][:2]}***@{email_parts[1]}"
                    context["recipient"] = masked_recipient
            else:  # Phone number
                masked_recipient = f"***{recipient[-4:]}" if len(recipient) > 4 else "***"
                context["recipient"] = masked_recipient
        if twilio_error_code:
            context["twilio_error_code"] = twilio_error_code
        if twilio_error_message:
            context["twilio_error_message"] = twilio_error_message
        
        kwargs["context"] = context
        
        # Add channel-specific suggestions
        suggestions = kwargs.get("suggestions", [])
        if channel == "whatsapp":
            suggestions.extend([
                "Verify WhatsApp Business account is approved",
                "Check if recipient has opted in to WhatsApp messages",
                "Try SMS fallback if WhatsApp fails"
            ])
        elif channel == "sms":
            suggestions.extend([
                "Verify phone number format (E.164)",
                "Check if SMS is supported in recipient's country",
                "Verify Twilio account balance"
            ])
        elif channel == "email":
            suggestions.extend([
                "Verify SendGrid API key is valid",
                "Check if sender email is verified in SendGrid",
                "Verify recipient email format"
            ])
        
        kwargs["suggestions"] = suggestions
        
        super().__init__(message, **kwargs)


class TwilioRateLimitError(TwilioSendError):
    """
    Rate limit exceeded errors.
    
    Raised when:
    - Twilio API rate limits are exceeded
    - SendGrid rate limits are exceeded
    - Too many requests in a time window
    """
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Initialize rate limit error.
        
        Args:
            message: Error description
            retry_after: Seconds to wait before retrying
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        
        if retry_after:
            context["retry_after_seconds"] = retry_after
        
        kwargs["context"] = context
        
        suggestions = kwargs.get("suggestions", [])
        suggestions.extend([
            f"Wait {retry_after} seconds before retrying" if retry_after else "Wait before retrying",
            "Implement exponential backoff for retries",
            "Consider upgrading Twilio plan for higher limits"
        ])
        kwargs["suggestions"] = suggestions
        
        super().__init__(message, **kwargs)


class TwilioNetworkError(TwilioError):
    """
    Network connectivity errors.
    
    Raised when:
    - Cannot connect to Twilio API
    - Cannot connect to SendGrid API
    - DNS resolution failures
    - Timeout errors
    """
    
    def __init__(
        self,
        message: str,
        service: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> None:
        """
        Initialize network error.
        
        Args:
            message: Error description
            service: Service that failed (twilio, sendgrid)
            timeout: Request timeout value
            **kwargs: Additional context passed to base class
        """
        context = kwargs.get("context", {})
        
        if service:
            context["service"] = service
        if timeout:
            context["timeout_seconds"] = timeout
        
        kwargs["context"] = context
        
        suggestions = kwargs.get("suggestions", [])
        suggestions.extend([
            "Check internet connectivity",
            "Verify firewall settings allow HTTPS traffic",
            "Try increasing request timeout",
            "Check Twilio/SendGrid service status"
        ])
        kwargs["suggestions"] = suggestions
        
        super().__init__(message, **kwargs)


# Export all exception classes
__all__ = [
    "TwilioError",
    "TwilioConfigurationError",
    "TwilioVerificationError", 
    "TwilioSendError",
    "TwilioRateLimitError",
    "TwilioNetworkError",
]
