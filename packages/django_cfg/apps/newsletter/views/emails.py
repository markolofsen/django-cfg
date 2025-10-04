"""
Email views.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..models import EmailLog
from ..services.email_service import NewsletterEmailService
from ..serializers import TestEmailSerializer, BulkEmailSerializer, EmailLogSerializer


class TestEmailView(generics.CreateAPIView):
    """Test email sending functionality."""
    
    serializer_class = TestEmailSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Test Email Sending",
        description="Send a test email to verify mailer configuration.",
        request=TestEmailSerializer,
        responses={200: "Success", 400: "Bad Request"},
        tags=["Testing"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        subject = serializer.validated_data['subject']
        message = serializer.validated_data['message']
        
        try:
            email_service = NewsletterEmailService()
            
            result = email_service.send_bulk_email(
                recipients=[email],
                subject=subject,
                email_title=subject,
                main_text=message,
                main_html_content=f"<p>{message}</p><p>If you received this email, the mailer is working correctly!</p>"
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_response = {
                'success': False,
                'sent_count': 0,
                'failed_count': 1,
                'total_recipients': 1,
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


class BulkEmailView(generics.CreateAPIView):
    """Send bulk emails."""
    
    serializer_class = BulkEmailSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Send Bulk Email",
        description="Send bulk emails to multiple recipients using base email template.",
        request=BulkEmailSerializer,
        responses={200: "Success", 400: "Bad Request"},
        tags=["Bulk Email"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            email_service = NewsletterEmailService()
            
            result = email_service.send_bulk_email(
                recipients=serializer.validated_data['recipients'],
                subject=serializer.validated_data['subject'],
                email_title=serializer.validated_data['email_title'],
                main_text=serializer.validated_data['main_text'],
                main_html_content=serializer.validated_data.get('main_html_content', ''),
                button_text=serializer.validated_data.get('button_text', ''),
                button_url=serializer.validated_data.get('button_url', ''),
                secondary_text=serializer.validated_data.get('secondary_text', '')
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_response = {
                'success': False,
                'sent_count': 0,
                'failed_count': len(serializer.validated_data['recipients']),
                'total_recipients': len(serializer.validated_data['recipients']),
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


class EmailLogListView(generics.ListAPIView):
    """List email logs."""
    
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List Email Logs",
        description="Get a list of email sending logs.",
        responses={200: EmailLogSerializer(many=True)},
        tags=["Logs"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
