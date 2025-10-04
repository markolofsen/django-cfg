"""
Currency management command for Universal Payment System v2.0.

Simple and reliable currency management using hybrid client.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta
import time
import concurrent.futures
from threading import Lock

from django_cfg.modules.django_logging import get_logger
from django_cfg.modules.django_currency import CurrencyConverter, CurrencyError
from django_cfg.apps.payments.models import Currency

logger = get_logger("manage_currencies")


class Command(BaseCommand):
    """Simple currency management command using hybrid client."""
    
    help = 'Manage currencies and exchange rates using hybrid client'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--populate',
            action='store_true',
            help='Populate all supported currencies from hybrid client'
        )
        parser.add_argument(
            '--rates-only',
            action='store_true',
            help='Update USD rates only (no population)'
        )
        parser.add_argument(
            '--currency',
            type=str,
            help='Update specific currency only'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if rates are fresh'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Limit number of currencies to process'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=20,
            help='Number of currencies to process in parallel (default: 20)'
        )
        parser.add_argument(
            '--max-workers',
            type=int,
            default=10,
            help='Maximum number of worker threads (default: 10)'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        start_time = time.time()
        
        try:
            self.stdout.write(self.style.SUCCESS('🚀 Starting Universal Currency Management'))
            
            # Initialize converter
            self.converter = CurrencyConverter(cache_ttl=3600)
            
            if options['populate']:
                self._populate_all_currencies(options)
            elif options['rates_only']:
                self._update_rates_only(options)
            else:
                # Default: populate + rates
                self._populate_all_currencies(options)
                self._update_rates_only(options)
            
            # Show summary
            elapsed = time.time() - start_time
            self.stdout.write(self.style.SUCCESS(f'✅ Currency management completed in {elapsed:.1f}s'))
            self._show_final_stats()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Currency management failed: {e}'))
            logger.error(f"Currency management command failed: {e}")
            raise CommandError(f"Command failed: {e}")
    
    def _populate_all_currencies(self, options):
        """Populate all supported currencies from hybrid client."""
        self.stdout.write("📦 Populating base currencies...")
        
        try:
            # Get all supported currencies from hybrid client
            supported_currencies = self.converter.hybrid.get_all_supported_currencies()
            self.stdout.write(f"Found {len(supported_currencies)} supported currencies")
            
            # Apply limit
            if options['limit'] and len(supported_currencies) > options['limit']:
                # Take first N currencies (sorted alphabetically)
                limited_currencies = dict(list(supported_currencies.items())[:options['limit']])
                supported_currencies = limited_currencies
                self.stdout.write(f"Limited to {len(supported_currencies)} currencies")
            
            # Apply specific currency filter
            if options['currency']:
                currency_code = options['currency'].upper()
                if currency_code in supported_currencies:
                    supported_currencies = {currency_code: supported_currencies[currency_code]}
                else:
                    raise CommandError(f"Currency '{currency_code}' not supported by hybrid client")
            
            created_count = 0
            updated_count = 0
            skipped_count = 0
            
            for code, name in supported_currencies.items():
                try:
                    # Determine currency type based on code
                    currency_type = self._determine_currency_type(code)
                    decimal_places = self._get_decimal_places(code, currency_type)
                    symbol = self._get_currency_symbol(code)
                    
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
                    else:
                        # Update name if it's different
                        if currency.name != name:
                            currency.name = name
                            currency.save()
                            self.stdout.write(f"   🔄 Updated {code} - {name}")
                            updated_count += 1
                        else:
                            self.stdout.write(f"   ⏭️  Skipped existing {code}")
                            skipped_count += 1
                            
                except Exception as e:
                    self.stdout.write(f"   ❌ Failed to create {code}: {e}")
                    logger.error(f"Failed to create currency {code}: {e}")
            
            self.stdout.write(f"📦 Population complete: {created_count} created, {updated_count} updated, {skipped_count} skipped")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to populate currencies: {e}"))
            logger.error(f"Currency population failed: {e}")
            raise
    
    def _update_rates_only(self, options):
        """Update USD exchange rates for existing currencies using batch processing."""
        self.stdout.write("💱 Updating USD exchange rates...")
        
        # Get currencies to update
        queryset = Currency.objects.filter(is_active=True)
        
        if options['currency']:
            currency_code = options['currency'].upper()
            queryset = queryset.filter(code=currency_code)
            if not queryset.exists():
                raise CommandError(f"Currency '{currency_code}' not found in database")
        
        # Apply freshness filter unless forced
        if not options['force']:
            # Only update rates older than 1 hour
            stale_threshold = timezone.now() - timedelta(hours=1)
            queryset = queryset.filter(
                models.Q(usd_rate_updated_at__isnull=True) |
                models.Q(usd_rate_updated_at__lt=stale_threshold)
            )
        
        currencies = list(queryset[:options['limit']])
        self.stdout.write(f"📊 Processing {len(currencies)} currencies...")
        
        # Handle USD separately (always 1.0)
        usd_currencies = [c for c in currencies if c.code == 'USD']
        other_currencies = [c for c in currencies if c.code != 'USD']
        
        updated_count = 0
        error_count = 0
        
        # Update USD currencies first (instant)
        for currency in usd_currencies:
            currency.usd_rate = 1.0
            currency.usd_rate_updated_at = timezone.now()
            currency.save()
            self.stdout.write(f"   ✅ USD: $1.00000000")
            updated_count += 1
        
        # Process other currencies in batches with threading
        if other_currencies:
            batch_size = options['batch_size']
            max_workers = min(options['max_workers'], len(other_currencies))
            
            self.stdout.write(f"🚀 Using {max_workers} workers, batch size: {batch_size}")
            
            # Thread-safe counters
            self._lock = Lock()
            self._updated_count = 0
            self._error_count = 0
            
            # Process in batches
            for i in range(0, len(other_currencies), batch_size):
                batch = other_currencies[i:i + batch_size]
                self.stdout.write(f"📦 Processing batch {i//batch_size + 1}/{(len(other_currencies) + batch_size - 1)//batch_size} ({len(batch)} currencies)")
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all tasks in current batch
                    future_to_currency = {
                        executor.submit(self._update_single_rate, currency): currency 
                        for currency in batch
                    }
                    
                    # Process completed tasks
                    for future in concurrent.futures.as_completed(future_to_currency):
                        currency = future_to_currency[future]
                        try:
                            success = future.result()
                            if success:
                                with self._lock:
                                    self._updated_count += 1
                            else:
                                with self._lock:
                                    self._error_count += 1
                        except Exception as e:
                            self.stdout.write(f"   ❌ {currency.code}: Thread error: {e}")
                            with self._lock:
                                self._error_count += 1
                
                # Show batch progress
                with self._lock:
                    self.stdout.write(f"   📊 Batch complete: {self._updated_count} updated, {self._error_count} errors so far")
            
            updated_count += self._updated_count
            error_count += self._error_count
        
        self.stdout.write(f"💱 Rate update complete: {updated_count} updated, {error_count} errors")
    
    def _update_single_rate(self, currency):
        """Update rate for a single currency (thread-safe)."""
        try:
            # Get rate from hybrid client
            rate_obj = self.converter.hybrid.fetch_rate(currency.code, 'USD')
            
            # Update database (Django ORM is thread-safe for individual operations)
            currency.usd_rate = rate_obj.rate
            currency.usd_rate_updated_at = timezone.now()
            currency.save()
            
            self.stdout.write(f"   ✅ {currency.code}: ${rate_obj.rate:.8f}")
            return True
            
        except Exception as e:
            self.stdout.write(f"   ⚠️  {currency.code}: Failed to convert 1.0 {currency.code} to USD: {e}")
            logger.warning(f"Rate update failed for {currency.code}: {e}")
            return False
    
    def _determine_currency_type(self, code: str) -> str:
        """Determine currency type based on code."""
        crypto_currencies = {
            'BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOT', 'MATIC', 'LTC', 'BCH',
            'LINK', 'UNI', 'ATOM', 'XLM', 'VET', 'FIL', 'TRX', 'ETC', 'THETA',
            'AAVE', 'MKR', 'COMP', 'SUSHI', 'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP'
        }
        
        metal_currencies = {'XAU', 'XAG', 'XPT', 'XPD'}
        
        if code in crypto_currencies:
            return Currency.CurrencyType.CRYPTO
        elif code in metal_currencies:
            return Currency.CurrencyType.FIAT  # Metals are treated as fiat for now
        else:
            return Currency.CurrencyType.FIAT
    
    def _get_decimal_places(self, code: str, currency_type: str) -> int:
        """Get appropriate decimal places for currency."""
        if currency_type == Currency.CurrencyType.CRYPTO:
            # Most cryptos use 8 decimal places, stablecoins use 6
            stablecoins = {'USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'USDP'}
            return 6 if code in stablecoins else 8
        elif code == 'JPY':
            # Japanese Yen has no decimal places
            return 0
        else:
            # Most fiat currencies use 2 decimal places
            return 2
    
    def _get_currency_symbol(self, code: str) -> str:
        """Get currency symbol if known."""
        symbols = {
            'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥', 'RUB': '₽',
            'BTC': '₿', 'ETH': 'Ξ', 'LTC': 'Ł', 'USDT': '₮'
        }
        return symbols.get(code, '')
    
    def _show_final_stats(self):
        """Show final statistics."""
        total_currencies = Currency.objects.count()
        active_currencies = Currency.objects.filter(is_active=True).count()
        
        # Count by type
        fiat_count = Currency.objects.filter(currency_type=Currency.CurrencyType.FIAT).count()
        crypto_count = Currency.objects.filter(currency_type=Currency.CurrencyType.CRYPTO).count()
        
        # Count with USD rates
        with_rates = Currency.objects.filter(usd_rate__isnull=False, usd_rate__gt=0).count()
        rate_percentage = (with_rates / total_currencies * 100) if total_currencies > 0 else 0
        
        self.stdout.write("\n📊 Final Statistics:")
        self.stdout.write(f"   Total currencies: {total_currencies}")
        self.stdout.write(f"   Fiat: {fiat_count}, Crypto: {crypto_count}")
        self.stdout.write(f"   Active: {active_currencies}")
        self.stdout.write(f"   With USD rates: {with_rates} ({rate_percentage:.1f}%)")
