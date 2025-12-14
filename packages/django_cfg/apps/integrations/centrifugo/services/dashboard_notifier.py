"""
Dashboard Real-time Notifications.

Publishes updates to dashboard WebSocket channel when events occur.
"""

from typing import Any
from django_cfg.utils import get_logger

logger = get_logger("centrifugo")

# Dashboard channel for real-time updates
DASHBOARD_CHANNEL = "centrifugo#dashboard"

# Centrifugo Wrapper API endpoints
WRAPPER_PUBLISH_ENDPOINT = "/api/publish"


class DashboardNotifier:
    """
    Service for publishing real-time updates to Centrifugo dashboard.

    Publishes notifications when:
    - New publish is created
    - Publish status changes (success/failure/timeout)
    - Statistics need to be refreshed
    """

    @staticmethod
    async def notify_new_publish(log_entry: Any) -> None:
        """
        Notify dashboard about new publish.

        Args:
            log_entry: CentrifugoLog instance
        """
        if not log_entry:
            return

        try:
            import httpx
            from .config_helper import get_centrifugo_config

            config = get_centrifugo_config()
            if not config or not config.enabled:
                return

            data = {
                "type": "new_publish",
                "publish": {
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "status": log_entry.status,
                    "wait_for_ack": log_entry.wait_for_ack,
                    "created_at": log_entry.created_at.isoformat(),
                }
            }

            # Direct wrapper call WITHOUT logging to avoid recursion
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{config.wrapper_url}{WRAPPER_PUBLISH_ENDPOINT}",
                    json={
                        "channel": DASHBOARD_CHANNEL,
                        "data": data,
                        "wait_for_ack": False,
                        "ack_timeout": 0,
                    }
                )

            logger.debug(f"📊 Dashboard notified: new publish {log_entry.message_id}")

        except Exception as e:
            logger.debug(f"Dashboard notification failed: {e}")

    @staticmethod
    async def notify_status_change(log_entry: Any, old_status: str = None) -> None:
        """
        Notify dashboard about publish status change.

        Args:
            log_entry: CentrifugoLog instance
            old_status: Previous status (optional)
        """
        if not log_entry:
            return

        try:
            import httpx
            from .config_helper import get_centrifugo_config

            config = get_centrifugo_config()
            if not config or not config.enabled:
                return

            data = {
                "type": "status_change",
                "publish": {
                    "message_id": log_entry.message_id,
                    "channel": log_entry.channel,
                    "status": log_entry.status,
                    "old_status": old_status,
                    "acks_received": log_entry.acks_received,
                    "duration_ms": log_entry.duration_ms,
                    "completed_at": log_entry.completed_at.isoformat() if log_entry.completed_at else None,
                }
            }

            # Direct wrapper call WITHOUT logging to avoid recursion
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{config.wrapper_url}{WRAPPER_PUBLISH_ENDPOINT}",
                    json={
                        "channel": DASHBOARD_CHANNEL,
                        "data": data,
                        "wait_for_ack": False,
                        "ack_timeout": 0,
                    }
                )

            logger.debug(f"📊 Dashboard notified: status change {log_entry.message_id} -> {log_entry.status}")

        except Exception as e:
            logger.debug(f"Dashboard notification failed: {e}")

    @staticmethod
    async def notify_stats_update() -> None:
        """
        Notify dashboard to refresh statistics.

        Triggers a full stats refresh on the dashboard.
        """
        try:
            from .client import CentrifugoClient

            client = CentrifugoClient()

            data = {
                "type": "stats_update",
                "action": "refresh",
            }

            await client.publish(
                channel=DASHBOARD_CHANNEL,
                data=data,
            )

            logger.debug("📊 Dashboard notified: refresh stats")

        except Exception as e:
            logger.warning(f"Failed to notify dashboard about stats update: {e}")


__all__ = [
    "DashboardNotifier",
    "DASHBOARD_CHANNEL",
]
