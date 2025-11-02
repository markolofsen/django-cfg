"""
Management command to update cryptocurrency prices from external API.

This is a CLI wrapper around the RQ task function.
Business logic is in apps.crypto.tasks.update_coin_prices
"""

from django.core.management.base import BaseCommand

from apps.crypto.tasks import update_coin_prices


class Command(BaseCommand):
    help = 'Update cryptocurrency prices from CoinGecko API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of coins to update (default: 100)',
        )
        parser.add_argument(
            '--verbosity',
            type=int,
            default=1,
            choices=[0, 1, 2],
            help='Output verbosity: 0=quiet, 1=normal, 2=verbose',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if data is recent',
        )

    def handle(self, *args, **options):
        limit = options.get('limit', 100)
        verbosity = options.get('verbosity', 1)
        force = options.get('force', False)

        # Use the task function directly
        result = update_coin_prices(
            limit=limit,
            verbosity=verbosity,
            force=force
        )

        # Display results
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Price update completed:\n"
                    f"  - Updated: {result['updated']}\n"
                    f"  - Skipped: {result['skipped']}\n"
                    f"  - Failed: {result['failed']}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Price update failed: {result.get('message')}")
            )
