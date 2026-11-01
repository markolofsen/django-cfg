"""Provider registry: id -> provider. The providers view, URL builder and serializers all read this."""

from __future__ import annotations

from typing import Dict, List, Optional

from .base import OAuthProvider
from .github import GitHubProvider
from .google import GoogleProvider

# Order is the order buttons are shown in.
_PROVIDERS: Dict[str, OAuthProvider] = {p.id: p for p in (GitHubProvider(), GoogleProvider())}


def all_providers() -> List[OAuthProvider]:
    return list(_PROVIDERS.values())


def get_provider(provider_id: str) -> Optional[OAuthProvider]:
    return _PROVIDERS.get(provider_id)


def enabled_providers() -> List[OAuthProvider]:
    return [p for p in _PROVIDERS.values() if p.is_enabled()]
