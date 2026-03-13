"""
Frontend Monitor ingest ViewSet.

POST /cfg/frontend-monitor/ingest/
- No authentication required (anonymous visitors send events too)
- Rate limited by IP: 100 requests/minute
- Accepts a batch of up to 50 events
- Returns 202 Accepted (no body)
"""

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django_cfg.apps.system.frontend_monitor.api.serializers.ingest import IngestBatchSerializer
from django_cfg.apps.system.frontend_monitor.services.ingest import IngestService
from django_cfg.core.decorators.rate_limit import rate_limit
from django_cfg.middleware.admin_notifications import get_client_ip

logger = logging.getLogger(__name__)


class FrontendMonitorViewSet(viewsets.GenericViewSet):
    """
    Ingest endpoint for browser-side errors, logs, and metrics.

    Designed to be called by a lightweight JS/TS client on the frontend.
    Supports both authenticated and anonymous visitors.
    """

    permission_classes = [AllowAny]
    authentication_classes = []  # Skip JWT/session auth overhead for public ingest

    @extend_schema(
        request=IngestBatchSerializer,
        responses={202: OpenApiResponse(description="Accepted")},
        summary="Ingest browser events",
        description="Accepts a batch of up to 50 frontend events. No authentication required.",
    )
    @action(detail=False, methods=["post"], url_path="ingest")
    @rate_limit(key="ip", rate="100/minute")
    def ingest(self, request):
        """
        Accepts a batch of frontend events.

        Request body:
            {"events": [{...}, {...}]}

        Response:
            202 Accepted (empty body)
        """
        serializer = IngestBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        ip_address = get_client_ip(request)
        user = request.user if request.user and request.user.is_authenticated else None
        events = serializer.validated_data["events"]

        try:
            IngestService().ingest_batch(events, ip_address, user)
        except Exception:
            logger.exception("Frontend monitor: unhandled error in ingest")
            # Still return 202 — client should not retry on server errors
            # (retrying would cause duplicate spam)

        return Response(status=status.HTTP_202_ACCEPTED)
