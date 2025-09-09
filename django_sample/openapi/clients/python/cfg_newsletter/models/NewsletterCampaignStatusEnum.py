from enum import Enum


class NewsletterCampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
