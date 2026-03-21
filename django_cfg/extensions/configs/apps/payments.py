"""
Base configuration for payments extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.payments import BasePaymentsSettings

    class PaymentsSettings(BasePaymentsSettings):
        pass

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

    enabled: bool = Field(
        default=True,
        description="Enable payments system"
    )

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
