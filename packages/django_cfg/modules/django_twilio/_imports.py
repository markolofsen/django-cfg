"""
Optional Twilio imports.

Makes twilio and sendgrid imports optional for testing and when not using Twilio functionality.
"""

# Third-party imports (optional - only required when using Twilio functionality)
try:
    from twilio.base.exceptions import TwilioException
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    Client = None  # type: ignore
    TwilioException = Exception  # Fallback to base exception
    TWILIO_AVAILABLE = False

try:
    from sendgrid import SendGridAPIClient
    SENDGRID_AVAILABLE = True
except ImportError:
    SendGridAPIClient = None  # type: ignore
    SENDGRID_AVAILABLE = False

__all__ = [
    'Client',
    'TwilioException',
    'SendGridAPIClient',
    'TWILIO_AVAILABLE',
    'SENDGRID_AVAILABLE',
]
