"""
django_centrifugo.streamlit.services.d1_query — D1CentrifugoQuery.

Thin wrapper around CentrifugoD1Service exposing Streamlit-friendly
methods. All methods return plain lists/dicts — no Pydantic models.
"""

from __future__ import annotations

from django_cfg.modules.django_cf.core import BaseD1Service


class D1CentrifugoQuery(BaseD1Service):
    """Read-only query helper for the Centrifugo Streamlit dashboard."""

    def _get_schema_statements(self) -> list[str]:
        from django_cfg.modules.django_centrifugo.events.schema import CENTRIFUGO_SCHEMA_STATEMENTS
        return CENTRIFUGO_SCHEMA_STATEMENTS

    def get_overview(self, *, hours: int = 24) -> dict:
        from django_cfg.modules.django_centrifugo.events.service import CentrifugoD1Service
        return CentrifugoD1Service().get_overview_stats(hours=hours)

    def get_publishes(
        self,
        *,
        hours: int = 24,
        limit: int = 300,
        offset: int = 0,
        channel: str | None = None,
        status: str | None = None,
    ) -> list[dict]:
        from django_cfg.modules.django_centrifugo.events.service import CentrifugoD1Service
        return CentrifugoD1Service().get_recent(
            hours=hours, limit=limit, offset=offset,
            channel=channel, status=status,
        )

    def get_channels(self, *, hours: int = 24) -> list[str]:
        from django_cfg.modules.django_centrifugo.events.service import CentrifugoD1Service
        return CentrifugoD1Service().get_channels(hours=hours)

    def get_channel_stats(self, *, hours: int = 24) -> list[dict]:
        from django_cfg.modules.django_centrifugo.events.service import CentrifugoD1Service
        return CentrifugoD1Service().get_channel_stats(hours=hours)

    def get_timeline(self, *, hours: int = 24, bucket: str = "hour") -> list[dict]:
        from django_cfg.modules.django_centrifugo.events.service import CentrifugoD1Service
        return CentrifugoD1Service().get_timeline(hours=hours, bucket=bucket)


__all__ = ["D1CentrifugoQuery"]
