"""
TimezoneMiddleware — activates user's local timezone for each request.

Reads the X-Timezone header sent automatically by the generated TS SDK
auth interceptor (auth.gen.ts). This lets Django date/time formatting and
ORM queries use the user's local timezone without any per-view code.

X-Client-Time (ISO-8601) is parsed and attached as request.client_time.

Persistence: when an authenticated user's timezone differs from what is
stored on their profile, the field is updated via a single UPDATE query.
A 24-hour in-process cache (keyed by user_pk + tz string) prevents
hitting the DB on every request.
"""

import logging
import zoneinfo
from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils import timezone as dj_timezone

logger = logging.getLogger(__name__)

# In-process cache: {user_pk: tz_string} — refreshed when tz changes or
# process restarts. Bounded to 2000 entries to cap memory on busy workers.
_PERSISTED: dict[int, str] = {}
_PERSIST_MAX = 2000


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_header = request.META.get("HTTP_X_TIMEZONE", "").strip()
        if tz_header:
            try:
                dj_timezone.activate(zoneinfo.ZoneInfo(tz_header))
            except (zoneinfo.ZoneInfoNotFoundError, KeyError):
                tz_header = ""
                dj_timezone.deactivate()
        else:
            dj_timezone.deactivate()

        client_time_header = request.META.get("HTTP_X_CLIENT_TIME", "").strip()
        if client_time_header:
            try:
                request.client_time = datetime.fromisoformat(
                    client_time_header.replace("Z", "+00:00")
                )
            except ValueError:
                request.client_time = None
        else:
            request.client_time = None

        response = self.get_response(request)

        # Persist after response so it never delays the request.
        if tz_header:
            self._maybe_persist(request, tz_header)

        dj_timezone.deactivate()
        return response

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------

    def _maybe_persist(self, request, tz: str) -> None:
        """Save timezone to CustomUser.timezone if it changed.

        Skips unauthenticated requests and repeated writes within the
        same process lifetime (in-process dict acts as an unbounded-TTL
        cache, reset on worker restart / deploy).
        """
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            return

        uid = user.pk
        if _PERSISTED.get(uid) == tz:
            return  # already up-to-date in this process

        try:
            User = get_user_model()
            # Only write if the DB value actually differs — avoids a
            # blind UPDATE on every cold-cache hit.
            if getattr(user, "timezone", None) != tz:
                User.objects.filter(pk=uid).update(timezone=tz)
                logger.debug("timezone persisted user=%s tz=%s", uid, tz)

            # Update in-process cache regardless (avoids the getattr
            # check on every subsequent request in this worker).
            _PERSISTED[uid] = tz

            # Evict oldest half when cap reached.
            if len(_PERSISTED) > _PERSIST_MAX:
                keep = dict(list(_PERSISTED.items())[_PERSIST_MAX // 2:])
                _PERSISTED.clear()
                _PERSISTED.update(keep)

        except Exception:
            logger.warning("timezone persist failed user=%s tz=%s", uid, tz, exc_info=True)
