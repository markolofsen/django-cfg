"""
Webmail deep-link resolution.

Public surface::

    from django_cfg.apps.system.accounts.services.webmail import WebmailService

    link = WebmailService.resolve("user@gmail.com")
    if link:
        ...  # link.url, link.provider, link.is_search
"""

from .service import WebmailService
from .types import ProviderConfidence, ProviderSpec, WebmailLink, WebmailProvider

__all__ = [
    "WebmailService",
    "WebmailLink",
    "WebmailProvider",
    "ProviderSpec",
    "ProviderConfidence",
]
