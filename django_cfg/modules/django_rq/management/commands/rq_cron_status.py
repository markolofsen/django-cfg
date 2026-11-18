"""
Cron-vs-worker status; exits 1 when not ok (usable as a compose healthcheck).

Example:
    python manage.py rq_cron_status
    python manage.py rq_cron_status --queue high --max-wait 60 --json
"""

import json
import sys

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Tell 'rqcron dead' from 'worker busy/starved'; exit 1 when not ok"

    def add_arguments(self, parser):
        parser.add_argument("--queue", action="append", dest="queues",
                            help="Queue to judge (repeatable; default: all)")
        parser.add_argument("--max-heartbeat-age", type=float, default=120.0,
                            help="Seconds without an rqcron heartbeat before 'cron_dead'")
        parser.add_argument("--max-wait", type=float, default=120.0,
                            help="Seconds a queued job may wait before 'starved'")
        parser.add_argument("--json", action="store_true", help="Print JSON")

    def handle(self, *args, **options):
        from django_cfg.modules.django_rq.health.status import UnknownQueueError, cron_status

        try:
            st = cron_status(
                queue_names=options["queues"],
                max_heartbeat_age=options["max_heartbeat_age"],
                max_wait=options["max_wait"],
            )
        except UnknownQueueError as e:
            # CommandError: one line on stderr, exit 1, no traceback.
            raise CommandError(str(e)) from None
        if options["json"]:
            self.stdout.write(json.dumps(st.as_dict(), default=str))
        else:
            hb = "n/a" if st.heartbeat_age_sec is None else f"{st.heartbeat_age_sec:.0f}s"
            self.stdout.write(f"{st.verdict}: cron_alive={st.cron_alive} heartbeat={hb} leader={st.leader or '-'}")
            for q in st.queues:
                wait = "-" if q.wait_sec is None else f"{q.wait_sec:.0f}s"
                self.stdout.write(f"  queue {q.queue}: depth={q.depth} wait={wait}")
            for b in st.busy:
                self.stdout.write(f"  busy {b.worker}: {b.func} {b.running_sec or 0:.0f}s ({','.join(b.queues)})")
            if st.reason:
                self.stdout.write(f"  reason: {st.reason}")
        if st.verdict != "ok":
            sys.exit(1)
