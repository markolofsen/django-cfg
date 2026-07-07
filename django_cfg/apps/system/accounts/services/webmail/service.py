"""
WebmailService — resolve a recipient email into a webmail deep-link.

Given the address the user is logging in with, we:
  1. detect their webmail provider from the domain,
  2. resolve the sender to search for (the project's DEFAULT_FROM_EMAIL),
  3. build a URL that opens a sender-filtered search (or the inbox, as fallback).

Unknown domains (corporate mailboxes, self-hosted, etc.) resolve to ``None`` —
the frontend then shows no button. This class never does network I/O and never
raises for bad input; callers can treat a ``None`` return as "no button".
"""

from __future__ import annotations

import logging
from email.utils import parseaddr
from typing import Optional
from urllib.parse import quote

from .providers import DOMAIN_TO_PROVIDER
from .types import ProviderSpec, WebmailLink

logger = logging.getLogger(__name__)


class WebmailService:
    """Pure, stateless resolver. Use the classmethods directly."""

    @classmethod
    def resolve(cls, email: str, sender: Optional[str] = None) -> Optional[WebmailLink]:
        """
        Resolve *email* into a :class:`WebmailLink`, or ``None`` if unknown.

        Args:
            email: The recipient address the user is logging in with.
            sender: The address our login email is *from*. When omitted, we read
                ``settings.DEFAULT_FROM_EMAIL``. Used to build the ``from:`` search.

        Returns:
            A :class:`WebmailLink` for known providers, else ``None``.
        """
        domain = cls._extract_domain(email)
        if not domain:
            return None

        spec = DOMAIN_TO_PROVIDER.get(domain)
        if spec is None:
            return None

        clean_sender = cls._clean_sender(sender if sender is not None else cls._config_sender())

        return cls._build_link(spec, clean_sender)

    # -- internals ----------------------------------------------------------

    @staticmethod
    def _extract_domain(email: str) -> Optional[str]:
        """Return the lowercased domain part of *email*, or None if malformed."""
        if not email or "@" not in email:
            return None
        domain = email.rsplit("@", 1)[1].strip().lower()
        return domain or None

    @staticmethod
    def _clean_sender(raw: Optional[str]) -> Optional[str]:
        """
        Extract a bare address from a possibly display-name-wrapped sender.

        ``"Acme <no-reply@acme.com>"`` -> ``"no-reply@acme.com"``. Returns None
        if *raw* is empty or has no address — the caller then builds an
        inbox-only link (no ``from:`` to search for).
        """
        if not raw:
            return None
        _, addr = parseaddr(raw)
        addr = (addr or "").strip().lower()
        return addr or None

    @staticmethod
    def _config_sender() -> Optional[str]:
        """Read DEFAULT_FROM_EMAIL from Django settings (safe if unset)."""
        try:
            from django.conf import settings

            return getattr(settings, "DEFAULT_FROM_EMAIL", None)
        except Exception:  # pragma: no cover - settings always available in-app
            return None

    @classmethod
    def _build_link(cls, spec: ProviderSpec, sender: Optional[str]) -> WebmailLink:
        """Build the concrete URL from a spec + sender, choosing search vs inbox."""
        # Use search only when the provider supports it AND we know the sender.
        if spec.search_url_template and sender:
            encoded = quote(sender, safe="")
            url = spec.search_url_template.replace("{sender}", encoded)
            is_search = True
        else:
            url = spec.inbox_url_template.replace("{sender}", quote(sender or "", safe=""))
            is_search = False

        return WebmailLink(
            provider=spec.provider,
            provider_name=spec.label,
            url=url,
            is_search=is_search,
        )
