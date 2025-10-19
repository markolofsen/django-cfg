"""
Simplified payment configuration for Payments v2.0.

Only supports NowPayments provider - no complex polymorphism needed.
"""

from pydantic import BaseModel, Field


class NowPaymentsConfig(BaseModel):
    """NowPayments provider configuration."""

    api_key: str = Field(
        default="",
        description="NowPayments API key"
    )

    ipn_secret: str = Field(
        default="",
        description="NowPayments IPN secret (for webhook validation)"
    )

    sandbox: bool = Field(
        default=False,
        description="Use sandbox API for testing"
    )

    enabled: bool = Field(
        default=True,
        description="Whether NowPayments is enabled"
    )

    @property
    def api_url(self) -> str:
        """Get API base URL based on sandbox mode."""
        if self.sandbox:
            return "https://api-sandbox.nowpayments.io/v1/"
        return "https://api.nowpayments.io/v1/"

    @property
    def api_key_str(self) -> str:
        """Get API key as string."""
        return self.api_key

    @property
    def is_configured(self) -> bool:
        """Check if provider is properly configured."""
        return bool(self.api_key and self.api_key.strip())


class PaymentsConfig(BaseModel):
    """
    Main payments configuration for Payments v2.0.

    Simplified - only NowPayments is supported.
    """

    enabled: bool = Field(
        default=True,
        description="Enable payments system"
    )

    nowpayments: NowPaymentsConfig = Field(
        default_factory=NowPaymentsConfig,
        description="NowPayments provider configuration"
    )

    def get_provider_config(self, provider: str = "nowpayments") -> NowPaymentsConfig:
        """
        Get provider configuration.

        Args:
            provider: Provider name (only "nowpayments" supported)

        Returns:
            NowPaymentsConfig instance

        Raises:
            ValueError: If provider is not supported
        """
        if provider.lower() == "nowpayments":
            return self.nowpayments

        raise ValueError(f"Provider '{provider}' not supported. Only 'nowpayments' is available in v2.0.")

    @property
    def active_providers(self) -> list[str]:
        """Get list of active provider names."""
        providers = []
        if self.nowpayments.enabled and self.nowpayments.is_configured:
            providers.append("nowpayments")
        return providers

    @property
    def is_configured(self) -> bool:
        """Check if at least one provider is configured."""
        return bool(self.active_providers)

    def get_middleware_classes(self) -> list[str]:
        """
        Get middleware classes for payments module.

        Returns:
            Empty list (v2.0 doesn't use middleware)
        """
        return []
