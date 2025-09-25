"""Contains all the data models used in inputs/outputs"""

from .bulk_email_request import BulkEmailRequest
from .email_log import EmailLog
from .email_log_status import EmailLogStatus
from .newsletter import Newsletter
from .newsletter_bulk_create_response_200 import NewsletterBulkCreateResponse200
from .newsletter_bulk_create_response_400 import NewsletterBulkCreateResponse400
from .newsletter_campaign import NewsletterCampaign
from .newsletter_campaign_request import NewsletterCampaignRequest
from .newsletter_campaign_status import NewsletterCampaignStatus
from .newsletter_campaigns_destroy_response_204 import NewsletterCampaignsDestroyResponse204
from .newsletter_campaigns_send_create_response_200 import NewsletterCampaignsSendCreateResponse200
from .newsletter_campaigns_send_create_response_400 import NewsletterCampaignsSendCreateResponse400
from .newsletter_campaigns_send_create_response_404 import NewsletterCampaignsSendCreateResponse404
from .newsletter_subscribe_create_response_201 import NewsletterSubscribeCreateResponse201
from .newsletter_subscribe_create_response_400 import NewsletterSubscribeCreateResponse400
from .newsletter_subscription import NewsletterSubscription
from .newsletter_test_create_response_200 import NewsletterTestCreateResponse200
from .newsletter_test_create_response_400 import NewsletterTestCreateResponse400
from .newsletter_unsubscribe_create_response_200 import NewsletterUnsubscribeCreateResponse200
from .newsletter_unsubscribe_create_response_404 import NewsletterUnsubscribeCreateResponse404
from .paginated_email_log_list import PaginatedEmailLogList
from .paginated_newsletter_campaign_list import PaginatedNewsletterCampaignList
from .paginated_newsletter_list import PaginatedNewsletterList
from .paginated_newsletter_subscription_list import PaginatedNewsletterSubscriptionList
from .patched_newsletter_campaign_request import PatchedNewsletterCampaignRequest
from .patched_unsubscribe_request import PatchedUnsubscribeRequest
from .send_campaign_request import SendCampaignRequest
from .subscribe_request import SubscribeRequest
from .test_email_request import TestEmailRequest
from .unsubscribe import Unsubscribe
from .unsubscribe_request import UnsubscribeRequest

__all__ = (
    "BulkEmailRequest",
    "EmailLog",
    "EmailLogStatus",
    "Newsletter",
    "NewsletterBulkCreateResponse200",
    "NewsletterBulkCreateResponse400",
    "NewsletterCampaign",
    "NewsletterCampaignRequest",
    "NewsletterCampaignsDestroyResponse204",
    "NewsletterCampaignsSendCreateResponse200",
    "NewsletterCampaignsSendCreateResponse400",
    "NewsletterCampaignsSendCreateResponse404",
    "NewsletterCampaignStatus",
    "NewsletterSubscribeCreateResponse201",
    "NewsletterSubscribeCreateResponse400",
    "NewsletterSubscription",
    "NewsletterTestCreateResponse200",
    "NewsletterTestCreateResponse400",
    "NewsletterUnsubscribeCreateResponse200",
    "NewsletterUnsubscribeCreateResponse404",
    "PaginatedEmailLogList",
    "PaginatedNewsletterCampaignList",
    "PaginatedNewsletterList",
    "PaginatedNewsletterSubscriptionList",
    "PatchedNewsletterCampaignRequest",
    "PatchedUnsubscribeRequest",
    "SendCampaignRequest",
    "SubscribeRequest",
    "TestEmailRequest",
    "Unsubscribe",
    "UnsubscribeRequest",
)
