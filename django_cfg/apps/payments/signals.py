"""Payment lifecycle signals — the host's zero-config fulfillment surface.

Emitted by the service layer regardless of whether a ``fulfillment_hook`` is
configured, so hosts can wire receivers instead of (or in addition to) the
dotted-path hook:

    from django_cfg.apps.payments.signals import payment_succeeded

    @receiver(payment_succeeded)
    def on_paid(sender, payment, **kwargs):
        ...

Both signals send ``sender=Payment`` with a ``payment`` kwarg. Receiver
exceptions propagate into the webhook handler's record-and-retry path (unlike
the fulfillment hook, which is swallowed after being recorded on the event).
"""

import django.dispatch

#: Sent when a payment reaches SUCCEEDED (webhook- or reconciliation-driven).
payment_succeeded = django.dispatch.Signal()

#: Sent when a payment reaches FAILED (webhook- or reconciliation-driven).
payment_failed = django.dispatch.Signal()

__all__ = ["payment_succeeded", "payment_failed"]
