"""WebhookService — replay a stored provider event.

Webhooks are persisted verbatim as ``PaymentEvent`` rows before processing. If a
handler bug drops or mis-applies an event, this re-runs it from the stored
payload without needing the provider to redeliver. Re-parsing goes through the
provider so the same normalization as live delivery is used.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class WebhookReplayError(Exception):
    pass


class WebhookService:
    @staticmethod
    def replay(*, event_id: str, force: bool = False) -> str:
        """Re-process a stored ``PaymentEvent`` by its provider event id.

        Returns a human-readable status string. With ``force=True`` it clears the
        ``processed_at`` mark first so an already-handled event is re-applied
        (use when fixing a handler bug). Without it, an already-processed event
        is a no-op (the underlying handler dedupes on ``event_id``).
        """
        from django_cfg.apps.payments.models import PaymentEvent
        from django_cfg.apps.payments.services import PaymentService

        event = PaymentEvent.objects.filter(event_id=event_id).first()
        if event is None:
            raise WebhookReplayError(f"No stored event with id {event_id!r}.")

        if force and event.processed_at is not None:
            event.processed_at = None
            event.error = ""
            event.save(update_fields=["processed_at", "error"])

        # Re-parse the stored envelope through the SAME provider path live
        # delivery uses (StripeProvider.parse_event_dict) — no duplicated
        # event-map here, so replay can't drift from live.
        from django_cfg.apps.payments.providers.stripe import StripeProvider

        raw = event.payload or {}
        result = StripeProvider.parse_event_dict(raw)
        # Preserve the stored event id (parse reads it from raw, but be explicit).
        if not result.event_id:
            from dataclasses import replace

            result = replace(result, event_id=event.event_id)

        PaymentService.handle_webhook(result=result, provider_name=event.provider)
        event.refresh_from_db()
        return (
            f"replayed {event_id} ({result.event_type}) → "
            f"{'processed' if event.processed_at else 'not processed'}"
        )
