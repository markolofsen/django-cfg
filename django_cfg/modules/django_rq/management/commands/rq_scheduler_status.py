"""
Scheduler-vs-worker status; exits 1 when not ok (usable as a healthcheck).

Example:
    python manage.py rq_scheduler_status
    python manage.py rq_scheduler_status --queue high --max-wait 60 --json
"""

import json
import sys

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Tell 'scheduler dead' from 'worker busy/starved'; exit 1 when not ok"

    def add_arguments(self, parser):
        parser.add_argument("--queue", action="append", dest="queues",
                            help="Queue to judge (repeatable; default: all)")
        parser.add_argument("--max-tick-age", type=float, default=120.0,
                            help="Seconds without a scheduler tick before 'scheduler_dead'")
        parser.add_argument("--max-wait", type=float, default=120.0,
                            help="Seconds a queued job may wait before 'starved'")
        parser.add_argument("--json", action="store_true", help="Print JSON")

    def handle(self, *args, **options):
        from django_cfg.modules.django_rq.health.status import scheduler_status

        st = scheduler_status(
            queue_names=options["queues"],
            max_tick_age=options["max_tick_age"],
            max_wait=options["max_wait"],
        )
        if options["json"]:
            self.stdout.write(json.dumps(st.as_dict(), default=str))
        else:
            tick = "n/a" if st.last_tick_age_sec is None else f"{st.last_tick_age_sec:.0f}s"
            self.stdout.write(f"{st.verdict}: scheduler_alive={st.scheduler_alive} last_tick={tick}")
            for q in st.queues:
                wait = "-" if q.wait_sec is None else f"{q.wait_sec:.0f}s"
                self.stdout.write(f"  queue {q.queue}: depth={q.depth} wait={wait}")
            for b in st.busy:
                self.stdout.write(f"  busy {b.worker}: {b.func} {b.running_sec or 0:.0f}s ({','.join(b.queues)})")
            if st.reason:
                self.stdout.write(f"  reason: {st.reason}")
        if st.verdict != "ok":
            sys.exit(1)
