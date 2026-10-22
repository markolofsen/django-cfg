"""
Optional egress through an Agent Vault credential proxy.

Agent Vault keeps the real provider key and injects it on the way out, so the
process holds only a placeholder. Off by default: with no ``LLM_VAULT_PROXY_URL``
every client is built exactly as before.

Environment:

    LLM_VAULT_PROXY_URL    http://<agent-token>:@vault.example:14322
                           (colon after the token: the proxy takes an empty password)
    LLM_VAULT_PROVIDERS    comma list of providers routed through it
                           (default "openrouter"; others stay direct)
    LLM_VAULT_CA_BUNDLE    path to the vault's root CA (PEM). Required: the
                           proxy re-signs HTTPS with its own CA.

A provider listed here whose host has no service rule in the vault gets 403
from the proxy (``unmatched_host_policy=deny``), so add the rule first.
"""

import logging
import os
import ssl
from typing import Optional

logger = logging.getLogger(__name__)

ENV_PROXY_URL = "LLM_VAULT_PROXY_URL"
ENV_PROVIDERS = "LLM_VAULT_PROVIDERS"
ENV_CA_BUNDLE = "LLM_VAULT_CA_BUNDLE"
DEFAULT_PROVIDERS = "openrouter"


def vault_providers() -> frozenset:
    """Providers routed through the vault; empty when the proxy is not configured."""
    if not os.environ.get(ENV_PROXY_URL):
        return frozenset()
    raw = os.environ.get(ENV_PROVIDERS, DEFAULT_PROVIDERS)
    return frozenset(p.strip().lower() for p in raw.split(",") if p.strip())


def vault_http_client(provider: str, *, asynchronous: bool = False) -> Optional[object]:
    """Return an httpx client wired to the vault proxy, or ``None`` for a direct call.

    Built on the OpenAI SDK's own ``DefaultHttpxClient`` so the SDK's default
    timeout, connection limits and redirect behaviour are kept.
    """
    if provider.lower() not in vault_providers():
        return None

    ca_bundle = os.environ.get(ENV_CA_BUNDLE)
    if not ca_bundle:
        # Fail closed: without the CA every request would fail TLS verification,
        # and verify=False would silently drop certificate checking.
        raise RuntimeError(
            f"{ENV_PROXY_URL} is set but {ENV_CA_BUNDLE} is not: the vault proxy "
            "re-signs HTTPS and its root CA is required."
        )

    from openai import DefaultAsyncHttpxClient, DefaultHttpxClient

    cls = DefaultAsyncHttpxClient if asynchronous else DefaultHttpxClient
    logger.info("LLM provider %s routed through the credential vault proxy", provider)
    context = ssl.create_default_context(cafile=ca_bundle)
    return cls(proxy=os.environ[ENV_PROXY_URL], verify=context)


def vault_httpx_kwargs(provider: str) -> dict:
    """Keyword arguments (``proxy``, ``verify``) for a plain ``httpx.Client``.

    Empty when the provider is not routed through the vault, so
    ``httpx.Client(**vault_httpx_kwargs("openrouter"))`` is a no-op by default.
    """
    if provider.lower() not in vault_providers():
        return {}
    ca_bundle = os.environ.get(ENV_CA_BUNDLE)
    if not ca_bundle:
        raise RuntimeError(
            f"{ENV_PROXY_URL} is set but {ENV_CA_BUNDLE} is not: the vault proxy "
            "re-signs HTTPS and its root CA is required."
        )
    return {
        "proxy": os.environ[ENV_PROXY_URL],
        "verify": ssl.create_default_context(cafile=ca_bundle),
    }
