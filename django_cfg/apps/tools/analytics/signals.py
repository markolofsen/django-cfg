"""Server-side attribution for completed framework authentication flows."""

from __future__ import annotations

import logging

from django.dispatch import receiver

from django_cfg.apps.system.accounts.signals import user_authenticated

from .services.auth import record_successful_login

logger = logging.getLogger("django_cfg.analytics")


@receiver(user_authenticated, dispatch_uid="django_cfg.analytics.record_successful_login")
def record_authenticated_user(sender, user, request, **kwargs) -> None:  # noqa: ARG001
    """Record login attribution without ever delaying or breaking authentication."""
    try:
        record_successful_login(user=user, request=request)
    except Exception:
        logger.exception("Analytics: could not record successful login")


__all__ = ["record_authenticated_user"]
