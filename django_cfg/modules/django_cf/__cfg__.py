"""
Cloudflare module configuration.

Add to djangoconfig.py:

    from django_cfg.modules.django_cf import CloudflareConfig

    class MyConfig(DjangoConfig):
        cloudflare: CloudflareConfig = CloudflareConfig(
            enabled=True,
            account_id="${CF_ACCOUNT_ID}",
            api_token="${CF_API_TOKEN}",
            d1_database_id="${CF_D1_DATABASE_ID}",
        )
"""

from enum import Enum
from typing import Annotated

from pydantic import Field, model_validator

from django_cfg.extensions.configs.modules import BaseModuleSettings


class D1Plan(str, Enum):
    """Cloudflare D1 billing plan — determines daily usage limits."""

    FREE = "free"        # 5M reads, 100K writes per day
    PAID = "paid"        # unlimited (no enforcement)

    @property
    def read_limit(self) -> int:
        """Max rows read per day (0 = unlimited)."""
        return {self.FREE: 5_000_000, self.PAID: 0}[self]

    @property
    def write_limit(self) -> int:
        """Max rows written per day (0 = unlimited)."""
        return {self.FREE: 100_000, self.PAID: 0}[self]


class CloudflareConfig(BaseModuleSettings):
    """Configuration for the django_cf Cloudflare module."""

    name: str = "cloudflare"
    version: str = "1.0.0"
    description: str = "Cloudflare D1 integration — automatic user sync"

    # ── Credentials ──────────────────────────────────────────────────────────

    account_id: Annotated[str, Field(default="", description="Cloudflare Account ID")]
    api_token: Annotated[str, Field(default="", description="Cloudflare API token (D1:Edit)")]
    d1_database_id: Annotated[str, Field(default="", description="D1 database UUID")]

    # ── Sync behaviour ───────────────────────────────────────────────────────

    sync_users: bool = Field(
        default=True,
        description="Sync CustomUser to D1 on every save event",
    )
    sync_batch_size: Annotated[int, Field(default=500, ge=1, le=2000)] = 500

    # ── D1 plan & limits ──────────────────────────────────────────────────────

    d1_plan: D1Plan = Field(
        default=D1Plan.FREE,
        description="D1 billing plan: 'free' (5M reads, 100K writes/day) or 'paid' (unlimited)",
    )
    d1_limit_warn_pct: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Log WARNING when daily usage exceeds this % (0 = disabled). Ignored on paid plan.",
    )

    # ── Alerting ─────────────────────────────────────────────────────────────

    telegram_alerts_enabled: bool = Field(
        default=False,
        description="Send Telegram alerts on UNHANDLED_EXCEPTION / RQ_FAILURE / SLOW_QUERY (>5s)",
    )
    telegram_batch_interval_sec: int = Field(
        default=60,
        ge=10,
        description="Seconds between batched Telegram alert flushes (min 10)",
    )
    telegram_alert_on_new: bool = Field(
        default=True,
        description="Flush immediately when a new fingerprint appears (first occurrence)",
    )

    # ── Validation ───────────────────────────────────────────────────────────

    @model_validator(mode="after")
    def validate_credentials(self) -> "CloudflareConfig":
        """Raise if module is enabled but credentials are incomplete."""
        if not self.enabled:
            return self
        missing = [
            f for f in ("account_id", "api_token", "d1_database_id")
            if not getattr(self, f)
        ]
        if missing:
            raise ValueError(
                f"django_cf: enabled=True but missing required fields: {missing}. "
                f"Set via env vars CF_ACCOUNT_ID / CF_API_TOKEN / CF_D1_DATABASE_ID."
            )
        return self

    def is_ready(self) -> bool:
        """Return True when module is enabled and all credentials are set."""
        return (
            self.enabled
            and bool(self.account_id)
            and bool(self.api_token)
            and bool(self.d1_database_id)
        )


__all__ = [
    "CloudflareConfig",
]
