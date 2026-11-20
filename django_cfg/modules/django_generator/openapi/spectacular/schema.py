"""
Custom AutoSchema for drf-spectacular with intelligent tagging.

Automatically determines tags based on URL paths for better API organization.
"""

import re

from drf_spectacular.openapi import AutoSchema


class PathBasedAutoSchema(AutoSchema):
    """
    AutoSchema that determines tags from URL paths instead of view names.
    
    For cfg group URLs like /cfg/accounts/..., /cfg/support/..., 
    extracts the app name from the second path segment to create precise tags.
    
    This provides better organization in generated API clients:
    - /cfg/accounts/otp/request/ → tag: "cfg__accounts"
    - /cfg/support/tickets/ → tag: "cfg__support"
    - /cfg/payments/webhooks/ → tag: "cfg__payments"
    
    The TypeScript generator will use these tags to create properly structured folders.
    """

    def get_tags(self):
        """
        Override tag determination to use path-based logic.

        For `/cfg/<app>/...` URLs we always stamp two tags:

            ["cfg", "<app>"]

        - `"cfg"` is the namespace marker — the TS resolver picks up every
          op that carries it for `cfg_*` groups (so app-side groups can
          safely match by short tag without dragging django-cfg ops in).
        - `"<app>"` (e.g. "accounts", "totp", "payments") is the
          sub-group tag — `cfg_<app>` resolves by intersecting
          `{"cfg", "<app>"}`.

        Any user-provided tags via `extend_schema(tags=[...])` win over
        this fallback (drf-spectacular calls `get_tags()` only when no
        explicit tags are set).
        """

        path = self.path

        cfg_pattern = re.compile(r"^/cfg/([^/]+)/")
        match = cfg_pattern.match(path)
        if match:
            return ["cfg", match.group(1)]

        return super().get_tags()

    def get_extensions(self):
        """Operation extensions, plus `x-realtime-invalidates` from `django_realtime.invalidated_by` markers.

        Markers on the class and on the action handler add up. The names match django_realtime.openapi
        (INVALIDATES, MARKER_ATTR); this module may not import that one.
        """
        extensions = dict(super().get_extensions() or {})
        patterns = list(extensions.get(_INVALIDATES) or ())
        view = getattr(self, "view", None)
        if view is not None:
            action = getattr(view, "action", None) or getattr(self, "method", "").lower()
            handler = getattr(view, action, None) if action else None
            for source in (type(view), handler):
                for pattern in getattr(source, _MARKER_ATTR, ()) or ():
                    if pattern not in patterns:
                        patterns.append(pattern)
        if patterns:
            extensions[_INVALIDATES] = patterns
        return extensions


_INVALIDATES = "x-realtime-invalidates"
_MARKER_ATTR = "realtime_invalidates"
