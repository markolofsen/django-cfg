"""Re-process a stored provider webhook event by its event id."""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Replay a stored PaymentEvent (by provider event_id) through the webhook "
        "handler. Use after fixing a handler bug — the payload is already saved."
    )

    def add_arguments(self, parser):
        parser.add_argument("event_id", type=str, help="Provider event id (e.g. evt_123)")
        parser.add_argument(
            "--force", action="store_true",
            help="Re-apply even if already processed (clears processed_at first).",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.payments.services import WebhookService
        from django_cfg.apps.payments.services.webhook_service import WebhookReplayError

        try:
            message = WebhookService.replay(
                event_id=options["event_id"], force=options["force"],
            )
        except WebhookReplayError as exc:
            self.stderr.write(self.style.ERROR(str(exc)))
            return

        self.stdout.write(self.style.SUCCESS(message))
