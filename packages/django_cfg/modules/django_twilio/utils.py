"""
Convenience functions for direct Twilio service usage.

Provides simple function-based API for sending and verifying OTPs
without manually instantiating service classes.
"""

from typing import Optional, Tuple

from .email_otp import EmailOTPService
from .sms import SMSOTPService
from .unified import UnifiedOTPService
from .whatsapp import WhatsAppOTPService

# Sync convenience functions

def send_whatsapp_otp(phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
    """
    Send WhatsApp OTP with optional SMS fallback.

    Args:
        phone_number: Phone number in E.164 format
        fallback_to_sms: Whether to fallback to SMS if WhatsApp fails

    Returns:
        Tuple[bool, str]: (success, message)

    Example:
        >>> success, message = send_whatsapp_otp("+1234567890")
        >>> if success:
        ...     print(f"OTP sent: {message}")
    """
    service = WhatsAppOTPService()
    return service.send_otp(phone_number, fallback_to_sms)


def send_email_otp(email: str, subject: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Send email OTP.

    Args:
        email: Recipient email address
        subject: Optional custom email subject

    Returns:
        Tuple[bool, str, str]: (success, message, otp_code)

    Example:
        >>> success, message, otp_code = send_email_otp("user@example.com")
        >>> if success:
        ...     print(f"OTP sent: {otp_code}")
    """
    service = EmailOTPService()
    return service.send_otp(email, subject)


def send_sms_otp(phone_number: str) -> Tuple[bool, str]:
    """
    Send SMS OTP.

    Args:
        phone_number: Phone number in E.164 format

    Returns:
        Tuple[bool, str]: (success, message)

    Example:
        >>> success, message = send_sms_otp("+1234567890")
        >>> if success:
        ...     print(f"OTP sent: {message}")
    """
    service = SMSOTPService()
    return service.send_otp(phone_number)


def verify_otp(identifier: str, code: str) -> Tuple[bool, str]:
    """
    Verify OTP code for any channel.

    Args:
        identifier: Phone number or email used for OTP
        code: OTP code to verify

    Returns:
        Tuple[bool, str]: (is_valid, message)

    Example:
        >>> is_valid, message = verify_otp("+1234567890", "123456")
        >>> if is_valid:
        ...     print("OTP verified successfully!")
    """
    service = UnifiedOTPService()
    return service.verify_otp(identifier, code)


# Async convenience functions

async def asend_whatsapp_otp(phone_number: str, fallback_to_sms: bool = True) -> Tuple[bool, str]:
    """
    Async send WhatsApp OTP.

    Args:
        phone_number: Phone number in E.164 format
        fallback_to_sms: Whether to fallback to SMS if WhatsApp fails

    Returns:
        Tuple[bool, str]: (success, message)

    Example:
        >>> success, message = await asend_whatsapp_otp("+1234567890")
        >>> if success:
        ...     print(f"OTP sent: {message}")
    """
    service = WhatsAppOTPService()
    return await service.asend_otp(phone_number, fallback_to_sms)


async def asend_email_otp(email: str, subject: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Async send email OTP.

    Args:
        email: Recipient email address
        subject: Optional custom email subject

    Returns:
        Tuple[bool, str, str]: (success, message, otp_code)

    Example:
        >>> success, message, otp_code = await asend_email_otp("user@example.com")
        >>> if success:
        ...     print(f"OTP sent: {otp_code}")
    """
    service = EmailOTPService()
    return await service.asend_otp(email, subject)


async def asend_sms_otp(phone_number: str) -> Tuple[bool, str]:
    """
    Async send SMS OTP.

    Args:
        phone_number: Phone number in E.164 format

    Returns:
        Tuple[bool, str]: (success, message)

    Example:
        >>> success, message = await asend_sms_otp("+1234567890")
        >>> if success:
        ...     print(f"OTP sent: {message}")
    """
    service = SMSOTPService()
    return await service.asend_otp(phone_number)


async def averify_otp(identifier: str, code: str) -> Tuple[bool, str]:
    """
    Async verify OTP code.

    Args:
        identifier: Phone number or email used for OTP
        code: OTP code to verify

    Returns:
        Tuple[bool, str]: (is_valid, message)

    Example:
        >>> is_valid, message = await averify_otp("+1234567890", "123456")
        >>> if is_valid:
        ...     print("OTP verified successfully!")
    """
    service = UnifiedOTPService()
    return await service.averify_otp(identifier, code)


__all__ = [
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
]
