"""
django_monitor.api.views — Frontend ingest ViewSet.

POST /cfg/monitor/ingest/
- No authentication (anonymous visitors send events too)
- Rate limited by IP: 100/minute
- Accepts batch of up to 50 events
- Returns 202 Accepted
"""

from __future__ import annotations

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import IngestBatchSerializer

logger = logging.getLogger(__name__)


def _get_client_ip(request) -> str:
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class MonitorIngestViewSet(viewsets.GenericViewSet):
    """
    Ingest endpoint for browser-side errors, logs, and metrics.

    Designed to be called by the @djangocfg/monitor JS SDK.
    Supports both authenticated and anonymous visitors.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        request=IngestBatchSerializer,
        responses={202: OpenApiResponse(description="Accepted")},
        summary="Ingest browser events",
        description=(
            "Accepts a batch of up to 50 frontend events. "
            "No authentication required — anonymous visitors can send events."
        ),
        tags=["monitor"],
    )
    @action(detail=False, methods=["post"], url_path="ingest")
    def ingest(self, request):
        """Accept a batch of frontend events and forward to D1."""
        serializer = IngestBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ip_address = _get_client_ip(request)
        user_id: str | None = None
        if request.user and request.user.is_authenticated:
            user_id = str(request.user.pk)

        events = serializer.validated_data["events"]
        self._forward_to_d1(events, ip_address, user_id)

        return Response(status=status.HTTP_202_ACCEPTED)

    def _forward_to_d1(self, events: list[dict], ip_address: str, user_id: str | None) -> None:
        """Forward validated events to D1 via django_monitor capture."""
        from django_cfg.modules.django_monitor import is_enabled, get_service
        from django_cfg.modules.django_monitor.events.types import FrontendEventSyncData

        if not is_enabled():
            return

        try:
            from django_cfg import get_current_config
            cfg = get_current_config()
            api_url = cfg.api_url if cfg else ""
        except Exception:
            api_url = ""

        try:
            service = get_service()
        except Exception:
            return

        for ev in events:
            try:
                data = FrontendEventSyncData.from_ingest(ev, api_url, ip_address, user_id)
                service.push_frontend_event(data)
            except Exception:
                logger.exception("django_monitor: failed to forward frontend event to D1")
