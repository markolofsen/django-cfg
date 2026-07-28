"""The ingest endpoint. POST -> validate -> INSERT -> 202.

Two bugs in django_monitor's ingest that are deliberately NOT repeated here:

1. It sets ``authentication_classes = []``, which makes ``request.user`` always
   AnonymousUser — rendering its own user_id capture dead code. Monitor
   structurally cannot attribute an event to a logged-in user. We keep
   ``AllowAny`` (anonymous traffic must be collected) but leave authentication
   ENABLED, so request.user resolves whenever a session cookie is present.
   **User attribution is the entire differentiator; giving it up is not an option.**

2. Its docstring advertised a 50-event cap while the serializer enforced 25 —
   and the docstring is what @extend_schema ships into the OpenAPI schema and the
   generated TS client. The limit here is interpolated from the serializer.
"""

from __future__ import annotations

import logging

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..services import claimed_domain, get_analytics_config, ingest_batch, resolve_site
from .serializers import (
    MAX_BATCH_SIZE,
    AnalyticsBatchSerializer,
    AnalyticsIngestResponseSerializer,
)

logger = logging.getLogger("django_cfg.analytics")


class PlainTextJSONParser(JSONParser):
    """Parse a JSON body that arrives labelled text/plain.

    navigator.sendBeacon with an application/json Blob triggers a CORS preflight,
    which on page unload usually cannot complete — so the POST is never sent,
    while sendBeacon still returns true. Silent data loss, and the worst possible
    failure mode for analytics.

    text/plain IS CORS-safelisted, so a beacon sent as a raw string is delivered
    with no preflight. The body is still JSON; only the label differs — hence
    subclassing JSONParser and swapping the media type.

    Scoped to THIS view. It does not touch the global DEFAULT_PARSER_CLASSES
    (JSONParser-only, deliberately), so the OpenAPI schema and the generated
    clients stay clean.
    """

    media_type = "text/plain"


def _client_ip(request) -> str:
    """Peer address, honouring X-Forwarded-For.

    NOTE: this is only trustworthy if a proxy you control sets the header. The IP
    is used solely as hash input for the visitor id and is never stored.
    """
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or ""


class CollectView(APIView):
    """Accept a batch of analytics events."""

    permission_classes = [AllowAny]
    # authentication_classes is intentionally NOT overridden. See module docstring.

    # Additive: JSON as normal, plus beacon-compatible text/plain.
    parser_classes = [JSONParser, PlainTextJSONParser]

    @extend_schema(
        operation_id="analytics_collect",
        request=AnalyticsBatchSerializer,
        responses={202: AnalyticsIngestResponseSerializer},
        summary="Collect analytics events",
        description=(
            f"Accepts up to {MAX_BATCH_SIZE} events per request. Always returns "
            "202 — a rejected event must never surface as a client-side error, "
            "and telling a bot it was filtered only teaches its author to adjust."
        ),
    )
    def post(self, request):
        serializer = AnalyticsBatchSerializer(data=request.data)
        if not serializer.is_valid():
            # Malformed payloads are dropped, not surfaced. A 400 here would put
            # a red error in the console of every page that embeds the SDK.
            logger.debug("Analytics: invalid payload: %s", serializer.errors)
            return Response({"accepted": 0}, status=status.HTTP_202_ACCEPTED)

        data = serializer.validated_data

        # The `site` in the body is a HINT, not the truth: anyone can POST
        # {"site": "yourdomain.com"} from anywhere. Origin/Referer are forbidden
        # headers — page JavaScript cannot forge them — so when present they win.
        # The domain must still be in security_domains to resolve at all.
        domain = claimed_domain(request, fallback=data["site"])

        # Auto-provisions the site when its domain is already trusted, so
        # analytics works out of the box instead of silently discarding
        # everything until someone creates a row by hand.
        site = resolve_site(domain)
        if site is None:
            return Response({"accepted": 0}, status=status.HTTP_202_ACCEPTED)

        config = get_analytics_config()

        try:
            written = ingest_batch(
                site=site,
                events=data["events"],
                ip=_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                # Resolves because authentication stays enabled. This is the line
                # django_monitor cannot have.
                user_id=(
                    request.user.id
                    if config.store_user_id and request.user.is_authenticated
                    else None
                ),
                fast_commit=config.fast_commit,
                session_timeout_minutes=config.session_timeout_minutes,
                salt_rotation_days=config.salt_rotation_days,
            )
        except Exception:
            # Analytics must never take down the page it is measuring.
            logger.exception("Analytics ingest failed")
            return Response({"accepted": 0}, status=status.HTTP_202_ACCEPTED)

        return Response({"accepted": written}, status=status.HTTP_202_ACCEPTED)


__all__ = ["CollectView"]
