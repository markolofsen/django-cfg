"""
DRF URLs for newsletter application.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'cfg_newsletter'

# DRF API URLs
api_urlpatterns = [
    # Newsletters
    path('newsletters/', views.NewsletterListView.as_view(), name='newsletter-list'),
    path('newsletters/<int:pk>/', views.NewsletterDetailView.as_view(), name='newsletter-detail'),
    
    # Subscriptions
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('unsubscribe/', views.UnsubscribeView.as_view(), name='unsubscribe'),
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscription-list'),
    
    # Campaigns
    path('campaigns/', views.NewsletterCampaignListView.as_view(), name='campaign-list'),
    path('campaigns/<int:pk>/', views.NewsletterCampaignDetailView.as_view(), name='campaign-detail'),
    path('campaigns/send/', views.SendCampaignView.as_view(), name='send-campaign'),
    
    # Email operations
    path('test/', views.TestEmailView.as_view(), name='test-email'),
    path('bulk/', views.BulkEmailView.as_view(), name='bulk-email'),
    
    # Logs
    path('logs/', views.EmailLogListView.as_view(), name='email-logs'),
]

urlpatterns = [
    path('', include(api_urlpatterns)),
    
    # Tracking endpoints (no auth required) - accept any string to handle invalid UUIDs gracefully
    path('track/open/<str:email_log_id>/', views.TrackEmailOpenView.as_view(), name='track-open'),
    path('track/click/<str:email_log_id>/', views.TrackEmailClickView.as_view(), name='track-click'),
]
