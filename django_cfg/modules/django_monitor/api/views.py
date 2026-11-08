"""
django_monitor.api.views — Frontend ingest ViewSet.

POST /cfg/monitor/ingest/
- No authentication required (anonymous visitors send events too); a valid JWT
  in ``Authorization: Bearer`` links the events to ``request.user.pk`` (soft: any
  failure leaves the request anonymous and still 202)
- Per client address (see ``limits.client_ip``): 60 requests and 300 events a minute (429);
  the same numbers per signed-in user, so one account cannot hide behind many addresses
- Per project: 3000 events a minute; beyond it the batch is dropped, counted, and still answered 202
- Body over 64 KB: 413, before parsing
- Accepts batch of up to 25 events
- Returns 202 Accepted
"""

from __future__ import annotations

import logging

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status, viewsets
from rest_framework.authentication import BaseAuthentication
from rest_framework.decorators import action
from rest_framework.negotiation import BaseContentNegotiation
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django_cfg.modules.django_monitor import limits as _limits
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


class SoftJWTAuthentication(BaseAuthentication):
    """Identify the user from a Bearer JWT, and never refuse the request.

    The ingest endpoint must answer 202 whatever the credentials: an expired
    token in a tab that has been open all night must not turn a crash report into
    a 401. Every failure (no header, other scheme, bad or expired token, revoked
    session, deactivated user, database down)
    therefore returns ``None`` and the request stays anonymous.

    JWT only, by design: no session cookie (so no CSRF check and no ambient
    credential a third-party page could ride) and no Basic. It reuses the
    project's own JWT class, so a revoked or deactivated account is anonymous here
    exactly as it is refused elsewhere.
    """

    def authenticate(self, request):
        try:
            from django_cfg.middleware.authentication import JWTAuthenticationWithLastLogin

            return JWTAuthenticationWithLastLogin().authenticate(request)
        except Exception:
            return None

    def authenticate_header(self, request):
        return None


class MonitorIngestViewSet(viewsets.GenericViewSet):
    """
    Ingest endpoint for browser-side errors, logs, and metrics.

    Designed to be called by the @djangocfg/devtools JS SDK.
    Supports both authenticated and anonymous visitors.
    """

    permission_classes = [AllowAny]
    authentication_classes = [SoftJWTAuthentication]

    def perform_authentication(self, request):
        # Deferred: the token is checked inside ``ingest`` once the cheap limits
        # and the payload check passed, so a flood of junk costs no database read.
        pass

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
        auth=[],
        summary="Ingest browser events",
        description=(
            "Accepts a batch of up to 25 frontend events (body up to 64 KB). "
            "No authentication required — anonymous visitors can send events. "
            "A valid Bearer JWT links the events to the user's id; an invalid one is ignored."
        ),
        tags=["cfg_monitor"],
    )
    @action(detail=False, methods=["post"], url_path="ingest")
    def ingest(self, request):
        """Accept a batch of frontend events and store them (JSONL + alerts)."""
        ip_address = _limits.client_ip(request)

        # Per-client request throttle: prevents runaway SDK loops and scripts.
        if not _limits.within("req", ip_address, 1, _limits.CLIENT_REQUESTS_PER_MIN):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        # Body size is judged from the declared length before anything is parsed.
        declared = request.META.get("CONTENT_LENGTH") or ""
        if declared.isdigit() and int(declared) > _limits.MAX_BODY_BYTES:
            return Response(status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

        serializer = IngestBatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        events = serializer.validated_data["events"]
        if not _limits.within("ev", ip_address, len(events), _limits.CLIENT_EVENTS_PER_MIN):
            return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)
        # The project ceiling answers 202: a 429 would only make an honest SDK retry.
        if not _limits.within("project", "all", len(events), _limits.PROJECT_EVENTS_PER_MIN):
            _limits.record_dropped(len(events))
            return Response(status=status.HTTP_202_ACCEPTED)

        # Soft: anonymous unless a valid Bearer JWT. The primary key only (any user
        # model, int or uuid); never an e-mail or a name.
        user_id: str | None = None
        user = request.user
        if user is not None and user.is_authenticated and user.pk is not None:
            user_id = str(user.pk)
            # One noisy account must not hide behind many addresses.
            if not (
                _limits.within("ureq", user_id, 1, _limits.CLIENT_REQUESTS_PER_MIN)
                and _limits.within("uev", user_id, len(events), _limits.CLIENT_EVENTS_PER_MIN)
            ):
                return Response(status=status.HTTP_429_TOO_MANY_REQUESTS)

        from django_cfg.modules.django_monitor.services import ingest_frontend_events

        ingest_frontend_events(
            events,
            ip_address=ip_address,
            user_id=user_id,
            origin=request.META.get("HTTP_ORIGIN", ""),
        )

        return Response(status=status.HTTP_202_ACCEPTED)
