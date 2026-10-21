"""
django_cfg.startup.drf_datetime_utc — render DRF datetimes in UTC.

django-cfg sets ``REST_FRAMEWORK["DATETIME_FORMAT"] = "%Y-%m-%dT%H:%M:%SZ"``
(literal ``Z``). DRF's ``DateTimeField.to_representation`` converts an aware
value to the *active* timezone before formatting, and ``TimezoneMiddleware``
activates the visitor's zone from ``X-Timezone``. Result: local wall-clock
time labelled ``Z`` (a +08:00 visitor got every datetime 8 hours late).

Fix: render under ``timezone.override(UTC)``. Only the output path is wrapped
(``to_representation``). Input parsing (``enforce_timezone`` from
``to_internal_value``) still uses the active zone, so naive input keeps being
read as visitor-local. Fields with an explicit ``default_timezone=`` argument
keep it. Django admin, templates and non-API code are not touched.

Patching the base class makes this global for plain ``serializers.DateTimeField``
as well as ModelSerializer fields and subclasses, with no per-project changes.
"""

from __future__ import annotations

import datetime

_MARKER = "_django_cfg_utc_output"


def patch_drf_datetime_utc() -> None:
    """Idempotently wrap DateTimeField.to_representation. Called from AppConfig.ready."""
    try:
        from django.utils import timezone
        from rest_framework.fields import DateTimeField
    except Exception:
        return

    original = DateTimeField.to_representation
    if getattr(original, _MARKER, False):
        return

    def to_representation(self, value):
        with timezone.override(datetime.timezone.utc):
            return original(self, value)

    setattr(to_representation, _MARKER, True)
    to_representation.__wrapped__ = original
    to_representation.__doc__ = original.__doc__
    DateTimeField.to_representation = to_representation
