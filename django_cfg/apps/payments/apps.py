"""Payments app configuration."""

from django.apps import AppConfig


class PaymentsAppConfig(AppConfig):
    """Provider-agnostic payments engine (checkout, webhooks, refunds)."""

    name = "django_cfg.apps.payments"
    label = "cfg_payments"
    verbose_name = "Payments"
    default_auto_field = "django.db.models.BigAutoField"
