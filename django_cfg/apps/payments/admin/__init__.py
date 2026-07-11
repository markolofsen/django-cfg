"""
Payments Admin

Export all admin classes.
"""

from django_cfg.apps.payments.admin.event_admin import (
    PaymentEventAdmin,
    payment_event_admin_config,
)
from django_cfg.apps.payments.admin.payment_admin import (
    PaymentAdmin,
    PaymentEventInline,
    payment_admin_config,
)

__all__ = [
    # Payment
    "PaymentAdmin",
    "PaymentEventInline",
    "payment_admin_config",
    # PaymentEvent
    "PaymentEventAdmin",
    "payment_event_admin_config",
]
