"""
Newsletter views package.
"""

# Newsletter views
from .newsletters import NewsletterListView, NewsletterDetailView

# Subscription views  
from .subscriptions import SubscribeView, UnsubscribeView, SubscriptionListView

# Campaign views
from .campaigns import (
    NewsletterCampaignListView, 
    NewsletterCampaignDetailView, 
    SendCampaignView
)

# Email views
from .emails import TestEmailView, BulkEmailView, EmailLogListView

# Tracking views
from .tracking import TrackEmailOpenView, TrackEmailClickView

__all__ = [
    # Newsletters
    'NewsletterListView',
    'NewsletterDetailView',
    
    # Subscriptions
    'SubscribeView', 
    'UnsubscribeView',
    'SubscriptionListView',
    
    # Campaigns
    'NewsletterCampaignListView',
    'NewsletterCampaignDetailView', 
    'SendCampaignView',
    
    # Emails
    'TestEmailView',
    'BulkEmailView', 
    'EmailLogListView',
    
    # Tracking
    'TrackEmailOpenView',
    'TrackEmailClickView',
]
