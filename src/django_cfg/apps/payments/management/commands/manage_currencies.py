"""
Universal currency management command.

Combines populate_currencies, update_currencies, and update_currency_rates into one.

Usage:
    python manage.py manage_currencies                          # Update existing currencies and rates
    python manage.py manage_currencies --populate               # Initial population + rates
    python manage.py manage_currencies --rates-only             # Only update USD rates
    python manage.py manage_currencies --max-crypto 50          # Limit crypto currencies
    python manage.py manage_currencies --force                  # Force refresh all data
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from decimal import Decimal
import time

from django_cfg.modules.django_logger import get_logger
from django_cfg.modules.django_currency.database.database_loader import (
    create_database_loader,
    DatabaseLoaderConfig
)
from django_cfg.apps.payments.models import Currency

logger = get_logger("manage_currencies")


class Command(BaseCommand):
    """Universal currency management command."""
    
    help = 'Manage currencies: populate, update, and refresh USD rates'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--populate',
            action='store_true',
            help='Initial population mode (for empty database)'
        )
        parser.add_argument(
            '--rates-only',
            action='store_true',
            help='Only update USD exchange rates'
        )
        parser.add_argument(
            '--max-crypto',
            type=int,
            default=200,
            help='Maximum number of cryptocurrencies to process (default: 200)'
        )
        parser.add_argument(
            '--max-fiat',
            type=int,
            default=50,
            help='Maximum number of fiat currencies to process (default: 50)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh all data even if fresh'
        )
        parser.add_argument(
            '--currency',
            type=str,
            help='Update specific currency by code (e.g., BTC, ETH)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        
    def handle(self, *args, **options):
        """Execute the command."""
        start_time = time.time()
        
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('🚀 Currency Management Tool'))
        self.stdout.write('=' * 60)
        
        # Determine mode
        if options['rates_only']:
            result = self._update_rates_only(options)
        elif options['populate']:
            result = self._populate_and_update(options)
        else:
            result = self._update_existing(options)
            
        # Show summary
        elapsed = time.time() - start_time
        self.stdout.write('=' * 60)
        self.stdout.write(f"⏱️  Completed in {elapsed:.2f} seconds")
        self.stdout.write('=' * 60)
        
        # Commands should not return values to stdout
        pass
        
    def _update_rates_only(self, options):
        """Update only USD exchange rates."""
        self.stdout.write("💱 Updating USD exchange rates...")
        
        if options['currency']:
            currencies = Currency.objects.filter(code__iexact=options['currency'])
            if not currencies.exists():
                raise CommandError(f"Currency '{options['currency']}' not found")
        else:
            # Update all currencies, prioritizing those without rates or stale rates
            stale_threshold = timezone.now() - timedelta(days=1)
            currencies = Currency.objects.filter(
                Q(usd_rate__isnull=True) | 
                Q(rate_updated_at__isnull=True) |
                Q(rate_updated_at__lt=stale_threshold)
            )
        
        updated_count = 0
        error_count = 0
        
        self.stdout.write(f"📊 Processing {currencies.count()} currencies...")
        
        for currency in currencies:
            if options['dry_run']:
                self.stdout.write(f"   [DRY RUN] Would update {currency.code}")
                continue
                
            try:
                # Force refresh if requested
                rate = Currency.objects.get_usd_rate(
                    currency.code, 
                    force_refresh=options['force']
                )
                
                if rate > 0:
                    self.stdout.write(f"   ✅ {currency.code}: ${rate:.8f}")
                    updated_count += 1
                else:
                    self.stdout.write(f"   ⚠️  {currency.code}: No rate available")
                    
            except Exception as e:
                self.stdout.write(f"   ❌ {currency.code}: {str(e)}")
                error_count += 1
        
        self.stdout.write(f"📈 Updated: {updated_count}, Errors: {error_count}")
        return updated_count
        
    def _populate_and_update(self, options):
        """Initial population of currencies."""
        self.stdout.write("🔧 Populating currencies from external APIs...")
        
        # Check if database is empty
        existing_count = Currency.objects.count()
        if existing_count > 0 and not options['force']:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Database already contains {existing_count} currencies. "
                    "Use --force to repopulate."
                )
            )
            return 0
            
        if options['dry_run']:
            self.stdout.write("[DRY RUN] Would populate currencies...")
            return 0
            
        # Create database loader
        config = DatabaseLoaderConfig(
            max_crypto_currencies=options['max_crypto'],
            max_fiat_currencies=options['max_fiat'],
            yahoo_delay=1.0,
            coinpaprika_delay=0.5
        )
        
        loader = create_database_loader(config)
        
        try:
            with transaction.atomic():
                # Load currency data
                currency_data = loader.build_currency_database_data()
                
                created_count = 0
                updated_count = 0
                
                for currency_info in currency_data:
                    currency, created = Currency.objects.get_or_create_normalized(
                        code=currency_info.code,
                        defaults={
                            'name': currency_info.name,
                            'currency_type': currency_info.currency_type,
                            'usd_rate': currency_info.rate,
                            'rate_updated_at': timezone.now()
                        }
                    )
                    
                    if created:
                        created_count += 1
                        self.stdout.write(f"   ➕ Created: {currency.code} - {currency.name}")
                    else:
                        # Update rate
                        currency.usd_rate = currency_info.rate
                        currency.rate_updated_at = timezone.now()
                        currency.save()
                        updated_count += 1
                        self.stdout.write(f"   🔄 Updated: {currency.code} - ${currency.usd_rate:.8f}")
                
                self.stdout.write(f"📊 Created: {created_count}, Updated: {updated_count}")
                return created_count + updated_count
                
        except Exception as e:
            logger.exception("Failed to populate currencies")
            raise CommandError(f"Population failed: {e}")
            
    def _update_existing(self, options):
        """Update existing currencies and rates."""
        self.stdout.write("🔄 Updating existing currencies...")
        
        if options['currency']:
            return self._update_rates_only(options)
            
        # First update currency metadata if needed
        self.stdout.write("1️⃣ Checking currency metadata...")
        
        # Then update rates
        self.stdout.write("2️⃣ Updating USD exchange rates...")
        rate_updates = self._update_rates_only(options)
        
        return rate_updates
