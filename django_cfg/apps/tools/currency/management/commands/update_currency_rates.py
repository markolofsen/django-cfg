"""
Management command to update currencies and rates.

Usage:
    python manage.py update_currency_rates                    # Update rates only
    python manage.py update_currency_rates --verbose          # Verbose output
    python manage.py update_currency_rates --sync-currencies  # Sync currency list
    python manage.py update_currency_rates --all              # Sync currencies + rates
    python manage.py update_currency_rates --stats            # Show statistics
"""

from django.core.management.base import BaseCommand

from django_cfg.apps.tools.currency.services.currencies import (
    get_currency_stats,
    sync_currencies,
)
from django_cfg.apps.tools.currency.services.update import update_rates


class Command(BaseCommand):
    help = "Update currency list and exchange rates"

    def add_arguments(self, parser):
        parser.add_argument(
            "--target",
            type=str,
            default="USD",
            help="Target currency for rates (default: USD)",
        )
        parser.add_argument(
            "--sync-currencies",
            action="store_true",
            help="Sync currency list from predefined data",
        )
        parser.add_argument(
            "--update-existing",
            action="store_true",
            help="Update existing currency metadata (name, symbol)",
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Sync currencies + update rates",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Show currency statistics only",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show detailed output",
        )

    def handle(self, *args, **options):
        target = options["target"]
        sync_curr = options["sync_currencies"] or options["all"]
        update_existing = options["update_existing"]
        update_rates_flag = not options["sync_currencies"] or options["all"]
        show_stats = options["stats"]
        verbose = options["verbose"]

        # Stats only
        if show_stats:
            self._show_stats()
            return

        # Sync currencies
        if sync_curr:
            self._sync_currencies(update_existing, verbose)

        # Update rates
        if update_rates_flag and not options["stats"]:
            self._update_rates(target, verbose)

        # Show final stats
        if verbose:
            self._show_stats()

    def _sync_currencies(self, update_existing: bool, verbose: bool):
        self.stdout.write("Syncing currency list...")

        result = sync_currencies(update_existing=update_existing)

        self.stdout.write(
            self.style.SUCCESS(
                f"Currencies: {result['created']} created, "
                f"{result['updated']} updated, "
                f"{result['skipped']} skipped"
            )
        )

        if verbose and result["created_codes"]:
            self.stdout.write(f"  Created: {', '.join(result['created_codes'])}")

        if verbose and result["updated_codes"]:
            self.stdout.write(f"  Updated: {', '.join(result['updated_codes'])}")

    def _update_rates(self, target: str, verbose: bool):
        self.stdout.write(f"Updating rates to {target}...")

        try:
            result = update_rates(target_currency=target)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Rates: {result['updated']} updated, {result['failed']} failed"
                )
            )

            if verbose and result["rates"]:
                self.stdout.write("\nSample rates:")
                for rate in result["rates"][:5]:
                    self.stdout.write(f"  {rate['pair']}: {rate['rate']}")
                if len(result["rates"]) > 5:
                    self.stdout.write(f"  ... and {len(result['rates']) - 5} more")

            if result["errors"]:
                self.stdout.write(self.style.WARNING(f"\nFailed: {len(result['errors'])}"))
                if verbose:
                    for error in result["errors"][:3]:
                        self.stdout.write(f"  {error['pair']}: {error['error']}")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed: {e}"))
            raise

    def _show_stats(self):
        stats = get_currency_stats()

        self.stdout.write("\nCurrency Statistics:")
        self.stdout.write(f"  Total currencies: {stats['total']}")
        self.stdout.write(f"  Active: {stats['active']} (fiat: {stats['fiat']}, crypto: {stats['crypto']})")
        self.stdout.write(f"  Inactive: {stats['inactive']}")
        self.stdout.write(f"  Exchange rates: {stats['rates']}")
