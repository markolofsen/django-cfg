"""System checks for `config.admin_access`.

django_cfg.W011  Production with the admin at the default `/admin/`: every
                 scanner on the internet tries that path first. Set an
                 unguessable `admin_access.path`.
django_cfg.W012  `admin_access` asks for something the URLconf does not do (a
                 custom path, or enabled=False) while the admin is still
                 mounted elsewhere, typically a hard-coded
                 `path("admin/", admin.site.urls)`. Setting the env var alone
                 would otherwise look like a fix and change nothing.

Both are warnings: existing projects keep starting unchanged. W011 becomes an
error in a later release.
"""

from __future__ import annotations

from django.core.checks import Tags, Warning, register
from django.urls import get_script_prefix

from django_cfg.core.admin_access import get_admin_access, get_mounted_admin_prefix
from django_cfg.models.django.admin_access import DEFAULT_ADMIN_PATH

_WIRING_HINT = (
    "In urls.py replace `path(\"admin/\", admin.site.urls)` with "
    "`*admin_urlpatterns()` (from django_cfg import admin_urlpatterns)."
)


@register(Tags.security)
def check_admin_access(app_configs, **kwargs):
    from django_cfg.core.state.registry import get_current_config

    config = get_current_config()
    if config is None:
        return []

    access = get_admin_access()
    mounted = get_mounted_admin_prefix()
    mounted_path = mounted[len(get_script_prefix()):] if mounted else None
    problems = []

    # What actually answers requests wins over what the config says. A disabled
    # admin is 404ed by AdminAccessMiddleware even if a route is still mounted.
    effective = mounted_path if mounted_path is not None else access.path

    if access.enabled and not config.debug and effective == DEFAULT_ADMIN_PATH:
        problems.append(
            Warning(
                "The Django admin is served at the default /admin/ in production.",
                hint=(
                    "Set admin_access.path (env ADMIN_ACCESS__PATH) to an unguessable value, e.g. "
                    "python -c \"import secrets; print(secrets.token_urlsafe(16) + '/')\". "
                    "This warning becomes an error in a later release. " + _WIRING_HINT
                ),
                id="django_cfg.W011",
            )
        )

    # Only an explicit request counts: the default config leaves a hand-mounted
    # admin alone, so existing projects see no new noise.
    if mounted_path is not None and (
        not access.enabled or (not access.is_default_path and mounted_path != access.path)
    ):
        wanted = "disabled" if not access.enabled else f"at /{access.path}"
        problems.append(
            Warning(
                f"admin_access wants the admin {wanted}, but it is mounted at /{mounted_path}.",
                hint=_WIRING_HINT,
                id="django_cfg.W012",
            )
        )

    return problems
