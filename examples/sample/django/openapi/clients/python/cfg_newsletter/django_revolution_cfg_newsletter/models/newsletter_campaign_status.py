from typing import Literal, cast

NewsletterCampaignStatus = Literal["draft", "failed", "sending", "sent"]

NEWSLETTER_CAMPAIGN_STATUS_VALUES: set[NewsletterCampaignStatus] = {
    "draft",
    "failed",
    "sending",
    "sent",
}


def check_newsletter_campaign_status(value: str) -> NewsletterCampaignStatus:
    if value in NEWSLETTER_CAMPAIGN_STATUS_VALUES:
        return cast(NewsletterCampaignStatus, value)
    raise TypeError(f"Unexpected value {value!r}. Expected one of {NEWSLETTER_CAMPAIGN_STATUS_VALUES!r}")
