"""
Run the RQ queue-health monitor once from the command line.

Shares the exact :class:`QueueHealthMonitor` implementation used by the
periodic ``run_queue_health_check`` scheduled task — this command is the
secondary, manual entry point.

Examples:
    python manage.py rq_health_check
    python manage.py rq_health_check --dry-run
    python manage.py rq_health_check --queue crm
    python manage.py rq_health_check --json
"""

import json

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Run one RQ queue-health check cycle.

    Collects per-queue metrics (depth, oldest-job age, failed count, worker
    liveness, scheduler lag, orphan-id ratio), evaluates them against the
    configured thresholds, and (unless ``--dry-run``) sends Telegram alerts for
    degraded queues.

    Options:
        --dry-run         Evaluate and report but never send Telegram alerts
                          or prune orphan IDs.
        --queue NAME      Only check this single queue (overrides config).
        --json            Print the summary as JSON instead of human text.
    """

    help = "Run the RQ queue-health monitor once (with Telegram alerting)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Evaluate and report but never send Telegram alerts or prune orphan IDs",
        )
        parser.add_argument(
            "--queue",
            type=str,
            default=None,
            help="Only check this single queue (overrides monitored_queues config)",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            dest="as_json",
            help="Print the summary as JSON",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        dry_run = options.get("dry_run", False)
        queue = options.get("queue")
        as_json = options.get("as_json", False)

        from django_cfg.modules.django_rq.health.monitor import QueueHealthMonitor

        config = None
        if queue:
            # Build a config restricted to the single requested queue, copied
            # from the resolved config so thresholds/overrides are preserved.
            base = QueueHealthMonitor().resolve_config()
            config = base.model_copy(update={"monitored_queues": [queue]})

        monitor = QueueHealthMonitor(config=config, dry_run=dry_run)
        summary = monitor.run()

        if as_json:
            self.stdout.write(json.dumps(summary, indent=2, default=str))
            return

        self._print_human(summary)

    def _print_human(self, summary: dict) -> None:
        """Render the summary as colored human-readable text."""
        if summary.get("error"):
            self.stdout.write(self.style.ERROR(f"Health check error: {summary['error']}"))

        checked = summary.get("checked", 0)
        critical = summary.get("critical", 0)
        warning = summary.get("warning", 0)
        healthy = summary.get("healthy", 0)

        header = (
            f"RQ queue-health: {checked} checked — "
            f"{healthy} healthy, {warning} warning, {critical} critical"
        )
        if critical:
            self.stdout.write(self.style.ERROR(header))
        elif warning:
            self.stdout.write(self.style.WARNING(header))
        else:
            self.stdout.write(self.style.SUCCESS(header))

        for queue_name, info in (summary.get("queues") or {}).items():
            status = info.get("status", "unknown")
            flags = []
            if info.get("overflow"):
                flags.append("overflow")
            if info.get("stuck"):
                flags.append("stuck")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            breaches = ", ".join(info.get("breaches") or []) or "-"
            line = f"  {queue_name}: {status}{flag_str} — breaches: {breaches}"
            if status == "critical":
                self.stdout.write(self.style.ERROR(line))
            elif status == "warning":
                self.stdout.write(self.style.WARNING(line))
            else:
                self.stdout.write(line)

        if summary.get("dry_run"):
            self.stdout.write(self.style.WARNING("(dry-run: no alerts sent, no pruning)"))
        else:
            self.stdout.write(
                f"Alerts sent: {summary.get('alerts_sent', 0)}, "
                f"recoveries: {summary.get('recoveries_sent', 0)}, "
                f"orphans pruned: {summary.get('orphans_pruned', 0)}"
            )
