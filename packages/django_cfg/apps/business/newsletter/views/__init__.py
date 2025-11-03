"""
Newsletter views package.
"""

# Newsletter views
# Campaign views
from .campaigns import NewsletterCampaignDetailView, NewsletterCampaignListView, SendCampaignView

# Email views
from .emails import BulkEmailView, EmailLogListView, TestEmailView
from .newsletters import NewsletterDetailView, NewsletterListView

# Subscription views
from .subscriptions import SubscribeView, SubscriptionListView, UnsubscribeView

# Tracking views
from .tracking import TrackEmailClickView, TrackEmailOpenView

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
