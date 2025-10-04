"""
NowPayments provider configuration.
"""

from pydantic import Field
from typing import Dict
from .base import BaseProviderConfig


class NowPaymentsProviderConfig(BaseProviderConfig):
    """NowPayments provider configuration."""

    provider_name: str = Field(default="nowpayments", description="Provider name")
    api_key: str = Field(default="", description="NowPayments API key")
    ipn_secret: str = Field(default="", description="NowPayments IPN secret for webhook validation")
    sandbox_mode: bool = Field(default=True, description="NowPayments sandbox mode")

    def get_provider_config(self) -> Dict[str, any]:
        """Get NowPayments-specific configuration."""
        return {
            'provider_name': self.provider_name,
            'enabled': self.enabled and bool(self.api_key.strip()),
            'api_key': self.api_key,
            'ipn_secret': self.ipn_secret,
            'sandbox_mode': self.sandbox_mode,
        }


# Future provider configs (commented out for now)
# class StripeProviderConfig(BaseProviderConfig):
#     """Stripe provider configuration."""
#
#     provider_name: str = Field(default="stripe", description="Provider name")
#     api_key: str = Field(default="", description="Stripe API key")
#     webhook_secret: str = Field(default="", description="Stripe webhook secret")
#
#     def get_provider_config(self) -> Dict[str, any]:
#         return {
#             'provider_name': self.provider_name,
#             'enabled': self.enabled and bool(self.api_key.strip()),
#             'api_key': self.api_key,
#             'webhook_secret': self.webhook_secret,
#         }


__all__ = [
    "NowPaymentsProviderConfig",
]
