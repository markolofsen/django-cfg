"""
Universal payment provider management command.

Combines sync_providers functionality with additional features.

Usage:
    python manage.py manage_providers                           # Sync all active providers
    python manage.py manage_providers --provider nowpayments   # Sync specific provider
    python manage.py manage_providers --with-rates             # Sync providers + update USD rates
    python manage.py manage_providers --stats                  # Show provider statistics
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from typing import List, Optional
import time

from django_cfg.modules.django_logger import get_logger
from django_cfg.apps.payments.services.providers.registry import get_payment_provider, get_available_providers
from django_cfg.apps.payments.models import Currency, ProviderCurrency

logger = get_logger("manage_providers")


class Command(BaseCommand):
    """Universal payment provider management command."""
    
    help = 'Manage payment providers: sync currencies, networks, and rates'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--provider',
            type=str,
            help='Specific provider(s) to sync (comma-separated). E.g: nowpayments,cryptomus'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all available providers'
        )
        parser.add_argument(
            '--with-rates',
            action='store_true',
            help='Also update USD exchange rates after sync'
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show provider statistics'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress information'
        )
        
    def handle(self, *args, **options):
        """Execute the command."""
        start_time = time.time()
        
        self.stdout.write('=' * 60)
        self.stdout.write(self.style.SUCCESS('🚀 Provider Management Tool'))
        self.stdout.write('=' * 60)
        
        if options['stats']:
            return self._show_stats()
            
        # Determine which providers to sync
        if options['provider']:
            provider_names = [p.strip() for p in options['provider'].split(',')]
        elif options['all']:
            provider_names = get_available_providers()
        else:
            # Default: sync active providers only
            provider_names = get_available_providers()
            
        # Sync providers
        total_synced = 0
        for provider_name in provider_names:
            synced = self._sync_provider(provider_name, options)
            total_synced += synced
            
        # Update rates if requested
        if options['with_rates'] and not options['dry_run']:
            self.stdout.write("\n💱 Updating USD exchange rates...")
            self._update_rates()
            
        # Show summary
        elapsed = time.time() - start_time
        self.stdout.write('=' * 60)
        self.stdout.write(f"📊 Total items synced: {total_synced}")
        self.stdout.write(f"⏱️  Completed in {elapsed:.2f} seconds")
        self.stdout.write('=' * 60)
        
        # Commands should not return values to stdout
        pass
        
    def _sync_provider(self, provider_name: str, options: dict) -> int:
        """Sync a specific provider."""
        self.stdout.write(f"\n🔄 Syncing {provider_name}...")
        
        try:
            provider = get_payment_provider(provider_name)
            
            if options['verbose']:
                config = provider.config
                self.stdout.write(f"   📡 Provider: {provider.__class__.__name__}")
                self.stdout.write(f"   🔧 Config: enabled={config.enabled} timeout_seconds={config.timeout_seconds} sandbox={getattr(config, 'sandbox', 'N/A')}")
            
            if options['dry_run']:
                # Dry run: just get parsed currencies to show what would be synced
                try:
                    parsed_response = provider.get_parsed_currencies()
                    currency_count = len(parsed_response.currencies)
                    
                    # Calculate unique networks
                    networks = set()
                    for currency in parsed_response.currencies:
                        if currency.network_code:
                            networks.add(currency.network_code)
                    network_count = len(networks)
                    
                    self.stdout.write(f"   💰 Would sync {currency_count} currencies")
                    self.stdout.write(f"   🌐 Would sync {network_count} networks")
                    
                    return currency_count + network_count
                    
                except Exception as e:
                    self.stdout.write(f"   ❌ Failed to fetch currencies: {e}")
                    return 0
            
            else:
                # Live sync
                with transaction.atomic():
                    sync_result = provider.sync_currencies_to_db()
                    
                    if options['verbose']:
                        self.stdout.write(f"   ✅ Synced {sync_result.total_items_processed} items")
                        if sync_result.errors:
                            self.stdout.write(f"   ⚠️  Errors: {len(sync_result.errors)}")
                            for error in sync_result.errors[:3]:  # Show first 3 errors
                                self.stdout.write(f"      • {error}")
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {provider_name}: {sync_result.total_items_processed} items synced")
                    )
                    
                    return sync_result.total_items_processed
        
        except Exception as e:
            logger.exception(f"Error syncing provider {provider_name}")
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to sync {provider_name}: {e}")
            )
            return 0
            
    def _update_rates(self):
        """Update USD rates for currencies."""
        try:
            # Get currencies that need rate updates
            from datetime import timedelta
            from django.db.models import Q
            
            stale_threshold = timezone.now() - timedelta(hours=12)
            currencies_to_update = Currency.objects.filter(
                Q(usd_rate__isnull=True) | 
                Q(rate_updated_at__isnull=True) |
                Q(rate_updated_at__lt=stale_threshold)
            )[:50]  # Limit to avoid long execution
            
            updated_count = 0
            for currency in currencies_to_update:
                try:
                    rate = Currency.objects.get_usd_rate(currency.code, force_refresh=True)
                    if rate > 0:
                        updated_count += 1
                        self.stdout.write(f"   ✅ {currency.code}: ${rate:.8f}")
                except Exception as e:
                    self.stdout.write(f"   ⚠️  {currency.code}: {str(e)}")
                    
            self.stdout.write(f"💱 Updated {updated_count} exchange rates")
            
        except Exception as e:
            self.stdout.write(f"⚠️  Rate update failed: {e}")
            
    def _show_stats(self):
        """Show provider statistics."""
        self.stdout.write("📊 Provider Statistics")
        self.stdout.write("-" * 40)
        
        # Available providers
        available_providers = get_available_providers()
        self.stdout.write(f"🏢 Available providers: {len(available_providers)}")
        for provider_name in available_providers:
            try:
                provider = get_payment_provider(provider_name)
                enabled = provider.config.enabled
                status = "✅ Enabled" if enabled else "❌ Disabled"
                self.stdout.write(f"   • {provider_name}: {status}")
            except Exception as e:
                self.stdout.write(f"   • {provider_name}: ❌ Error ({e})")
        
        self.stdout.write()
        
        # Database statistics
        total_currencies = Currency.objects.count()
        total_provider_currencies = ProviderCurrency.objects.count()
        
        self.stdout.write(f"💰 Total currencies: {total_currencies}")
        self.stdout.write(f"🔗 Total provider currencies: {total_provider_currencies}")
        
        # Provider breakdown
        from django.db.models import Count
        provider_stats = ProviderCurrency.objects.values('provider_name').annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write("\n📊 Currencies by provider:")
        for stat in provider_stats:
            self.stdout.write(f"   • {stat['provider_name']}: {stat['count']} currencies")
            
        # Rate statistics
        currencies_with_rates = Currency.objects.exclude(usd_rate__isnull=True).exclude(usd_rate=0)
        rate_coverage = (currencies_with_rates.count() / total_currencies * 100) if total_currencies > 0 else 0
        
        self.stdout.write(f"\n💵 USD rate coverage: {rate_coverage:.1f}% ({currencies_with_rates.count()}/{total_currencies})")
        
        # Stats command should not return values
