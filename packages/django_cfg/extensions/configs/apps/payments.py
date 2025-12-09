"""
Base configuration for payments extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.payments import BasePaymentsSettings

    class PaymentsSettings(BasePaymentsSettings):
        nowpayments_api_key = "your-api-key"
        nowpayments_ipn_secret = "your-ipn-secret"

    settings = PaymentsSettings()
"""

from typing import List, Optional

from pydantic import Field, computed_field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, NavigationItem, NavigationSection


class BasePaymentsSettings(BaseExtensionSettings):
    """
    Base settings for payments extension.

    All payment configuration is now in __cfg__.py, not DjangoConfig.
    """

    # === Manifest defaults ===
    name: str = "payments"
    version: str = "2.0.0"
    description: str = "Payments v2.0 - Simplified payment system"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "payments"
    url_prefix: str = "payments"
    url_namespace: str = "payments"

    # === Payments Configuration ===
    # These fields replace DjangoConfig.payments

    enabled: bool = Field(
        default=True,
        description="Enable payments system"
    )

    # NowPayments provider settings
    nowpayments_api_key: str = Field(
        default="",
        description="NowPayments API key"
    )

    nowpayments_ipn_secret: str = Field(
        default="",
        description="NowPayments IPN secret (for webhook validation)"
    )

    nowpayments_sandbox: bool = Field(
        default=False,
        description="Use sandbox API for testing"
    )

    nowpayments_enabled: bool = Field(
        default=True,
        description="Whether NowPayments is enabled"
    )

    @computed_field
    @property
    def nowpayments_api_url(self) -> str:
        """Get API base URL based on sandbox mode."""
        if self.nowpayments_sandbox:
            return "https://api-sandbox.nowpayments.io/v1/"
        return "https://api.nowpayments.io/v1/"

    @computed_field
    @property
    def nowpayments_is_configured(self) -> bool:
        """Check if NowPayments is properly configured."""
        return bool(self.nowpayments_api_key and self.nowpayments_api_key.strip())

    @computed_field
    @property
    def active_providers(self) -> List[str]:
        """Get list of active provider names."""
        providers = []
        if self.nowpayments_enabled and self.nowpayments_is_configured:
            providers.append("nowpayments")
        return providers

    @computed_field
    @property
    def is_configured(self) -> bool:
        """Check if at least one provider is configured."""
        return bool(self.active_providers)

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Payments",
            icon=Icons.ACCOUNT_BALANCE,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Payments",
                    icon=Icons.ACCOUNT_BALANCE,
                    app="payments",
                    model="payment",
                ),
                NavigationItem(
                    title="Currencies",
                    icon=Icons.CURRENCY_BITCOIN,
                    app="payments",
                    model="currency",
                ),
                NavigationItem(
                    title="User Balances",
                    icon=Icons.ACCOUNT_BALANCE_WALLET,
                    app="payments",
                    model="userbalance",
                ),
                NavigationItem(
                    title="Transactions",
                    icon=Icons.RECEIPT_LONG,
                    app="payments",
                    model="transaction",
                ),
                NavigationItem(
                    title="Withdrawal Requests",
                    icon=Icons.DOWNLOAD,
                    app="payments",
                    model="withdrawalrequest",
                ),
            ],
        ),
    )
