"""
Management command to import cryptocurrency coins.

This is a CLI wrapper around the RQ task function.
Business logic is in apps.crypto.tasks.import_coins
"""

from django.core.management.base import BaseCommand

from apps.crypto.tasks import import_coins


class Command(BaseCommand):
    help = 'Import cryptocurrency data (demo: creates sample coins)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='demo',
            help='Data source (demo, api, csv)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Number of coins to import in this batch (default: 10)',
        )

    def handle(self, *args, **options):
        source = options.get('source', 'demo')
        batch_size = options.get('batch_size', 10)

        self.stdout.write(f'Importing coins from {source}...')

        # Use the task function directly
        result = import_coins(
            source=source,
            batch_size=batch_size
        )

        # Display results
        if result['success']:
            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Import completed:\n"
                    f"  - Imported: {result['imported']} new coins\n"
                    f"  - Updated: {result['updated']} existing coins\n"
                    f"  - Skipped: {result['skipped']}"
                )
            )
        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Import failed: {result.get('message')}")
            )
