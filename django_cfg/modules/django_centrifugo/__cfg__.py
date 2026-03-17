"""
django_centrifugo module configuration.

Controls D1 publish-log capture for Centrifugo events.
Add to your DjangoConfig to enable:

    from django_cfg.modules.django_centrifugo import DjangoCentrifugoModuleConfig
    # (loaded automatically — no extra INSTALLED_APPS entry needed)
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class DjangoCentrifugoModuleConfig(BaseModel):
    """Configuration for django_centrifugo D1 publish-log module."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    log_publishes: bool = True        # Log every publish call to D1
    retention_days: int = 30          # How long to keep centrifugo_logs


# Module-level settings singleton
settings = DjangoCentrifugoModuleConfig()


__all__ = ["DjangoCentrifugoModuleConfig", "settings"]
