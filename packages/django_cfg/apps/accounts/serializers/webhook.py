"""
Twilio Webhook Serializers

Serializers for validating and processing Twilio webhook data.
"""

from rest_framework import serializers


class TwilioWebhookSerializer(serializers.Serializer):
    """
    Serializer for Twilio webhook data.
    
    This handles both message status webhooks and verification webhooks
    from Twilio. The fields are optional because different webhook types
    send different data.
    """
    
    # Message-related fields (SMS/WhatsApp)
    MessageSid = serializers.CharField(required=False, help_text="Twilio Message SID")
    MessageStatus = serializers.CharField(required=False, help_text="Message status (sent, delivered, failed, etc.)")
    To = serializers.CharField(required=False, help_text="Recipient phone number")
    From = serializers.CharField(required=False, help_text="Sender phone number")
    Body = serializers.CharField(required=False, help_text="Message body")
    
    # Error fields
    ErrorCode = serializers.CharField(required=False, help_text="Twilio error code")
    ErrorMessage = serializers.CharField(required=False, help_text="Error message description")
    
    # Pricing fields
    Price = serializers.DecimalField(max_digits=10, decimal_places=6, required=False, help_text="Message price")
    PriceUnit = serializers.CharField(required=False, help_text="Currency code")
    
    # Verification-related fields (Verify API)
    VerificationSid = serializers.CharField(required=False, help_text="Twilio Verification SID")
    VerificationStatus = serializers.CharField(required=False, help_text="Verification status (approved, canceled, etc.)")
    Channel = serializers.CharField(required=False, help_text="Verification channel (sms, whatsapp, call)")
    
    # Timestamp fields
    DateCreated = serializers.DateTimeField(required=False, help_text="When the message was created")
    DateSent = serializers.DateTimeField(required=False, help_text="When the message was sent")
    DateUpdated = serializers.DateTimeField(required=False, help_text="When the status was last updated")
    
    # Account information
    AccountSid = serializers.CharField(required=False, help_text="Twilio Account SID")
    
    # Additional fields that might be present
    Direction = serializers.CharField(required=False, help_text="Message direction (inbound/outbound)")
    ApiVersion = serializers.CharField(required=False, help_text="Twilio API version")
    
    # Alternative field names (some webhooks use different casing)
    message_sid = serializers.CharField(required=False, help_text="Alternative field name for MessageSid")
    message_status = serializers.CharField(required=False, help_text="Alternative field name for MessageStatus")
    verification_sid = serializers.CharField(required=False, help_text="Alternative field name for VerificationSid")
    verification_status = serializers.CharField(required=False, help_text="Alternative field name for VerificationStatus")
    
    def validate(self, data):
        """
        Ensure that we have at least one of the required identifiers.
        """
        message_sid = data.get('MessageSid') or data.get('message_sid')
        verification_sid = data.get('VerificationSid') or data.get('verification_sid')
        
        if not message_sid and not verification_sid:
            raise serializers.ValidationError(
                "Either MessageSid or VerificationSid must be provided"
            )
        
        return data
    
    def to_internal_value(self, data):
        """
        Convert the webhook data to internal format.
        
        This handles the fact that Twilio webhooks are sent as form data,
        not JSON, so we need to be flexible about the input format.
        """
        if hasattr(data, 'items'):
            # Convert QueryDict or dict to regular dict
            data = dict(data.items()) if hasattr(data, 'items') else data
        
        return super().to_internal_value(data)


class TwilioWebhookResponseSerializer(serializers.Serializer):
    """Response serializer for webhook endpoints."""
    status = serializers.CharField(help_text="Processing status")
    message = serializers.CharField(required=False, help_text="Optional message")


class TwilioWebhookErrorSerializer(serializers.Serializer):
    """Error response serializer for webhook endpoints."""
    error = serializers.CharField(help_text="Error description")
    details = serializers.DictField(required=False, help_text="Additional error details")
