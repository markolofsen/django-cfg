"""
Management command to update currency data using django_currency database loader.

This command automatically populates and updates the payments Currency model
with fresh data from external APIs (CoinGecko, YFinance).

Usage:
    python manage.py update_currencies
    python manage.py update_currencies --max-crypto 100 --max-fiat 20
    python manage.py update_currencies --dry-run
    python manage.py update_currencies --force-update
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from django_cfg.modules.django_currency.database.database_loader import (
    CurrencyDatabaseLoader,
    DatabaseLoaderConfig,
    create_database_loader
)
from django_cfg.apps.payments.models.currencies import Currency

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command to update currency data.
    
    Features:
    - Automatic detection of new currencies
    - Rate updates for existing currencies
    - Dry-run mode for testing
    - Configurable limits for API calls
    - Progress reporting
    - Error handling and rollback
    """
    
    help = 'Update currency data from external APIs (CoinGecko, YFinance)'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--max-crypto',
            type=int,
            default=500,
            help='Maximum number of cryptocurrencies to load (default: 500)'
        )
        
        parser.add_argument(
            '--max-fiat',
            type=int,
            default=50,
            help='Maximum number of fiat currencies to load (default: 50)'
        )
        
        parser.add_argument(
            '--min-market-cap',
            type=float,
            default=1000000,
            help='Minimum market cap in USD for cryptocurrencies (default: 1M)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes'
        )
        
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Force update all currencies even if recently updated'
        )
        
        parser.add_argument(
            '--exclude-stablecoins',
            action='store_true',
            help='Exclude stablecoins from cryptocurrency updates'
        )
        
        parser.add_argument(
            '--update-threshold-hours',
            type=int,
            default=6,
            help='Only update currencies older than N hours (default: 6)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output with detailed progress'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        
        # Configure logging
        log_level = logging.INFO if options['verbose'] else logging.WARNING
        logging.getLogger('django_cfg.modules.django_currency').setLevel(log_level)
        
        self.stdout.write(
            self.style.SUCCESS('🏦 Starting currency database update...')
        )
        
        try:
            # Create database loader with options
            config = DatabaseLoaderConfig(
                max_cryptocurrencies=options['max_crypto'],
                max_fiat_currencies=options['max_fiat'],
                min_market_cap_usd=options['min_market_cap'],
                exclude_stablecoins=options['exclude_stablecoins'],
                coingecko_delay=1.5,  # Be respectful to APIs
                yfinance_delay=0.5
            )
            
            loader = CurrencyDatabaseLoader(config)
            
            # Get statistics
            stats = loader.get_statistics()
            self.stdout.write(f"📊 Loader config: {stats['total_currencies']} currencies available")
            self.stdout.write(f"   • {stats['total_fiat_currencies']} fiat currencies")
            self.stdout.write(f"   • {stats['total_cryptocurrencies']} cryptocurrencies")
            
            # Check existing currencies
            existing_count = Currency.objects.count()
            self.stdout.write(f"📋 Current database: {existing_count} currencies")
            
            # Determine update strategy
            if options['force_update']:
                currencies_to_update = Currency.objects.all()
                self.stdout.write("🔄 Force update mode: updating all currencies")
            else:
                threshold = timezone.now() - timedelta(hours=options['update_threshold_hours'])
                currencies_to_update = Currency.objects.filter(
                    rate_updated_at__lt=threshold
                ) | Currency.objects.filter(rate_updated_at__isnull=True)
                
                self.stdout.write(
                    f"⏰ Updating currencies older than {options['update_threshold_hours']} hours: "
                    f"{currencies_to_update.count()} currencies"
                )
            
            # Load fresh currency data
            self.stdout.write("🌐 Fetching fresh currency data from APIs...")
            fresh_currencies = loader.build_currency_database_data()
            
            if options['dry_run']:
                self._handle_dry_run(fresh_currencies, currencies_to_update)
            else:
                self._handle_update(fresh_currencies, currencies_to_update, options)
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Update interrupted by user')
            )
            raise CommandError("Update cancelled by user")
            
        except Exception as e:
            logger.exception("Currency update failed")
            self.stdout.write(
                self.style.ERROR(f'❌ Currency update failed: {str(e)}')
            )
            raise CommandError(f"Update failed: {str(e)}")
    
    def _handle_dry_run(self, fresh_currencies: List, currencies_to_update):
        """Handle dry-run mode - show what would be updated."""
        self.stdout.write(
            self.style.WARNING('🧪 DRY RUN MODE - No changes will be made')
        )
        
        # Analyze changes
        existing_codes = set(Currency.objects.values_list('code', flat=True))
        fresh_codes = {curr.code for curr in fresh_currencies}
        
        new_currencies = fresh_codes - existing_codes
        existing_currencies = fresh_codes & existing_codes
        
        self.stdout.write(f"\n📈 Analysis:")
        self.stdout.write(f"   • Would add {len(new_currencies)} new currencies")
        self.stdout.write(f"   • Would update {len(existing_currencies)} existing currencies")
        
        if new_currencies:
            self.stdout.write(f"\n➕ New currencies to add:")
            for code in sorted(list(new_currencies)[:10]):  # Show first 10
                currency = next(c for c in fresh_currencies if c.code == code)
                self.stdout.write(f"   • {code}: {currency.name} ({currency.currency_type})")
            if len(new_currencies) > 10:
                self.stdout.write(f"   ... and {len(new_currencies) - 10} more")
        
        if existing_currencies:
            self.stdout.write(f"\n🔄 Existing currencies to update:")
            for code in sorted(list(existing_currencies)[:10]):  # Show first 10
                currency = next(c for c in fresh_currencies if c.code == code)
                try:
                    existing = Currency.objects.get(code=code)
                    rate_diff = abs(existing.usd_rate - currency.usd_rate)
                    if rate_diff > 0.01:  # Significant change
                        change_pct = ((currency.usd_rate - existing.usd_rate) / existing.usd_rate) * 100
                        self.stdout.write(
                            f"   • {code}: ${existing.usd_rate:.6f} → ${currency.usd_rate:.6f} "
                            f"({change_pct:+.2f}%)"
                        )
                except Currency.DoesNotExist:
                    pass
        
        self.stdout.write(
            self.style.SUCCESS('\n✅ Dry run completed - use --force-update to apply changes')
        )
    
    def _handle_update(self, fresh_currencies: List, currencies_to_update, options: Dict):
        """Handle actual database update."""
        
        updated_count = 0
        created_count = 0
        errors = []
        
        # Create lookup for fresh data
        fresh_data_map = {curr.code: curr for curr in fresh_currencies}
        
        try:
            with transaction.atomic():
                self.stdout.write("💾 Updating database...")
                
                # Process currencies
                for i, fresh_currency in enumerate(fresh_currencies):
                    try:
                        currency, created = Currency.objects.update_or_create(
                            code=fresh_currency.code,
                            defaults={
                                'name': fresh_currency.name,
                                'symbol': fresh_currency.symbol,
                                'currency_type': fresh_currency.currency_type,
                                'decimal_places': fresh_currency.decimal_places,
                                'usd_rate': fresh_currency.usd_rate,
                                'min_payment_amount': fresh_currency.min_payment_amount,
                                'is_active': fresh_currency.is_active,
                                'rate_updated_at': timezone.now()
                            }
                        )
                        
                        if created:
                            created_count += 1
                            if options['verbose']:
                                self.stdout.write(f"   ➕ Created {fresh_currency.code}")
                        else:
                            updated_count += 1
                            if options['verbose']:
                                self.stdout.write(f"   🔄 Updated {fresh_currency.code}")
                        
                        # Progress indicator
                        if (i + 1) % 50 == 0:
                            self.stdout.write(f"   Progress: {i + 1}/{len(fresh_currencies)} currencies processed")
                    
                    except Exception as e:
                        error_msg = f"Failed to update {fresh_currency.code}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        
                        # Continue with other currencies unless it's a critical error
                        if len(errors) > 10:  # Too many errors
                            raise CommandError(f"Too many errors ({len(errors)}), aborting")
                
                # Summary
                total_processed = created_count + updated_count
                self.stdout.write(f"\n📊 Update Summary:")
                self.stdout.write(f"   ✅ Successfully processed: {total_processed} currencies")
                self.stdout.write(f"   ➕ Created new: {created_count}")
                self.stdout.write(f"   🔄 Updated existing: {updated_count}")
                
                if errors:
                    self.stdout.write(f"   ⚠️ Errors: {len(errors)}")
                    for error in errors[:5]:  # Show first 5 errors
                        self.stdout.write(f"      • {error}")
                    if len(errors) > 5:
                        self.stdout.write(f"      ... and {len(errors) - 5} more errors")
                
                # Deactivate currencies not in fresh data (optional)
                fresh_codes = {curr.code for curr in fresh_currencies}
                stale_currencies = Currency.objects.filter(is_active=True).exclude(
                    code__in=fresh_codes
                )
                
                if stale_currencies.exists():
                    self.stdout.write(f"   📋 Found {stale_currencies.count()} currencies not in fresh data")
                    # Optionally deactivate them
                    # stale_currencies.update(is_active=False)
                
                self.stdout.write(
                    self.style.SUCCESS('✅ Currency database update completed successfully!')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Update failed and rolled back: {str(e)}')
            )
            raise
    
    def _show_statistics(self):
        """Show current currency statistics."""
        total = Currency.objects.count()
        fiat_count = Currency.objects.filter(currency_type=Currency.CurrencyType.FIAT).count()
        crypto_count = Currency.objects.filter(currency_type=Currency.CurrencyType.CRYPTO).count()
        active_count = Currency.objects.filter(is_active=True).count()
        
        # Recent updates
        recent_threshold = timezone.now() - timedelta(hours=24)
        recent_updates = Currency.objects.filter(rate_updated_at__gte=recent_threshold).count()
        
        self.stdout.write(f"\n📊 Current Database Statistics:")
        self.stdout.write(f"   • Total currencies: {total}")
        self.stdout.write(f"   • Fiat currencies: {fiat_count}")
        self.stdout.write(f"   • Cryptocurrencies: {crypto_count}")
        self.stdout.write(f"   • Active currencies: {active_count}")
        self.stdout.write(f"   • Updated in last 24h: {recent_updates}")
        
        # Show some examples
        recent_currencies = Currency.objects.filter(
            rate_updated_at__gte=recent_threshold
        ).order_by('-rate_updated_at')[:5]
        
        if recent_currencies:
            self.stdout.write(f"\n🕒 Recently updated currencies:")
            for currency in recent_currencies:
                age = timezone.now() - currency.rate_updated_at
                hours_ago = int(age.total_seconds() / 3600)
                self.stdout.write(
                    f"   • {currency.code}: ${currency.usd_rate:.6f} ({hours_ago}h ago)"
                )
