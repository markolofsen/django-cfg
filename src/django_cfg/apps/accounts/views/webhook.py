"""
Twilio Webhook Views

Handles incoming webhooks from Twilio for status updates and delivery reports.
"""

import logging
import hashlib
import hmac
import base64
from urllib.parse import urljoin
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from twilio.request_validator import RequestValidator

from django_cfg.core.config import get_current_config
from ..models import TwilioResponse, OTPSecret
from ..serializers.webhook import TwilioWebhookSerializer

logger = logging.getLogger(__name__)


class TwilioWebhookViewSet(viewsets.GenericViewSet):
    """
    Twilio Webhook ViewSet for handling delivery status and message events.
    
    This endpoint receives webhooks from Twilio for:
    - Message status updates (sent, delivered, failed, etc.)
    - Verification status updates (approved, canceled, etc.)
    - Error notifications and delivery reports
    """
    
    permission_classes = [permissions.AllowAny]  # Twilio webhooks don't use standard auth
    serializer_class = TwilioWebhookSerializer
    
    def _validate_twilio_signature(self, request):
        """
        Validate that the request came from Twilio by verifying the signature.
        
        Returns:
            bool: True if signature is valid, False otherwise
        """
        try:
            config = get_current_config()
            if not config or not hasattr(config, 'twilio') or not config.twilio:
                logger.warning("Twilio config not found - skipping signature validation")
                return True  # Allow in development if config is missing
            
            auth_token = config.twilio.auth_token.get_secret_value()
            validator = RequestValidator(auth_token)
            
            # Get the signature from headers
            signature = request.META.get('HTTP_X_TWILIO_SIGNATURE', '')
            if not signature:
                logger.warning("No Twilio signature found in headers")
                return False
            
            # Build the full URL
            url = request.build_absolute_uri()
            
            # Get POST data as dict
            post_data = dict(request.POST.items())
            
            # Validate the signature
            is_valid = validator.validate(url, post_data, signature)
            
            if not is_valid:
                logger.warning(f"Invalid Twilio signature for URL: {url}")
                
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating Twilio signature: {e}")
            return False
    
    @extend_schema(
        summary="Twilio Message Status Webhook",
        description="Receives status updates for SMS and WhatsApp messages from Twilio",
        request=TwilioWebhookSerializer,
        responses={200: "Webhook processed successfully"},
        parameters=[
            OpenApiParameter(
                name="X-Twilio-Signature",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.HEADER,
                description="Twilio signature for request validation"
            ),
        ]
    )
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=["post"], url_path="message-status")
    def message_status(self, request):
        """Handle message status webhooks from Twilio."""
        
        # Validate signature
        if not self._validate_twilio_signature(request):
            logger.warning("Invalid Twilio signature - rejecting webhook")
            return Response(
                {"error": "Invalid signature"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Parse webhook data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Invalid webhook data: {serializer.errors}")
            return Response(
                {"error": "Invalid webhook data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        webhook_data = serializer.validated_data
        message_sid = webhook_data.get('MessageSid') or webhook_data.get('message_sid')
        
        if not message_sid:
            logger.warning("No MessageSid found in webhook data")
            return Response(
                {"error": "MessageSid required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Find existing TwilioResponse or create new one
            twilio_response, created = TwilioResponse.objects.get_or_create(
                message_sid=message_sid,
                defaults={
                    'response_type': 'webhook_status',
                    'service_type': self._detect_service_type(webhook_data),
                    'status': webhook_data.get('MessageStatus', ''),
                    'to_number': webhook_data.get('To', ''),
                    'from_number': webhook_data.get('From', ''),
                    'error_code': webhook_data.get('ErrorCode', ''),
                    'error_message': webhook_data.get('ErrorMessage', ''),
                    'response_data': webhook_data,
                }
            )
            
            if not created:
                # Update existing record
                twilio_response.status = webhook_data.get('MessageStatus', twilio_response.status)
                twilio_response.error_code = webhook_data.get('ErrorCode', twilio_response.error_code)
                twilio_response.error_message = webhook_data.get('ErrorMessage', twilio_response.error_message)
                twilio_response.response_data.update(webhook_data)
                twilio_response.save(update_fields=['status', 'error_code', 'error_message', 'response_data', 'updated_at'])
            
            logger.info(f"Processed message status webhook for {message_sid}: {webhook_data.get('MessageStatus')}")
            
            return Response({"status": "processed"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing message status webhook: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        summary="Twilio Verification Status Webhook",
        description="Receives status updates for Verify API verifications from Twilio",
        request=TwilioWebhookSerializer,
        responses={200: "Webhook processed successfully"}
    )
    @method_decorator(csrf_exempt)
    @action(detail=False, methods=["post"], url_path="verification-status")
    def verification_status(self, request):
        """Handle verification status webhooks from Twilio Verify API."""
        
        # Validate signature
        if not self._validate_twilio_signature(request):
            return Response(
                {"error": "Invalid signature"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Parse webhook data
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid webhook data", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        webhook_data = serializer.validated_data
        verification_sid = webhook_data.get('VerificationSid') or webhook_data.get('verification_sid')
        
        if not verification_sid:
            return Response(
                {"error": "VerificationSid required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Find existing TwilioResponse or create new one
            twilio_response, created = TwilioResponse.objects.get_or_create(
                verification_sid=verification_sid,
                defaults={
                    'response_type': 'webhook_status',
                    'service_type': 'verify',
                    'status': webhook_data.get('VerificationStatus', ''),
                    'to_number': webhook_data.get('To', ''),
                    'response_data': webhook_data,
                }
            )
            
            if not created:
                # Update existing record
                twilio_response.status = webhook_data.get('VerificationStatus', twilio_response.status)
                twilio_response.response_data.update(webhook_data)
                twilio_response.save(update_fields=['status', 'response_data', 'updated_at'])
            
            logger.info(f"Processed verification status webhook for {verification_sid}: {webhook_data.get('VerificationStatus')}")
            
            return Response({"status": "processed"}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error processing verification status webhook: {e}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _detect_service_type(self, webhook_data):
        """Detect service type from webhook data."""
        from_number = webhook_data.get('From', '')
        
        if 'whatsapp:' in from_number:
            return 'whatsapp'
        elif webhook_data.get('VerificationSid'):
            return 'verify'
        else:
            return 'sms'


# Legacy function-based view for compatibility
@csrf_exempt
@require_POST
def twilio_webhook_legacy(request):
    """
    Legacy webhook endpoint for backward compatibility.
    
    This is a simple function-based view that can be used if the
    ViewSet approach doesn't work with your URL configuration.
    """
    try:
        # Basic processing - just log the webhook
        webhook_data = dict(request.POST.items())
        message_sid = webhook_data.get('MessageSid')
        status_value = webhook_data.get('MessageStatus')
        
        logger.info(f"Legacy webhook received - MessageSid: {message_sid}, Status: {status_value}")
        
        # You can add more processing here if needed
        
        return HttpResponse("OK", status=200)
        
    except Exception as e:
        logger.error(f"Error in legacy webhook: {e}")
        return HttpResponse("Error", status=500)
