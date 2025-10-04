"""
Campaign views.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..models import NewsletterCampaign
from ..serializers import NewsletterCampaignSerializer, SendCampaignSerializer


class NewsletterCampaignListView(generics.ListCreateAPIView):
    """List and create newsletter campaigns."""
    
    queryset = NewsletterCampaign.objects.all()
    serializer_class = NewsletterCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List Newsletter Campaigns",
        description="Get a list of all newsletter campaigns.",
        responses={200: NewsletterCampaignSerializer(many=True)},
        tags=["Campaigns"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Create Newsletter Campaign",
        description="Create a new newsletter campaign.",
        request=NewsletterCampaignSerializer,
        responses={201: NewsletterCampaignSerializer},
        tags=["Campaigns"]
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class NewsletterCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a newsletter campaign."""
    
    queryset = NewsletterCampaign.objects.all()
    serializer_class = NewsletterCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get Campaign Details",
        description="Retrieve details of a specific newsletter campaign.",
        responses={200: NewsletterCampaignSerializer},
        tags=["Campaigns"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update Campaign",
        description="Update a newsletter campaign.",
        request=NewsletterCampaignSerializer,
        responses={200: NewsletterCampaignSerializer},
        tags=["Campaigns"]
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)
    
    @extend_schema(
        summary="Delete Campaign",
        description="Delete a newsletter campaign.",
        responses={204: "No Content"},
        tags=["Campaigns"]
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class SendCampaignView(generics.CreateAPIView):
    """Send a newsletter campaign."""
    
    serializer_class = SendCampaignSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Send Newsletter Campaign",
        description="Send a newsletter campaign to all subscribers.",
        request=SendCampaignSerializer,
        responses={200: "Success", 400: "Bad Request", 404: "Campaign not found"},
        tags=["Campaigns"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        campaign_id = serializer.validated_data['campaign_id']
        
        try:
            campaign = NewsletterCampaign.objects.get(id=campaign_id)
            
            if campaign.status != NewsletterCampaign.CampaignStatus.DRAFT:
                return Response(
                    {'success': False, 'error': 'Campaign is not in draft status'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            success = campaign.send_campaign()
            
            if success:
                # Get updated campaign data
                campaign.refresh_from_db()
                response_data = {
                    'success': True,
                    'sent_count': campaign.recipient_count,
                    'failed_count': 0,
                    'total_recipients': campaign.recipient_count,
                    'newsletter_id': campaign.newsletter.id,
                    'newsletter_title': campaign.newsletter.title
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'success': False, 'error': 'Failed to send campaign'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except NewsletterCampaign.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Campaign not found'},
                status=status.HTTP_404_NOT_FOUND
            )
