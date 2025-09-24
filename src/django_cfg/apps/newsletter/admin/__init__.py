"""
Admin configuration for Newsletter app.
"""

from .newsletter_admin import EmailLogAdmin, NewsletterAdmin, NewsletterSubscriptionAdmin, NewsletterCampaignAdmin

__all__ = [
    'EmailLogAdmin',
    'NewsletterAdmin', 
    'NewsletterSubscriptionAdmin',
    'NewsletterCampaignAdmin',
]
