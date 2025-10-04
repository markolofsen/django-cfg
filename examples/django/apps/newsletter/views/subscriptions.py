"""
Subscription views.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from ..models import Newsletter, NewsletterSubscription
from ..serializers import (
    NewsletterSubscriptionSerializer,
    SubscribeSerializer,
    UnsubscribeSerializer,
)


class SubscribeView(generics.CreateAPIView):
    """Handle newsletter subscriptions."""
    
    serializer_class = SubscribeSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Subscribe to Newsletter",
        description="Subscribe an email address to a newsletter.",
        request=SubscribeSerializer,
        responses={201: "Created", 400: "Bad Request"},
        tags=["Subscriptions"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        newsletter_id = serializer.validated_data['newsletter_id']
        email = serializer.validated_data['email']
        
        try:
            newsletter = Newsletter.objects.get(id=newsletter_id, is_active=True)
            
            # Create or reactivate subscription
            subscription, created = NewsletterSubscription.objects.get_or_create(
                newsletter=newsletter,
                email=email,
                defaults={'is_active': True}
            )
            
            if not created and not subscription.is_active:
                # Reactivate subscription
                subscription.is_active = True
                subscription.unsubscribed_at = None
                subscription.save()
                created = True
            
            if created:
                response_data = {
                    'success': True,
                    'message': f'Successfully subscribed to {newsletter.title}',
                    'subscription_id': subscription.id
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data = {
                    'success': False,
                    'message': 'Already subscribed to this newsletter'
                }
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
                
        except Newsletter.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Newsletter not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UnsubscribeView(generics.UpdateAPIView):
    """Handle newsletter unsubscriptions."""
    
    serializer_class = UnsubscribeSerializer
    permission_classes = [AllowAny]
    
    @extend_schema(
        summary="Unsubscribe from Newsletter",
        description="Unsubscribe from a newsletter using subscription ID.",
        request=UnsubscribeSerializer,
        responses={200: "Success", 404: "Subscription not found"},
        tags=["Subscriptions"]
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        subscription_id = serializer.validated_data['subscription_id']
        
        try:
            subscription = NewsletterSubscription.objects.get(
                id=subscription_id, 
                is_active=True
            )
            
            newsletter_title = subscription.newsletter.title
            subscription.unsubscribe()
            
            response_data = {
                'success': True,
                'message': f'Successfully unsubscribed from {newsletter_title}'
            }
            return Response(response_data, status=status.HTTP_200_OK)
            
        except NewsletterSubscription.DoesNotExist:
            return Response(
                {'success': False, 'message': 'Subscription not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class SubscriptionListView(generics.ListAPIView):
    """List user's subscriptions."""
    
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return NewsletterSubscription.objects.filter(
            user=self.request.user,
            is_active=True
        )
    
    @extend_schema(
        summary="List User Subscriptions",
        description="Get a list of current user's active newsletter subscriptions.",
        responses={200: NewsletterSubscriptionSerializer(many=True)},
        tags=["Subscriptions"]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
