"""
Management command to check LLM provider balances and send notifications.

Usage:
    python manage.py check_llm_balance
    python manage.py check_llm_balance --force  # Bypass cache
    python manage.py check_llm_balance --force-notify  # Force send notifications

Recommended cron schedule (hourly):
    0 * * * * cd /path/to/project && python manage.py check_llm_balance
"""

import time
from django.core.management.base import BaseCommand

from django_cfg.modules.django_llm_monitoring import BalanceChecker, LLMBalanceNotifier


class Command(BaseCommand):
    help = "Check LLM provider balances (OpenAI, OpenRouter) and send notifications if low"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force fresh API calls (bypass cache)",
        )
        parser.add_argument(
            "--force-notify",
            action="store_true",
            help="Force send notifications (even if already sent in last 24h)",
        )

    def handle(self, *args, **options):
        force = options["force"]
        force_notify = options["force_notify"]

        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("LLM BALANCE CHECK"))
        self.stdout.write("=" * 70)

        if force:
            self.stdout.write(self.style.WARNING("Force mode: bypassing cache"))
        if force_notify:
            self.stdout.write(self.style.WARNING("Force notify: will send notifications even if recently sent"))

        self.stdout.write("")

        # Initialize checker and notifier
        checker = BalanceChecker()
        notifier = LLMBalanceNotifier()

        # Check balances
        self.stdout.write("Checking balances...")
        balances = checker.check_all_balances(force=force)

        # Display results
        self.stdout.write("")
        for provider, balance_data in balances.items():
            provider_display = provider.replace("_", " ").title()

            if balance_data.error:
                self.stdout.write(
                    self.style.ERROR(f"  ✗ {provider_display}: {balance_data.error}")
                )
            elif balance_data.balance is None:
                # Balance not available - show API key status
                if balance_data.status == "valid":
                    status = self.style.SUCCESS(f"API Key Valid ✓")
                    if balance_data.note:
                        status += f" ({balance_data.note})"
                    self.stdout.write(f"  {provider_display}: {status}")
                else:
                    status = self.style.WARNING(f"Status: {balance_data.status}")
                    self.stdout.write(f"  {provider_display}: {status}")
            else:
                balance = balance_data.balance
                currency = balance_data.currency.upper()

                # Colorize based on balance level
                if balance <= notifier.THRESHOLD_CRITICAL:
                    status = self.style.ERROR(f"${balance:.2f} {currency} 🚨 CRITICAL")
                elif balance <= notifier.THRESHOLD_WARNING:
                    status = self.style.WARNING(f"${balance:.2f} {currency} ⚠️ WARNING")
                else:
                    status = self.style.SUCCESS(f"${balance:.2f} {currency} ✓ OK")

                # Show additional info
                extra_info = []
                if balance_data.limit:
                    extra_info.append(f"limit: ${balance_data.limit:.2f}")
                if balance_data.usage:
                    extra_info.append(f"usage: ${balance_data.usage:.2f}")
                if balance_data.note:
                    extra_info.append(f"({balance_data.note})")

                if extra_info:
                    status += f" [{', '.join(extra_info)}]"

                self.stdout.write(f"  {provider_display}: {status}")

        # Check and send notifications
        self.stdout.write("")
        self.stdout.write("Checking notification thresholds...")
        notification_results = notifier.check_all_and_notify(balances, force=force_notify)

        # Show notification results
        notifications_sent = False
        for provider, level in notification_results.items():
            if level:
                notifications_sent = True
                provider_display = provider.replace("_", " ").title()
                emoji = "🚨" if level == "critical" else "⚠️"
                self.stdout.write(
                    self.style.WARNING(f"  {emoji} Sent {level.upper()} notification: {provider_display}")
                )

        if not notifications_sent:
            self.stdout.write(self.style.SUCCESS("  ✓ No notifications needed"))

        # Summary
        self.stdout.write("")
        self.stdout.write("=" * 70)
        self.stdout.write(self.style.SUCCESS("CHECK COMPLETE"))
        self.stdout.write("=" * 70)

        total_balance = sum(
            data.balance
            for data in balances.values()
            if not data.error and data.balance is not None
        )
        self.stdout.write(f"Total balance across all providers: ${total_balance:.2f} USD")

        if notifications_sent:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("⚠️ Low balance alerts were sent to administrators")
            )
            # Wait for Telegram queue to process messages (async worker thread)
            self.stdout.write("")
            self.stdout.write("Waiting for notification delivery...")
            time.sleep(2)  # Give queue worker time to send messages
            self.stdout.write(self.style.SUCCESS("✓ Notifications delivered"))
