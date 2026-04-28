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
        - `"<app>"` (e.g. "accounts", "totp", "centrifugo") is the
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

