"""Single source of truth for where the admin is mounted.

Everything that used to assume `/admin/` (middleware, notifications, nav
fallbacks, the project's own `urls.py`) asks here instead.

Truth order for the prefix: what is actually mounted (`reverse("admin:index")`)
wins, because a project may still hard-code `path("admin/", ...)` or any other
prefix; the configured `admin_access.path` is the fallback for when no admin
route exists yet or at all.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from django.urls import URLPattern, get_script_prefix, path, reverse

if TYPE_CHECKING:
    from ..models.django.admin_access import AdminAccessConfig

# The framework's own staff-only surface (dashboard tabs, Next.js admin). It
# belongs to the admin, so it follows the same enabled / allowlist rules.
CFG_ADMIN_PREFIX = "/cfg/admin/"


def get_admin_access() -> "AdminAccessConfig":
    """The active config, or a default one (env-aware) when none is registered."""
    from ..models.django.admin_access import AdminAccessConfig
    from .state.registry import get_current_config

    config = get_current_config()
    access = getattr(config, "admin_access", None) if config is not None else None
    return access if access is not None else AdminAccessConfig()


def get_mounted_admin_prefix() -> Optional[str]:
    """`/<path>/` where the admin is actually mounted, or None if it is not."""
    try:
        url = reverse("admin:index")
    except Exception:  # noqa: BLE001 - NoReverseMatch, or a broken URLconf: never take callers down
        return None
    # An admin mounted at the root claims every URL; it cannot name a prefix.
    return None if url == get_script_prefix() else url


def get_admin_prefix() -> str:
    """Absolute URL prefix of the admin, with leading and trailing slash."""
    return get_mounted_admin_prefix() or get_script_prefix() + get_admin_access().path


def get_admin_path() -> str:
    """Admin prefix relative to the script prefix, no leading slash (`admin/`)."""
    return get_admin_prefix()[len(get_script_prefix()):]


def is_admin_path(request_path: str) -> bool:
    """True for the admin prefix itself (`/admin`) and everything below it."""
    prefix = get_admin_prefix()
    return (request_path if request_path.endswith("/") else request_path + "/").startswith(prefix)


def is_guarded_path(request_path: str) -> bool:
    """Admin or the framework's staff surface under /cfg/admin/."""
    if is_admin_path(request_path):
        return True
    return (request_path if request_path.endswith("/") else request_path + "/").startswith(
        get_script_prefix().rstrip("/") + CFG_ADMIN_PREFIX
    )


def admin_urlpatterns(site=None) -> List[URLPattern]:
    """The admin route for `urls.py`, honouring `admin_access`.

        urlpatterns = [*admin_urlpatterns(), ...]

    Returns `[]` when the admin is disabled, so it is simply not routed.
    """
    access = get_admin_access()
    if not access.enabled:
        return []
    if site is None:
        from django.contrib import admin

        site = admin.site
    return [path(access.path, site.urls)]
