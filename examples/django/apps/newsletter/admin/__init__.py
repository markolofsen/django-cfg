"""
Newsletter admin interfaces using Django-CFG admin system.

Refactored admin interfaces with Material Icons and optimized queries.
"""

from .newsletter_admin import (
    EmailLogAdmin, 
    NewsletterAdmin, 
    NewsletterSubscriptionAdmin, 
    NewsletterCampaignAdmin
)
from .filters import (
    UserEmailFilter, 
    UserNameFilter, 
    HasUserFilter, 
    EmailOpenedFilter, 
    EmailClickedFilter
)
from .resources import (
    NewsletterResource, 
    NewsletterSubscriptionResource, 
    EmailLogResource
)

__all__ = [
    'EmailLogAdmin',
    'NewsletterAdmin', 
    'NewsletterSubscriptionAdmin',
    'NewsletterCampaignAdmin',
    'UserEmailFilter',
    'UserNameFilter',
    'HasUserFilter',
    'EmailOpenedFilter',
    'EmailClickedFilter',
    'NewsletterResource',
    'NewsletterSubscriptionResource',
    'EmailLogResource',
]
