"""Which mappings exist. A project registers its own; the built-in user model has a minimal preset.

    # apps/crm/apps.py  (ready())
    from django_cfg.modules.django_notion.export import ExportField, ExportMapping, register_export

    register_export(ExportMapping(model="shop.Customer", key=ExportField("Email", "email", "email"), fields=(...)))

A project widens the user preset on purpose, by registering it again with explicit arguments:

    register_export(user_export(verified_only=False, active_within_days=None), replace=True)
"""

from __future__ import annotations

from datetime import timedelta
from typing import Dict, Optional

from .mapping import Exclusion, ExportConfigError, ExportField, ExportMapping

_registry: Dict[str, ExportMapping] = {}


def register_export(mapping: ExportMapping, *, replace: bool = False) -> ExportMapping:
    label = mapping.model.lower()
    if label in _registry and not replace:
        raise ExportConfigError(f"an export for {mapping.model} is already registered; pass replace=True to widen or change it")
    _registry[label] = mapping
    return mapping


def user_export(
    model: Optional[str] = None, *, verified_only: bool = True, active_within_days: Optional[int] = 90,
) -> ExportMapping:
    """The minimal user preset: key email; Name, Date joined, Email verified.

    Never password, tokens, sessions or staff status (``ExportMapping`` refuses those names). Always left out: staff
    and superusers, inactive and deleted accounts, addresses that are not valid. By default also left out: an
    unverified address, and an account with no login in the last 90 days. ``verified_only=False`` and
    ``active_within_days=None`` (or a larger number) widen that, and they are the project's explicit choice: the
    default sends as little personal data to a third party as possible.
    """
    if model is None:
        from django.conf import settings

        model = settings.AUTH_USER_MODEL
    exclusions = [
        Exclusion("staff or superuser", lambda u, now: bool(getattr(u, "is_staff", False) or getattr(u, "is_superuser", False))),
        Exclusion("deleted account", lambda u, now: getattr(u, "deleted_at", None) is not None),
        Exclusion("inactive account", lambda u, now: not getattr(u, "is_active", True)),
    ]
    if verified_only:
        exclusions.append(Exclusion("email not verified", lambda u, now: not getattr(u, "is_email_verified", False)))
    if active_within_days is not None:
        days = active_within_days
        exclusions.append(Exclusion(
            f"no login in {days} days",
            lambda u, now: u.last_login is None or u.last_login < now - timedelta(days=days),
        ))
    return ExportMapping(
        model=model,
        key=ExportField("Email", "email", "email"),
        fields=(
            ExportField("Name", "get_full_name", "title", transform=lambda v, u: (v or "").strip() or u.email.split("@")[0]),
            ExportField("Date joined", "date_joined", "date"),
            ExportField("Email verified", "is_email_verified", "checkbox"),
        ),
        exclusions=tuple(exclusions),
    )


def get_export(label: str) -> ExportMapping:
    """The mapping for ``app_label.Model``. The user model falls back to ``user_export()`` when nothing was registered."""
    key = label.lower()
    if key in _registry:
        return _registry[key]
    from django.conf import settings

    if key == settings.AUTH_USER_MODEL.lower():
        return user_export(settings.AUTH_USER_MODEL)
    raise ExportConfigError(
        f"no export is declared for {label}: register one with register_export(ExportMapping(...)) "
        f"(see django_cfg.modules.django_notion.export)"
    )


def clear_exports() -> None:
    """Forget every registered mapping (tests)."""
    _registry.clear()
