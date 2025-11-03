"""
Newsletter admin interfaces using Django-CFG admin system.

Refactored admin interfaces with Material Icons and optimized queries.
"""

from .newsletter_admin import (
    EmailLogAdmin,
    NewsletterAdmin,
    NewsletterCampaignAdmin,
    NewsletterSubscriptionAdmin,
)
from .filters import (
    EmailClickedFilter,
    EmailOpenedFilter,
    HasUserFilter,
    UserEmailFilter,
    UserNameFilter,
)
from .resources import EmailLogResource, NewsletterResource, NewsletterSubscriptionResource

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
