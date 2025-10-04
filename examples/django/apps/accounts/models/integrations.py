"""
Third-party integrations models (Twilio, etc.).
"""

from django.db import models

from .choices import TwilioResponseType, TwilioServiceType


class TwilioResponse(models.Model):
    """Model for storing Twilio API responses and webhook data."""
    
    response_type = models.CharField(max_length=20, choices=TwilioResponseType.choices)
    service_type = models.CharField(max_length=10, choices=TwilioServiceType.choices)
    
    # Twilio identifiers
    message_sid = models.CharField(max_length=34, blank=True, help_text="Twilio Message SID")
    verification_sid = models.CharField(max_length=34, blank=True, help_text="Twilio Verification SID")
    
    # Request/Response data
    request_data = models.JSONField(default=dict, help_text="Original request parameters")
    response_data = models.JSONField(default=dict, help_text="Twilio API response")
    
    # Status and error handling
    status = models.CharField(max_length=20, blank=True, help_text="Message/Verification status")
    error_code = models.CharField(max_length=10, blank=True, help_text="Twilio error code")
    error_message = models.TextField(blank=True, help_text="Error description")
    
    # Contact information
    to_number = models.CharField(max_length=20, blank=True, help_text="Recipient phone/email")
    from_number = models.CharField(max_length=20, blank=True, help_text="Sender phone/email")
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    price_unit = models.CharField(max_length=3, blank=True, help_text="Currency code")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    twilio_created_at = models.DateTimeField(null=True, blank=True, help_text="Timestamp from Twilio")
    
    # Relations
    otp_secret = models.ForeignKey(
        'OTPSecret', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='twilio_responses',
        help_text="Related OTP if applicable"
    )
    
    class Meta:
        app_label = 'django_cfg_accounts'
        verbose_name = 'Twilio Response'
        verbose_name_plural = 'Twilio Responses'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['message_sid']),
            models.Index(fields=['verification_sid']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['response_type', 'service_type']),
        ]
    
    def __str__(self):
        return f"{self.get_response_type_display()} - {self.get_service_type_display()}"
    
    @property
    def has_error(self):
        """Check if response has error."""
        return bool(self.error_code or self.error_message)
    
    @property
    def is_successful(self):
        """Check if response is successful."""
        return not self.has_error and self.status in ['sent', 'delivered', 'approved']
