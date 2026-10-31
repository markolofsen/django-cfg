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
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import IngestBatchSerializer

logger = logging.getLogger(__name__)


class PlainTextJSONParser(JSONParser):
    """Parse a JSON body that arrives labelled text/plain.

    The devtools SDK flushes on page unload. A cross-origin unload flush CANNOT
    carry `application/json`: that type is not CORS-safelisted, so it triggers an
    OPTIONS preflight which usually cannot complete before the document dies —
    and the POST is then never sent, silently. The events lost that way are the
    ones that mattered most (whatever crashed the page).

    `text/plain` IS CORS-safelisted, so the flush is delivered with no preflight.
    The body is still JSON; only the label differs.

    Additive and scoped to THIS view: it does not touch the global
    DEFAULT_PARSER_CLASSES (JSONParser-only, deliberately), so the OpenAPI schema
    and generated clients stay clean.
    """

    media_type = "text/plain"


class AlwaysJSON(BaseContentNegotiation):
    """Answer in JSON whatever `Accept` says.

    The caller is an SDK that never reads the body. A 406 for `Accept: text/html`
    would only turn a harmless event into a lost one.
    """

    def select_parser(self, request, parsers):
        # Same rule as DRF's default: the first parser whose media type matches.
        from rest_framework.negotiation import DefaultContentNegotiation

        return DefaultContentNegotiation().select_parser(request, parsers)

    def select_renderer(self, request, renderers, format_suffix=None):
        return renderers[0], renderers[0].media_type


def _get_client_ip(request) -> str:
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


class MonitorIngestViewSet(viewsets.GenericViewSet):
    """
    Ingest endpoint for browser-side errors, logs, and metrics.

    Designed to be called by the @djangocfg/devtools JS SDK.
    Supports both authenticated and anonymous visitors.
    """

    permission_classes = [AllowAny]
    authentication_classes = []

    # The request shape. Also what the browsable-API renderer asks for through
    # get_serializer() when a browser-like client sends `Accept: text/html`:
    # without it that renderer raised an AssertionError and the response was a 500.
    serializer_class = IngestBatchSerializer
    # JSON only: a machine endpoint has no use for the HTML form renderer.
    renderer_classes = [JSONRenderer]
    content_negotiation_class = AlwaysJSON

    # text/plain is required for the SDK's page-unload flush to survive CORS.
    parser_classes = [JSONParser, PlainTextJSONParser]

    @extend_schema(
        request=IngestBatchSerializer,
        responses={202: OpenApiResponse(description="Accepted")},
        summary="Ingest browser events",
        description=(
            "Accepts a batch of up to 25 frontend events. "
            "No authentication required — anonymous visitors can send events."
        ),
        tags=["cfg_monitor"],
    )
    @action(detail=False, methods=["post"], url_path="ingest")
    def ingest(self, request):
        """Accept a batch of frontend events and store them (JSONL + alerts)."""
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

        from django_cfg.modules.django_monitor.services import ingest_frontend_events

        ingest_frontend_events(
            serializer.validated_data["events"],
            ip_address=ip_address,
            user_id=user_id,
        )

        return Response(status=status.HTTP_202_ACCEPTED)
