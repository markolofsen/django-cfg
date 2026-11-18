"""Tab callbacks and the two POST endpoints of the MCP tab.

The endpoints answer only active staff (anyone else: 404, as the dashboard
does), only on POST, behind Django's CSRF check (the session is the
credential, so a cross-site form must not be able to read a key). The JSON
carries ``Cache-Control: no-store``. Nothing here logs a key: the audit line
names the user id and the profile, never the value.
"""

from __future__ import annotations

import logging

from django.http import Http404, JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from . import mcp_connect, module_status

logger = logging.getLogger(__name__)


def _config():
    from django_cfg.core.state import get_current_config

    return get_current_config()


def _base(request) -> str:
    return "django_overview/iframe_base.html" if request.GET.get("iframe") == "1" else "django_dashboard/base.html"


def mcp_tab(request) -> dict:
    config = _config()
    mcp = mcp_connect.enabled_mcp(config)
    return {
        "overview_base": _base(request),
        "mcp_enabled": mcp is not None,
        "profiles": mcp_connect.profiles_for(request, config),
        "key_header": mcp_connect.KEY_HEADER,
    }


def modules_tab(request) -> dict:
    return {"overview_base": _base(request), "modules": module_status.collect(_config())}


def _staff_only(request) -> None:
    user = request.user
    if not (user.is_authenticated and user.is_active and user.is_staff):
        raise Http404


def _no_store(payload: dict, status: int = 200) -> JsonResponse:
    response = JsonResponse(payload, status=status)
    response["Cache-Control"] = "no-store, private"
    response["Pragma"] = "no-cache"
    response["X-Content-Type-Options"] = "nosniff"
    return response


@never_cache
@csrf_protect
@require_POST
def reveal_credential(request, profile: str):
    """The real key and commands for the signed-in admin on one profile."""
    _staff_only(request)
    payload = mcp_connect.reveal_payload(request, _config(), profile)
    if payload is None:
        return _no_store({"detail": "No key you may see on this profile."}, status=404)
    logger.info("Overview: MCP %s key of profile %r revealed to user id %s", payload["kind"], profile, request.user.pk)
    return _no_store(payload)


@never_cache
@csrf_protect
@require_POST
def create_credential(request, profile: str):
    """Create the admin's own ``UserAPIKey`` when they have none, then answer like reveal."""
    _staff_only(request)
    config = _config()
    mcp = mcp_connect.enabled_mcp(config)
    target = (getattr(mcp, "profiles", None) or {}).get(profile) if mcp else None
    if target is None or not mcp_connect._takes_user_keys(target):
        return _no_store({"detail": "This profile does not take personal keys."}, status=404)
    from django_cfg.apps.system.accounts.models import UserAPIKey

    UserAPIKey.objects.for_user(request.user)  # idempotent: an existing key is returned unchanged
    logger.info("Overview: personal API key ensured for user id %s (profile %r)", request.user.pk, profile)
    payload = mcp_connect.reveal_payload(request, config, profile)
    if payload is None:
        return _no_store({"detail": "The key was created but this profile does not accept it."}, status=409)
    return _no_store(payload)
