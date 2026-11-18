"""
Run the project's RQ schedules on RQ's native cron (replaces ``rqscheduler``).

Every ``RQScheduleConfig`` entry of ``DjangoRQConfig.get_all_schedules()`` is
registered; there is no config file argument. Run ONE per project: a second one
waits as standby (leader lock) and takes over when the first stops. The same
process moves delayed jobs (``enqueue_in/at``, ``Retry(interval=...)``) for every
queue in ``RQ_QUEUES``.

Example:
    python manage.py rqcron
    python manage.py rqcron --list          # print the schedules and exit
    python manage.py rqcron --poll 2 -l DEBUG

Overrides django-rq's ``rqcron`` (django_cfg.modules.django_rq is installed
before django_rq).
"""

import json
import logging

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Runs the RQ cron scheduler with the django-cfg schedules (one per project)"

    def add_arguments(self, parser):
        parser.add_argument("--logging-level", "-l", default="INFO",
                            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        parser.add_argument("--poll", type=float, default=None,
                            help="Seconds between loops (default 1): the delay of a delayed job, at most")
        parser.add_argument("--list", action="store_true", help="Print the registered schedules as JSON and exit")
        parser.add_argument("--alive-file", default=None,
                            help="File touched every loop for the healthcheck (default: $RQCRON_ALIVE_FILE "
                                 "or /tmp/rqcron.alive)")

    def handle(self, *args, **options):
        from django_cfg.modules.django_rq.cron import DEFAULT_POLL_SEC, DjangoCfgCronScheduler
        from django_cfg.modules.django_rq.services.config_helper import get_rq_config

        rq_config = get_rq_config()
        if not rq_config or not rq_config.enabled:
            raise CommandError("RQ is not enabled in the django-cfg config")
        scheduler = DjangoCfgCronScheduler.from_config(
            rq_config,
            poll_interval=options["poll"] or DEFAULT_POLL_SEC,
            logging_level=getattr(logging, options["logging_level"]),
            alive_file=options["alive_file"],
        )
        if options["list"]:
            rows = scheduler.describe()
            self.stdout.write(json.dumps({"schedules": rows, "count": len(rows),
                                         "not_registered": [{"func": f, "reason": r} for f, r in scheduler.skipped]},
                                        indent=2, default=str))
            return
        self.stdout.write(self.style.SUCCESS(
            f"rqcron: {len(scheduler.get_jobs())} recurring, {len(scheduler.one_offs)} one-off, "
            f"{len(scheduler.skipped)} not registered"
        ))
        scheduler.start()
