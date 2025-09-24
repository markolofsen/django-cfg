"""
Management command to populate initial currency data.

This is a simpler version of update_currencies designed for initial setup.
Use this when you need to populate an empty currency database.

Usage:
    python manage.py populate_currencies
    python manage.py populate_currencies --quick
    python manage.py populate_currencies --crypto-only
    python manage.py populate_currencies --fiat-only
"""

import logging
from typing import List

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from django_cfg.modules.django_currency.database.database_loader import (
    create_database_loader,
    DatabaseLoaderConfig
)
from django_cfg.apps.payments.models.currencies import Currency

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Simple command to populate initial currency data.
    
    Optimized for first-time setup with sensible defaults.
    """
    
    help = 'Populate initial currency data (for empty database)'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--quick',
            action='store_true',
            help='Quick setup with top 50 cryptocurrencies and 20 fiat currencies'
        )
        
        parser.add_argument(
            '--crypto-only',
            action='store_true',
            help='Only populate cryptocurrencies'
        )
        
        parser.add_argument(
            '--fiat-only',
            action='store_true',
            help='Only populate fiat currencies'
        )
        
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip currencies that already exist in database'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        
        self.stdout.write(
            self.style.SUCCESS('🪙 Populating currency database...')
        )
        
        # Check if database is empty
        existing_count = Currency.objects.count()
        if existing_count > 0 and not options['skip_existing']:
            self.stdout.write(
                self.style.WARNING(f'⚠️ Database already contains {existing_count} currencies')
            )
            response = input('Continue anyway? [y/N]: ')
            if response.lower() != 'y':
                self.stdout.write('Cancelled by user')
                return
        
        try:
            # Configure loader based on options
            if options['quick']:
                config = DatabaseLoaderConfig(
                    max_cryptocurrencies=50,
                    max_fiat_currencies=20,
                    min_market_cap_usd=10_000_000,  # Top coins only
                    coingecko_delay=1.0,  # Faster for initial setup
                )
                self.stdout.write("⚡ Quick setup mode: top 50 crypto + 20 fiat")
            else:
                config = DatabaseLoaderConfig(
                    max_cryptocurrencies=200,
                    max_fiat_currencies=30,
                    min_market_cap_usd=1_000_000,
                    coingecko_delay=1.5,
                )
                self.stdout.write("📈 Standard setup: top 200 crypto + 30 fiat")
            
            loader = create_database_loader(
                max_cryptocurrencies=config.max_cryptocurrencies,
                max_fiat_currencies=config.max_fiat_currencies,
                min_market_cap_usd=config.min_market_cap_usd,
                coingecko_delay=config.coingecko_delay
            )
            
            # Get statistics
            stats = loader.get_statistics()
            self.stdout.write(f"📊 Available: {stats['total_currencies']} currencies")
            
            # Load currency data
            self.stdout.write("🌐 Fetching currency data from APIs...")
            fresh_currencies = loader.build_currency_database_data()
            
            # Filter by type if requested
            if options['crypto_only']:
                fresh_currencies = [c for c in fresh_currencies if c.currency_type == 'crypto']
                self.stdout.write(f"🔗 Crypto only: {len(fresh_currencies)} cryptocurrencies")
            elif options['fiat_only']:
                fresh_currencies = [c for c in fresh_currencies if c.currency_type == 'fiat']
                self.stdout.write(f"💵 Fiat only: {len(fresh_currencies)} fiat currencies")
            else:
                crypto_count = sum(1 for c in fresh_currencies if c.currency_type == 'crypto')
                fiat_count = sum(1 for c in fresh_currencies if c.currency_type == 'fiat')
                self.stdout.write(f"💰 Mixed: {crypto_count} crypto + {fiat_count} fiat")
            
            # Populate database
            self._populate_database(fresh_currencies, options)
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Population interrupted by user')
            )
            raise CommandError("Population cancelled")
            
        except Exception as e:
            logger.exception("Currency population failed")
            self.stdout.write(
                self.style.ERROR(f'❌ Population failed: {str(e)}')
            )
            raise CommandError(f"Population failed: {str(e)}")
    
    def _populate_database(self, currencies: List, options: dict):
        """Populate the database with currencies."""
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        try:
            with transaction.atomic():
                self.stdout.write("💾 Populating database...")
                
                for i, currency_data in enumerate(currencies):
                    try:
                        # Check if exists and should skip
                        if options['skip_existing']:
                            if Currency.objects.filter(code=currency_data.code).exists():
                                skipped_count += 1
                                continue
                        
                        # Create or update
                        currency, created = Currency.objects.update_or_create(
                            code=currency_data.code,
                            defaults={
                                'name': currency_data.name,
                                'symbol': currency_data.symbol,
                                'currency_type': currency_data.currency_type,
                                'decimal_places': currency_data.decimal_places,
                                'usd_rate': currency_data.usd_rate,
                                'min_payment_amount': currency_data.min_payment_amount,
                                'is_active': currency_data.is_active,
                                'rate_updated_at': timezone.now()
                            }
                        )
                        
                        if created:
                            created_count += 1
                        else:
                            updated_count += 1
                        
                        # Progress indicator every 25 currencies
                        if (i + 1) % 25 == 0:
                            self.stdout.write(f"   📊 Progress: {i + 1}/{len(currencies)}")
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'⚠️ Failed to create {currency_data.code}: {e}')
                        )
                        continue
                
                # Final summary
                total_processed = created_count + updated_count
                self.stdout.write(f"\n🎉 Population completed!")
                self.stdout.write(f"   ✅ Created: {created_count} currencies")
                self.stdout.write(f"   🔄 Updated: {updated_count} currencies")
                self.stdout.write(f"   ⏭️ Skipped: {skipped_count} currencies")
                self.stdout.write(f"   📊 Total: {total_processed} currencies processed")
                
                # Show some examples
                self._show_examples()
                
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Currency database is ready for payments!')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Population failed and rolled back: {str(e)}')
            )
            raise
    
    def _show_examples(self):
        """Show some example currencies that were created."""
        
        # Show top cryptocurrencies
        crypto_examples = Currency.objects.filter(
            currency_type=Currency.CurrencyType.CRYPTO
        ).order_by('-usd_rate')[:3]
        
        if crypto_examples:
            self.stdout.write(f"\n🔗 Top cryptocurrencies:")
            for currency in crypto_examples:
                self.stdout.write(f"   • {currency.code}: ${currency.usd_rate:.2f}")
        
        # Show fiat currencies
        fiat_examples = Currency.objects.filter(
            currency_type=Currency.CurrencyType.FIAT
        ).order_by('code')[:5]
        
        if fiat_examples:
            self.stdout.write(f"\n💵 Fiat currencies:")
            for currency in fiat_examples:
                self.stdout.write(f"   • {currency.code}: {currency.name} ({currency.symbol})")
        
        # Total counts
        total = Currency.objects.count()
        crypto_count = Currency.objects.filter(currency_type=Currency.CurrencyType.CRYPTO).count()
        fiat_count = Currency.objects.filter(currency_type=Currency.CurrencyType.FIAT).count()
        
        self.stdout.write(f"\n📊 Database now contains:")
        self.stdout.write(f"   • Total: {total} currencies")
        self.stdout.write(f"   • Crypto: {crypto_count} currencies")
        self.stdout.write(f"   • Fiat: {fiat_count} currencies")
