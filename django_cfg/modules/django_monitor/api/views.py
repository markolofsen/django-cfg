"""
django_monitor.api.views — Frontend ingest ViewSet.

POST /cfg/monitor/ingest/
- No authentication (anonymous visitors send events too)
- Rate limited by IP: 60/minute
- Accepts batch of up to 25 events
- Returns 202 Accepted
"""

from __future__ import annotations

import logging

from django_ratelimit.core import is_ratelimited
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
        # IP throttle: 60 ingest calls/minute — prevents runaway SDK loops
        if is_ratelimited(request, group="monitor_ingest", key="ip", rate="60/m", increment=True):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = IngestBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ip_address = _get_client_ip(request)
        user_id: str | None = None
        if request.user and request.user.is_authenticated:
            user_id = str(request.user.pk)

        events = serializer.validated_data["events"]
        self._forward_to_d1(request, events, ip_address, user_id)

        return Response(status=status.HTTP_202_ACCEPTED)

    def _forward_to_d1(self, request, events: list[dict], ip_address: str, user_id: str | None) -> None:
        """Forward validated events to D1 via django_monitor capture."""
        from django_cfg.modules.django_monitor import is_enabled, get_service
        from django_cfg.modules.django_monitor.events.types import FrontendEventSyncData

        if not is_enabled():
            return

        try:
            service = get_service()
        except Exception:
            return

        try:
            api_url = service._get_api_url()
        except Exception:
            # Fallback: infer from the incoming request host when config not available
            scheme = "https" if request.is_secure() else "http"
            api_url = f"{scheme}://{request.get_host()}"

        batch: list = []
        for ev in events:
            try:
                batch.append(FrontendEventSyncData.from_ingest(ev, api_url, ip_address, user_id))
            except Exception:
                logger.exception("django_monitor: failed to build FrontendEventSyncData")

        if batch:
            try:
                service.push_frontend_events_batch(batch)
            except Exception:
                logger.exception("django_monitor: failed to push frontend events batch to D1")
