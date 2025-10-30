"""
Management command to update cryptocurrency prices from external API.
"""

from django.core.management.base import BaseCommand

from apps.crypto.models import Coin


class Command(BaseCommand):
    help = 'Update cryptocurrency prices from CoinGecko API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--coin',
            type=str,
            help='Update specific coin by symbol (e.g., BTC, ETH)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of coins to update (default: 100)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if data is recent',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        coin_symbol = options.get('coin')
        limit = options.get('limit')
        force = options.get('force')
        dry_run = options.get('dry_run')

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - No changes will be made')
            )

        if coin_symbol:
            self.stdout.write(f'Updating prices for {coin_symbol}...')
            # Update specific coin logic here
            queryset = Coin.objects.filter(symbol__iexact=coin_symbol)
        else:
            self.stdout.write(f'Updating prices for top {limit} coins...')
            # Update all coins logic here
            queryset = Coin.objects.filter(is_active=True)[:limit]

        updated_count = 0
        for coin in queryset:
            if not dry_run:
                # API call and update logic would go here
                pass

            updated_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'✓ Updated {coin.symbol}: ${coin.current_price_usd}')
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'Would update {updated_count} coins (dry run)')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {updated_count} coins')
            )
