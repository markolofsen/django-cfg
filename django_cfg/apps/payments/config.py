"""Config accessor — resolves the host's ``PaymentsConfig`` pydantic model.

The engine reads ALL of its configuration (provider registry, currency,
Stripe secrets, seam hooks) from the ``payments`` field on the host's
``DjangoConfig``. This module is the one place that resolution happens.

Tests can bypass the pydantic config for provider selection: ``get_provider``
(and ``get_default_currency`` here) consult the plain Django settings
``PAYMENTS_PROVIDER_REGISTRY`` / ``PAYMENTS_DEFAULT_PROVIDER`` /
``PAYMENTS_DEFAULT_CURRENCY`` FIRST, so a test can inject a fake provider with
pytest-django's ``settings`` fixture without touching the config object.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django_cfg.core.state import get_current_config

if TYPE_CHECKING:
    from django_cfg.models.django.payments import PaymentsConfig


def get_payments_config() -> "PaymentsConfig":
    """Return the host's ``PaymentsConfig`` (the ``payments`` field on DjangoConfig).

    Raises ``ImproperlyConfigured`` when the app is imported without the config
    being enabled — that is always a wiring bug (the apps builder only installs
    this app when ``payments`` is set and enabled).
    """
    config = get_current_config()
    payments = getattr(config, "payments", None) if config else None
    if payments is None:
        raise ImproperlyConfigured(
            "PaymentsConfig is not enabled on DjangoConfig "
            "(set `payments = PaymentsConfig(...)`)."
        )
    return payments


def get_default_currency() -> str:
    """ISO currency used when a checkout omits one (settings override first)."""
    override = getattr(settings, "PAYMENTS_DEFAULT_CURRENCY", None)
    if override:
        return override
    return get_payments_config().default_currency
