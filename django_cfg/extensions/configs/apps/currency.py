"""
Base configuration for currency extension.

Users extend this class in their extension's __cfg__.py:

    from django_cfg.extensions.configs.apps.currency import BaseCurrencySettings

    class CurrencySettings(BaseCurrencySettings):
        cache_ttl: int = 7200  # Override default
        crypto_enabled: bool = False

    settings = CurrencySettings()
"""

from typing import List, Literal

from pydantic import Field, computed_field

from django_cfg.modules.django_admin.icons import Icons

from .base import BaseExtensionSettings, ExtensionScheduleConfig, NavigationItem, NavigationSection


class BaseCurrencySettings(BaseExtensionSettings):
    """
    Base settings for currency extension.

    Provides currency conversion with:
    - Multiple providers (hybrid, coinpaprika)
    - Fiat and crypto support
    - Database caching of exchange rates
    - Admin interface for rate management
    - Scheduled rate updates
    """

    # === Manifest defaults ===
    name: str = "currency"
    version: str = "1.0.0"
    description: str = "Currency conversion with fiat and crypto support"
    author: str = "DjangoCFG Team"
    min_djangocfg_version: str = "1.5.0"
    django_app_label: str = "currency"
    url_prefix: str = "currency"
    url_namespace: str = "currency"

    pip_requires: List[str] = Field(
        default_factory=lambda: ["requests>=2.28.0"],
        description="Required pip packages"
    )

    # === Provider Settings ===
    default_provider: Literal["hybrid", "coinpaprika"] = Field(
        default="hybrid",
        description="Default provider for currency rates. 'hybrid' uses YFinance + CoinPaprika"
    )

    # === Cache Settings ===
    cache_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds (default: 1 hour)"
    )

    cache_backend: Literal["memory", "database", "redis"] = Field(
        default="database",
        description="Cache backend for exchange rates"
    )

    # === Fallback Settings ===
    enable_usd_fallback: bool = Field(
        default=True,
        description="Enable indirect conversion via USD when direct rate unavailable"
    )

    default_base_currency: str = Field(
        default="USD",
        description="Default base currency for conversions"
    )

    # === Crypto Support ===
    crypto_enabled: bool = Field(
        default=True,
        description="Enable cryptocurrency conversion"
    )

    # === Precision ===
    rate_precision: int = Field(
        default=8,
        description="Decimal precision for exchange rates"
    )

    fiat_precision: int = Field(
        default=2,
        description="Decimal precision for fiat currency display"
    )

    # === Logging ===
    log_conversions: bool = Field(
        default=False,
        description="Log all currency conversions"
    )

    # === Scheduled Tasks ===
    auto_update_enabled: bool = Field(
        default=True,
        description="Enable automatic rate updates"
    )

    auto_update_cron: str = Field(
        default="0 */6 * * *",
        description="Cron schedule for automatic rate updates (default: every 6 hours)"
    )

    # === Supported Currencies ===
    supported_fiat: List[str] = Field(
        default_factory=lambda: ["USD", "EUR", "GBP", "KRW", "JPY", "CNY", "RUB"],
        description="List of supported fiat currencies"
    )

    supported_crypto: List[str] = Field(
        default_factory=lambda: ["BTC", "ETH", "USDT", "USDC", "SOL", "TRX"],
        description="List of supported cryptocurrencies"
    )

    @computed_field
    @property
    def all_supported_currencies(self) -> List[str]:
        """Get all supported currencies (fiat + crypto)."""
        currencies = list(self.supported_fiat)
        if self.crypto_enabled:
            currencies.extend(self.supported_crypto)
        return currencies

    # === Admin Navigation ===
    navigation: NavigationSection = Field(
        default_factory=lambda: NavigationSection(
            title="Currency",
            icon=Icons.CURRENCY_EXCHANGE,
            collapsible=True,
            items=[
                NavigationItem(
                    title="Exchange Rates",
                    icon=Icons.CURRENCY_EXCHANGE,
                    app="currency",
                    model="exchangerate",
                ),
                NavigationItem(
                    title="Currencies",
                    icon=Icons.PAID,
                    app="currency",
                    model="currency",
                ),
                NavigationItem(
                    title="Conversion History",
                    icon=Icons.HISTORY,
                    app="currency",
                    model="conversionlog",
                ),
            ],
        ),
        description="Admin navigation section configuration"
    )

    # === Scheduled Tasks ===
    schedules: List[ExtensionScheduleConfig] = Field(
        default_factory=list,
        description="RQ scheduled tasks"
    )

    def get_rq_schedules(self) -> list:
        """Get RQ scheduled tasks for currency extension."""
        schedules = super().get_rq_schedules()

        if self.auto_update_enabled:
            schedules.append(
                ExtensionScheduleConfig(
                    task="update_exchange_rates",
                    cron=self.auto_update_cron,
                    description="Update exchange rates from providers",
                ).to_rq_schedule(self.name)
            )

        return schedules
