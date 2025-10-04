"""
Lead Views - API views for Lead model.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import Lead
from .serializers import (
    LeadSubmissionSerializer, 
    LeadSubmissionResponseSerializer, 
    LeadSubmissionErrorSerializer
)


class LeadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Lead model.
    
    Provides only submission functionality for leads from frontend forms.
    """
    queryset = Lead.objects.all()
    serializer_class = LeadSubmissionSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Submit Lead Form",
        description="Submit a new lead from frontend contact form with automatic Telegram notifications.",
        request=LeadSubmissionSerializer,
        responses={
            201: LeadSubmissionResponseSerializer,
            400: LeadSubmissionErrorSerializer
        },
        tags=["Lead Submission"],
        examples=[
            OpenApiExample(
                "Contact Form Submission",
                value={
                    "name": "John Doe",
                    "email": "john@example.com",
                    "company": "Tech Corp",
                    "company_site": "https://techcorp.com",
                    "contact_type": "email",
                    "contact_value": "john@example.com",
                    "subject": "Partnership Inquiry",
                    "message": "I'm interested in discussing a potential partnership.",
                    "site_url": "https://mysite.com/contact"
                },
                request_only=True,
                status_codes=["201"]
            )
        ]
    )
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def submit(self, request):
        """Submit a new lead from frontend form."""
        serializer = LeadSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            # Get client IP and user agent
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Create lead with metadata
            lead_data = serializer.validated_data
            lead_data.update({
                'ip_address': ip_address,
                'user_agent': user_agent,
                'status': Lead.StatusChoices.NEW
            })
            
            lead = Lead.objects.create(**lead_data)
            
            return Response({
                'success': True,
                'message': 'Lead submitted successfully',
                'lead_id': lead.id
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'error': 'Invalid data',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
