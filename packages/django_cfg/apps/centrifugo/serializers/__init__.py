"""
Serializers for Centrifugo module.
"""

from .admin_api import (
    CentrifugoChannelsRequest,
    CentrifugoChannelsResponse,
    CentrifugoHistoryRequest,
    CentrifugoHistoryResponse,
    CentrifugoInfoRequest,
    CentrifugoInfoResponse,
    CentrifugoPresenceRequest,
    CentrifugoPresenceResponse,
    CentrifugoPresenceStatsRequest,
    CentrifugoPresenceStatsResponse,
)
from .channels import ChannelListSerializer, ChannelStatsSerializer
from .health import HealthCheckSerializer
from .publishes import RecentPublishesSerializer
from .stats import OverviewStatsSerializer

__all__ = [
    # Monitoring API (Django logs)
    "HealthCheckSerializer",
    "OverviewStatsSerializer",
    "RecentPublishesSerializer",
    "ChannelStatsSerializer",
    "ChannelListSerializer",
    # Admin API (Centrifugo server)
    "CentrifugoInfoRequest",
    "CentrifugoInfoResponse",
    "CentrifugoChannelsRequest",
    "CentrifugoChannelsResponse",
    "CentrifugoPresenceRequest",
    "CentrifugoPresenceResponse",
    "CentrifugoPresenceStatsRequest",
    "CentrifugoPresenceStatsResponse",
    "CentrifugoHistoryRequest",
    "CentrifugoHistoryResponse",
]
