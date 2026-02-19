"""Centrifugo service for Streamlit admin.

Provides WebSocket channel monitoring and management.
"""

from models.centrifugo import ChannelInfo, CentrifugoHealth, PublishRecord
from services.base import BaseService


class CentrifugoService(BaseService):
    """Centrifugo WebSocket service."""

    def get_health(self) -> CentrifugoHealth:
        """Get Centrifugo health status."""
        default = CentrifugoHealth(status="error", nodes=0, clients=0, channels=0)

        def fetch() -> CentrifugoHealth:
            # CentrifugoHealthCheck has status: str ("healthy"/"unhealthy")
            data = self.api.cfg_centrifugo_monitoring.centrifugo_monitor_health_retrieve()
            return CentrifugoHealth(
                status=data.status,
                nodes=0,  # Not in health check, need to get from info
                clients=0,  # Not in health check
                channels=0,  # Not in health check
                uptime=None,
            )

        return self._safe_call("get_health", fetch, default)

    def get_channels(self) -> list[ChannelInfo]:
        """Get all active channels."""

        def fetch() -> list[ChannelInfo]:
            # Get channel stats from monitoring
            data = self.api.cfg_centrifugo_monitoring.centrifugo_monitor_channels_retrieve()
            return [
                ChannelInfo(
                    name=ch.channel,
                    subscribers=0,  # ChannelStats doesn't have subscribers
                    presence=False,
                    history=False,
                    last_activity=ch.last_activity_at,
                )
                for ch in data.channels
            ]

        return self._safe_call("get_channels", fetch, [])

    def get_channel_presence(self, channel: str) -> list[dict]:
        """Get presence info for a specific channel."""

        def fetch() -> list[dict]:
            from api.generated.cfg.cfg__centrifugo__centrifugo_admin_api.models import (
                CentrifugoPresenceRequestRequest,
            )

            request = CentrifugoPresenceRequestRequest(channel=channel)
            data = self.api.cfg_centrifugo_admin_api.centrifugo_server_presence_create(
                data=request
            )
            # CentrifugoPresenceResponse has clients list
            return [
                {"client_id": c.client, "user_id": c.user}
                for c in (data.clients or [])
            ]

        return self._safe_call("get_channel_presence", fetch, [])

    def get_publishes(self, limit: int = 50) -> list[PublishRecord]:
        """Get recent publish records."""

        def fetch() -> list[PublishRecord]:
            # PaginatedPublishList has .results with Publish items
            data = self.api.cfg_centrifugo_monitoring.centrifugo_monitor_publishes_list(
                page_size=limit
            )
            return [
                PublishRecord(
                    id=p.message_id,
                    channel=p.channel,
                    data={},  # Publish model doesn't have data field
                    timestamp=p.created_at,
                )
                for p in data.results
            ]

        return self._safe_call("get_publishes", fetch, [])

    def get_server_info(self) -> dict:
        """Get Centrifugo server info."""

        def fetch() -> dict:
            data = self.api.cfg_centrifugo_admin_api.centrifugo_server_info_create()
            return {
                "version": data.version,
                "nodes": len(data.nodes) if data.nodes else 0,
                "node_info": [
                    {"name": n.name, "num_clients": n.num_clients, "num_channels": n.num_channels}
                    for n in (data.nodes or [])
                ],
            }

        return self._safe_call("get_server_info", fetch, {"version": "unknown", "nodes": 0, "node_info": []})

    def get_overview_stats(self) -> dict:
        """Get overview statistics."""

        def fetch() -> dict:
            data = self.api.cfg_centrifugo_monitoring.centrifugo_monitor_overview_retrieve()
            return {
                "total": data.total,
                "successful": data.successful,
                "failed": data.failed,
                "timeout": data.timeout,
                "success_rate": data.success_rate,
                "avg_duration_ms": data.avg_duration_ms,
                "period_hours": data.period_hours,
            }

        return self._safe_call(
            "get_overview_stats",
            fetch,
            {"total": 0, "successful": 0, "failed": 0, "timeout": 0, "success_rate": 0.0, "avg_duration_ms": 0.0, "period_hours": 24},
        )
