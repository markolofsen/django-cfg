"""Owner resolution for API views — the request→billable-party seam.

The engine doesn't know the host's ownership model. For API requests it
resolves "whose payments are these?" like so:

1. ``PaymentsConfig.owner_resolver`` (dotted path to ``fn(request) -> owner``)
   when set — the host's own logic (active organization, team, tenant…).
2. Otherwise, if the owner model IS the user model, ``request.user``.
3. Otherwise the wiring is incomplete → ``ImproperlyConfigured``.
"""

from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from django_cfg.apps.payments.config import get_payments_config
from django_cfg.apps.payments.models import get_owner_model_name


def resolve_owner(request):
    """Return the billable owner instance for ``request`` (see module docstring)."""
    cfg = get_payments_config()
    if cfg.owner_resolver:
        resolver = import_string(cfg.owner_resolver)
        return resolver(request)

    if get_owner_model_name() == settings.AUTH_USER_MODEL:
        return request.user

    raise ImproperlyConfigured(
        "PaymentsConfig.owner_model points at a non-user model "
        f"({get_owner_model_name()!r}); set PaymentsConfig.owner_resolver to a "
        "dotted path of fn(request) -> owner so API views can scope payments."
    )
