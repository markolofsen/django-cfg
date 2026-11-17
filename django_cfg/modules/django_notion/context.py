"""What the request that saved the lead said about itself: page, campaign, language.

``RequestContextMiddleware`` keeps a small dict for the lifetime of one request; ``enrich`` reads it. Outside a request
(a shell, a worker) the dict is empty and nothing is added. Only attribution is kept: no cookies, no IP, no user agent.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Dict
from urllib.parse import parse_qsl, urlsplit

_ctx: ContextVar[Dict[str, Any]] = ContextVar("django_notion_request", default={})

# query parameter -> Details label
CAMPAIGN_PARAMS = {
    "utm_source": "UTM source", "utm_medium": "UTM medium", "utm_campaign": "UTM campaign",
    "utm_term": "UTM term", "utm_content": "UTM content",
    "gclid": "GCLID", "gbraid": "GBRAID", "wbraid": "WBRAID", "msclkid": "MSCLKID", "li_fat_id": "LinkedIn click ID",
}


def get() -> Dict[str, Any]:
    return _ctx.get()


def _campaign(url: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for key, value in parse_qsl(urlsplit(url).query, keep_blank_values=False):
        label = CAMPAIGN_PARAMS.get(key.lower())
        if label and value.strip() and label not in out:
            out[label] = value.strip()[:200]
    return out


def from_request(request) -> Dict[str, Any]:
    meta = request.META
    referer = (meta.get("HTTP_REFERER") or "").strip()
    page = referer if urlsplit(referer).scheme in ("http", "https") and len(referer) <= 2000 else ""
    campaign = _campaign(page) if page else {}
    campaign.update(_campaign(request.get_full_path()))
    lang = (meta.get("HTTP_ACCEPT_LANGUAGE") or "").split(",")[0].split(";")[0].strip()[:35]
    return {"page_url": page, "campaign": campaign, "locale": lang}


class RequestContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = _ctx.set(from_request(request))
        try:
            return self.get_response(request)
        finally:
            _ctx.reset(token)
