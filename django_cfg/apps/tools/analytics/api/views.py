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
    """Client address as resolved by the edge rules (core/edge.py). Used solely as hash input for the visitor id and
    never stored. Before 2.4.x it was X-Forwarded-For[0], which behind Traefik was the Cloudflare edge."""
    from django_cfg.core.edge import get_client_ip

    return get_client_ip(request)


def _resolve_user_id(request, token: str) -> int | None:
    """The authenticated user's id, or None.

    Cookie/session auth resolves through DRF as usual. A SPA that signs in with a
    bearer token has no cookie, and `sendBeacon` cannot set an Authorization
    header, so the SDK may carry the access token in the body instead. It is
    verified here by the same class that guards the API (signature, expiry,
    is_active and the sign-out cutoff) and is never stored; any failure means an
    anonymous hit, never an error.
    """
    if request.user.is_authenticated:
        return request.user.id
    if not token:
        return None
    try:
        from django_cfg.middleware.authentication import JWTAuthenticationWithLastLogin

        backend = JWTAuthenticationWithLastLogin()
        user = backend.get_user(backend.get_validated_token(token.encode()))
        return user.id if user is not None and user.is_active else None
    except Exception:
        return None


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
        user_id = _resolve_user_id(request, data.get("auth", "")) if config.store_user_id else None

        try:
            written = ingest_batch(
                site=site,
                events=data["events"],
                ip=_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                # Resolves because authentication stays enabled. This is the line
                # django_monitor cannot have.
                user_id=user_id,
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
