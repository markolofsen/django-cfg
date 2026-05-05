"""
TimezoneMiddleware — activates user's local timezone for each request.

Reads the X-Timezone header sent automatically by the generated TS SDK
auth interceptor (auth.gen.ts). This lets Django date/time formatting and
ORM queries use the user's local timezone without any per-view code.

X-Client-Time (ISO-8601) is parsed and attached as request.client_time.
"""

import zoneinfo
from datetime import datetime

from django.utils import timezone as dj_timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz_header = request.META.get("HTTP_X_TIMEZONE", "").strip()
        if tz_header:
            try:
                dj_timezone.activate(zoneinfo.ZoneInfo(tz_header))
            except (zoneinfo.ZoneInfoNotFoundError, KeyError):
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
        dj_timezone.deactivate()
        return response
