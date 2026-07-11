"""
monitor_status — show monitor alerting state and event log location.

Usage:
    python manage.py monitor_status
"""

from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    command_name = "monitor_status"
    help = "Show django_monitor alerting state and event log location"

    def handle(self, *args, **options):
        from pathlib import Path

        from django_cfg.modules.django_monitor.capture.notify import _is_alerts_enabled

        self.stdout.write(self.style.SUCCESS("Status: ENABLED (zero-config)"))
        alerts = "on (TelegramConfig set)" if _is_alerts_enabled() else "off (no TelegramConfig)"
        self.stdout.write(f"  Telegram alerts : {alerts}")

        log_path = Path.cwd() / "logs" / "djangocfg" / "monitor.log"
        self.stdout.write(f"  Event log       : {log_path}")
        if log_path.exists():
            with log_path.open("rb") as f:
                lines = sum(1 for _ in f)
            self.stdout.write(f"  Today           : {lines} event(s), {log_path.stat().st_size / 1024:.1f} KB")
        else:
            self.stdout.write("  Today           : no events yet")
