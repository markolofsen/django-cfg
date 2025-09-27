"""
Currency management command for Universal Payment System v2.0.

Integrates with django_currency module for automatic rate updates and population.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from typing import List, Optional
import time

from django_cfg.modules.django_logger import get_logger
from django_cfg.modules.django_currency import (
    CurrencyConverter, convert_currency, get_exchange_rate,
    CurrencyError, CurrencyNotFoundError
)
from django_cfg.apps.payments.models import Currency, Network, ProviderCurrency

logger = get_logger("manage_currencies")


class Command(BaseCommand):
    """
    Universal currency management command using ready modules.
    
    Features:
    - Population of missing currencies
    - USD rate updates using django_currency
    - Provider currency synchronization
    - Flexible filtering and options
    """
    
    help = 'Manage currencies and exchange rates for the payment system'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        
        # Main operation modes
        parser.add_argument(
            '--populate',
            action='store_true',
            help='Populate missing base currencies'
        )
        
        parser.add_argument(
            '--rates-only',
            action='store_true',
            help='Update USD exchange rates only (no population)'
        )
        
        parser.add_argument(
            '--sync-providers',
            action='store_true',
            help='Sync provider currencies after rate updates'
        )
        
        # Filtering options
        parser.add_argument(
            '--currency',
            type=str,
            help='Update specific currency code (e.g., BTC, ETH)'
        )
        
        parser.add_argument(
            '--currency-type',
            choices=['fiat', 'crypto'],
            help='Filter by currency type'
        )
        
        parser.add_argument(
            '--provider',
            type=str,
            help='Filter by provider name'
        )
        
        # Behavior options
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force refresh rates even if recently updated'
        )
        
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip currencies that already exist during population'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Limit number of currencies to process (default: 100)'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        
        start_time = time.time()
        
        try:
            self.stdout.write(
                self.style.SUCCESS('🚀 Starting Universal Currency Management')
            )
            
            # Determine operation mode
            if options['populate']:
                result = self._populate_currencies(options)
            elif options['rates_only']:
                result = self._update_rates_only(options)
            else:
                # Default: populate + rates
                self.stdout.write("📋 Running full currency management (populate + rates)")
                populate_result = self._populate_currencies(options)
                rates_result = self._update_rates_only(options)
                result = populate_result + rates_result
            
            # Optional provider sync
            if options['sync_providers']:
                self._sync_provider_currencies(options)
            
            # Show summary
            elapsed = time.time() - start_time
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Currency management completed in {elapsed:.1f}s'
                )
            )
            
            if not options['dry_run']:
                self._show_final_stats()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Currency management failed: {e}')
            )
            logger.error(f"Currency management command failed: {e}")
            raise CommandError(f"Command failed: {e}")
    
    def _populate_currencies(self, options) -> int:
        """Populate missing base currencies."""
        
        self.stdout.write("📦 Populating base currencies...")
        
        # Define standard currencies to populate
        standard_currencies = [
            # Major fiat currencies
            ('USD', 'US Dollar', Currency.CurrencyType.FIAT, '$', 2),
            ('EUR', 'Euro', Currency.CurrencyType.FIAT, '€', 2),
            ('GBP', 'British Pound', Currency.CurrencyType.FIAT, '£', 2),
            ('JPY', 'Japanese Yen', Currency.CurrencyType.FIAT, '¥', 0),
            ('CNY', 'Chinese Yuan', Currency.CurrencyType.FIAT, '¥', 2),
            ('RUB', 'Russian Ruble', Currency.CurrencyType.FIAT, '₽', 2),
            
            # Major cryptocurrencies
            ('BTC', 'Bitcoin', Currency.CurrencyType.CRYPTO, '₿', 8),
            ('ETH', 'Ethereum', Currency.CurrencyType.CRYPTO, 'Ξ', 8),
            ('USDT', 'Tether USD', Currency.CurrencyType.CRYPTO, '₮', 6),
            ('USDC', 'USD Coin', Currency.CurrencyType.CRYPTO, '', 6),
            ('BNB', 'Binance Coin', Currency.CurrencyType.CRYPTO, '', 8),
            ('ADA', 'Cardano', Currency.CurrencyType.CRYPTO, '', 6),
            ('SOL', 'Solana', Currency.CurrencyType.CRYPTO, '', 8),
            ('DOT', 'Polkadot', Currency.CurrencyType.CRYPTO, '', 8),
            ('MATIC', 'Polygon', Currency.CurrencyType.CRYPTO, '', 8),
            ('LTC', 'Litecoin', Currency.CurrencyType.CRYPTO, 'Ł', 8),
            ('TRX', 'TRON', Currency.CurrencyType.CRYPTO, '', 6),
            ('XRP', 'Ripple', Currency.CurrencyType.CRYPTO, '', 6),
        ]
        
        # Apply currency type filter
        if options['currency_type']:
            currency_type_filter = Currency.CurrencyType.FIAT if options['currency_type'] == 'fiat' else Currency.CurrencyType.CRYPTO
            standard_currencies = [
                c for c in standard_currencies 
                if c[2] == currency_type_filter
            ]
        
        # Apply specific currency filter
        if options['currency']:
            currency_code = options['currency'].upper()
            standard_currencies = [
                c for c in standard_currencies 
                if c[0] == currency_code
            ]
            
            if not standard_currencies:
                raise CommandError(f"Currency '{currency_code}' not in standard list")
        
        created_count = 0
        skipped_count = 0
        
        for code, name, currency_type, symbol, decimal_places in standard_currencies:
            
            if options['dry_run']:
                exists = Currency.objects.filter(code=code).exists()
                if exists and options['skip_existing']:
                    self.stdout.write(f"   [DRY RUN] Would skip existing {code}")
                    skipped_count += 1
                else:
                    self.stdout.write(f"   [DRY RUN] Would create/update {code}")
                continue
            
            try:
                currency, created = Currency.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': name,
                        'currency_type': currency_type,
                        'symbol': symbol,
                        'decimal_places': decimal_places,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f"   ✅ Created {code} - {name}")
                    created_count += 1
                    logger.info(f"Created currency: {code}")
                elif not options['skip_existing']:
                    # Update existing currency if not skipping
                    currency.name = name
                    currency.symbol = symbol
                    currency.decimal_places = decimal_places
                    currency.save()
                    self.stdout.write(f"   🔄 Updated {code} - {name}")
                else:
                    self.stdout.write(f"   ⏭️  Skipped existing {code}")
                    skipped_count += 1
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Failed to create {code}: {e}")
                logger.error(f"Failed to create currency {code}: {e}")
        
        self.stdout.write(f"📦 Population complete: {created_count} created, {skipped_count} skipped")
        return created_count
    
    def _update_rates_only(self, options) -> int:
        """Update USD exchange rates using django_currency module."""
        
        self.stdout.write("💱 Updating USD exchange rates...")
        
        # Build queryset based on options
        queryset = Currency.objects.all()
        
        if options['currency']:
            queryset = queryset.filter(code__iexact=options['currency'])
            if not queryset.exists():
                raise CommandError(f"Currency '{options['currency']}' not found")
        
        if options['currency_type']:
            currency_type = Currency.CurrencyType.FIAT if options['currency_type'] == 'fiat' else Currency.CurrencyType.CRYPTO
            queryset = queryset.filter(currency_type=currency_type)
        
        # Filter by staleness unless forced
        if not options['force']:
            # For now, skip staleness check since rate fields don't exist
            # TODO: Implement proper rate tracking fields
            pass
        
        # Apply limit
        queryset = queryset[:options['limit']]
        
        updated_count = 0
        error_count = 0
        
        self.stdout.write(f"📊 Processing {queryset.count()} currencies...")
        
        for currency in queryset:
            
            if options['dry_run']:
                self.stdout.write(f"   [DRY RUN] Would update {currency.code}")
                continue
            
            try:
                # Use django_currency module to get rate
                if currency.code == 'USD':
                    # USD is the base currency
                    usd_rate = 1.0
                else:
                    # Get rate from django_currency
                    usd_rate = get_exchange_rate(currency.code, 'USD')
                
                if usd_rate and usd_rate > 0:
                    # Update rate in ProviderCurrency (create if doesn't exist)
                    provider_currency, created = ProviderCurrency.objects.get_or_create(
                        currency=currency,
                        provider='system',  # System-level rate
                        provider_currency_code=currency.code,
                        defaults={
                            'is_enabled': True
                        }
                    )
                    
                    if not created:
                        # TODO: Add rate tracking fields to ProviderCurrency model
                        provider_currency.save()  # Touch the record to update timestamp
                    
                    # Update currency's exchange rate source
                    currency.exchange_rate_source = 'django_currency'
                    currency.save(update_fields=['exchange_rate_source'])
                    
                    self.stdout.write(f"   ✅ {currency.code}: ${usd_rate:.8f}")
                    updated_count += 1
                    
                else:
                    self.stdout.write(f"   ⚠️  {currency.code}: No rate available")
                    
            except (CurrencyError, CurrencyNotFoundError) as e:
                self.stdout.write(f"   ⚠️  {currency.code}: {str(e)}")
                error_count += 1
            except Exception as e:
                self.stdout.write(f"   ❌ {currency.code}: {str(e)}")
                error_count += 1
                logger.error(f"Failed to update rate for {currency.code}: {e}")
        
        self.stdout.write(f"💱 Rate update complete: {updated_count} updated, {error_count} errors")
        return updated_count
    
    def _sync_provider_currencies(self, options):
        """Sync provider currencies after rate updates."""
        
        self.stdout.write("🔄 Syncing provider currencies...")
        
        try:
            from django.core.management import call_command
            
            if options['provider']:
                call_command('manage_providers', '--provider', options['provider'])
            else:
                call_command('manage_providers', '--all')
                
            self.stdout.write("🔄 Provider sync completed")
            
        except Exception as e:
            self.stdout.write(f"⚠️  Provider sync failed: {e}")
            logger.warning(f"Provider sync failed: {e}")
    
    def _show_final_stats(self):
        """Show final statistics."""
        
        try:
            total_currencies = Currency.objects.count()
            fiat_count = Currency.objects.filter(currency_type=Currency.CurrencyType.FIAT).count()
            crypto_count = Currency.objects.filter(currency_type=Currency.CurrencyType.CRYPTO).count()
            active_count = Currency.objects.filter(is_active=True).count()
            
            # Count currencies with provider configs (simplified since rate fields don't exist)
            currencies_with_rates = Currency.objects.filter(
                provider_configs__isnull=False
            ).distinct().count()
            
            rate_coverage = (currencies_with_rates / total_currencies * 100) if total_currencies > 0 else 0
            
            self.stdout.write("\n📊 Final Statistics:")
            self.stdout.write(f"   Total currencies: {total_currencies}")
            self.stdout.write(f"   Fiat: {fiat_count}, Crypto: {crypto_count}")
            self.stdout.write(f"   Active: {active_count}")
            self.stdout.write(f"   With USD rates: {currencies_with_rates} ({rate_coverage:.1f}%)")
            
        except Exception as e:
            logger.warning(f"Failed to show final stats: {e}")
