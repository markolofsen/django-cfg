"""
Dynamic webhook providers configuration.

Uses ProviderRegistry to get available providers dynamically.
"""

from typing import Dict, Any, List
from dataclasses import dataclass
from ..providers.registry import get_provider_registry


@dataclass
class WebhookProviderInfo:
    """Webhook information for a provider."""
    name: str
    display_name: str
    signature_header: str
    signature_algorithm: str
    content_type: str = 'application/json'
    icon: str = '🔌'


# Provider webhook metadata (only what's needed for webhooks)
WEBHOOK_METADATA = {
    'nowpayments': WebhookProviderInfo(
        name='nowpayments',
        display_name='NowPayments',
        signature_header='x-nowpayments-sig',
        signature_algorithm='HMAC-SHA512',
        icon='💎'
    ),
    # 'stripe': WebhookProviderInfo(
    #     name='stripe',
    #     display_name='Stripe',
    #     signature_header='stripe-signature',
    #     signature_algorithm='HMAC-SHA256'
    # ),
    # 'cryptapi': WebhookProviderInfo(
    #     name='cryptapi',
    #     display_name='CryptAPI',
    #     signature_header='x-cryptapi-signature',
    #     signature_algorithm='HMAC-SHA256'
    # ),
    # 'cryptomus': WebhookProviderInfo(
    #     name='cryptomus',
    #     display_name='Cryptomus',
    #     signature_header='sign',
    #     signature_algorithm='HMAC-SHA256'
    # )
}


def get_supported_providers() -> List[str]:
    """Get list of supported providers from ProviderRegistry."""
    try:
        registry = get_provider_registry()
        return registry.get_available_providers()
    except Exception:
        # Fallback to providers with webhook metadata
        return list(WEBHOOK_METADATA.keys())


def get_webhook_provider_info(provider: str) -> WebhookProviderInfo:
    """Get webhook info for a specific provider."""
    if provider not in WEBHOOK_METADATA:
        # Default webhook info for unknown providers
        return WebhookProviderInfo(
            name=provider,
            display_name=provider.title(),
            signature_header='signature',
            signature_algorithm='HMAC-SHA256',
            icon='🔌'
        )
    return WEBHOOK_METADATA[provider]


def get_signature_header(provider: str) -> str:
    """Get signature header name for provider."""
    return get_webhook_provider_info(provider).signature_header


def get_signature_algorithm(provider: str) -> str:
    """Get signature algorithm for provider."""
    return get_webhook_provider_info(provider).signature_algorithm


def is_provider_supported(provider: str) -> bool:
    """Check if provider is supported (from registry)."""
    return provider in get_supported_providers()


def get_all_providers_info() -> Dict[str, Dict[str, Any]]:
    """Get all providers information as dict."""
    supported_providers = get_supported_providers()
    
    return {
        name: {
            'name': info.name,
            'display_name': info.display_name,
            'signature_header': info.signature_header,
            'signature_algorithm': info.signature_algorithm,
            'content_type': info.content_type,
            'icon': info.icon
        }
        for name in supported_providers
        for info in [get_webhook_provider_info(name)]
    }
