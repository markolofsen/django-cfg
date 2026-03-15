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

from typing import Annotated

from pydantic import Field, model_validator

from django_cfg.extensions.configs.modules import BaseModuleSettings


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

    # ── Alerting ─────────────────────────────────────────────────────────────

    telegram_alerts_enabled: bool = Field(
        default=False,
        description="Send Telegram alerts on UNHANDLED_EXCEPTION / RQ_FAILURE / SLOW_QUERY (>5s)",
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
