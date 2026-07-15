"""Referrer -> channel classification. Runs ONCE, at ingest.

Umami re-runs a 12-branch CASE of ILIKE '%...%' over domain lists on every
dashboard load. It is unindexable, and it is the reason they need 14 composite
indexes to stay afloat. We resolve the channel on write and store the answer.

Licensing note: Snowplow's referers.yml is **GPLv3** (it derives from Matomo's
SearchEngines.php), so it cannot be vendored into MIT django-cfg. The lists below
are hand-written from GA4's published source categories. Keep them that way.
"""

from __future__ import annotations

from urllib.parse import urlparse

from ..models.event import Channel

# Checked BEFORE search engines. An LLM referrer that falls through to "organic
# search" is today's most common misclassification (PostHog currently files
# perplexity.ai as Organic Search; Matomo only added an AI type in 5.5.0).
AI_DOMAINS = frozenset({
    "chatgpt.com", "chat.openai.com", "openai.com",
    "claude.ai", "perplexity.ai", "copilot.microsoft.com",
    "gemini.google.com", "bard.google.com",
    "you.com", "phind.com", "poe.com", "mistral.ai", "deepseek.com",
})

SEARCH_DOMAINS = frozenset({
    "google", "bing", "yahoo", "duckduckgo", "yandex", "baidu",
    "ecosia", "brave", "startpage", "qwant", "naver", "seznam",
})

SOCIAL_DOMAINS = frozenset({
    "facebook", "instagram", "twitter", "x.com", "t.co", "linkedin",
    "reddit", "pinterest", "tiktok", "threads", "mastodon", "bluesky",
    "vk.com", "telegram", "t.me", "discord", "news.ycombinator.com",
})

VIDEO_DOMAINS = frozenset({"youtube", "youtu.be", "vimeo", "twitch", "dailymotion"})

# GA4's live paid-search rule. Many blog posts circulate a stale version of this.
_PAID_MEDIUMS = frozenset({"cpc", "ppc", "paidsearch", "retargeting"})
_EMAIL_MEDIUMS = frozenset({"email", "e-mail", "e_mail", "newsletter"})
_AFFILIATE_MEDIUMS = frozenset({"affiliate"})


def referrer_domain(referrer: str) -> str:
    """Host of a referrer URL, minus 'www.'. Empty string when unparseable."""
    if not referrer:
        return ""
    try:
        host = (urlparse(referrer).hostname or "").lower()
    except ValueError:
        return ""
    return host[4:] if host.startswith("www.") else host


def _is_paid(medium: str) -> bool:
    # GA4: ^(.*cp.*|ppc|retargeting|paid.*)$
    return (
        medium in _PAID_MEDIUMS
        or "cp" in medium
        or medium.startswith("paid")
    )


def _matches(host: str, needles: frozenset[str]) -> bool:
    return any(n in host for n in needles)


def classify(
    *,
    referrer: str = "",
    utm_source: str = "",
    utm_medium: str = "",
    self_host: str = "",
) -> tuple[str, str]:
    """Return ``(channel, referrer_domain)``.

    UTM parameters win over the referrer header: a campaign explicitly declares
    its own channel, and the header may be stripped by the referrer policy.
    """
    host = referrer_domain(referrer)
    source = utm_source.lower().strip()
    medium = utm_medium.lower().strip()

    # Self-referral is not a referral — it is internal navigation.
    if host and self_host and host == self_host.lower():
        host = ""

    # ChatGPT appends ?utm_source=chatgpt.com, so an AI visit can arrive with no
    # referrer header at all. Match on the source too or it is undercounted.
    if source in AI_DOMAINS or (host and host in AI_DOMAINS):
        return Channel.AI, host

    if medium:
        if medium in _EMAIL_MEDIUMS:
            return Channel.EMAIL, host
        if medium in _AFFILIATE_MEDIUMS:
            return Channel.AFFILIATE, host
        if _is_paid(medium):
            paid_social = _matches(source, SOCIAL_DOMAINS) or _matches(host, SOCIAL_DOMAINS)
            return (Channel.PAID_SOCIAL if paid_social else Channel.PAID_SEARCH), host
        if medium in ("organic", "referral", "social"):
            pass  # fall through to host-based classification

    if not host:
        # No referrer, no campaign: genuinely direct.
        return (Channel.DIRECT if not source else Channel.REFERRAL), ""

    if _matches(host, SEARCH_DOMAINS):
        return Channel.ORGANIC_SEARCH, host
    if _matches(host, VIDEO_DOMAINS):
        return Channel.ORGANIC_VIDEO, host
    if _matches(host, SOCIAL_DOMAINS):
        return Channel.ORGANIC_SOCIAL, host

    return Channel.REFERRAL, host


__all__ = ["classify", "referrer_domain"]
