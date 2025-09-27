"""
Provider management command for Universal Payment System v2.0.

Manages payment provider synchronization, health checks, and statistics.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from typing import List, Optional, Dict
import time

from django_cfg.modules.django_logger import get_logger
from django_cfg.apps.payments.models import Currency, Network, ProviderCurrency
from django_cfg.apps.payments.services.providers import get_provider_registry

logger = get_logger("manage_providers")


class Command(BaseCommand):
    """
    Universal provider management command.
    
    Features:
    - Provider currency synchronization
    - Health monitoring and statistics
    - Selective provider updates
    - Integration with ProviderRegistry
    """
    
    help = 'Manage payment providers and their currencies'
    
    def add_arguments(self, parser):
        """Add command arguments."""
        
        # Main operation modes
        parser.add_argument(
            '--all',
            action='store_true',
            help='Sync all active providers'
        )
        
        parser.add_argument(
            '--provider',
            type=str,
            help='Sync specific provider (e.g., nowpayments, cryptomus)'
        )
        
        parser.add_argument(
            '--health-check',
            action='store_true',
            help='Perform health check on all providers'
        )
        
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show provider statistics'
        )
        
        # Sync options
        parser.add_argument(
            '--with-rates',
            action='store_true',
            help='Update USD rates after syncing currencies'
        )
        
        parser.add_argument(
            '--currencies',
            type=str,
            help='Comma-separated list of currency codes to sync (e.g., BTC,ETH,USDT)'
        )
        
        parser.add_argument(
            '--force-refresh',
            action='store_true',
            help='Force refresh even if recently synced'
        )
        
        # Behavior options
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed output'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        
        start_time = time.time()
        
        try:
            self.stdout.write(
                self.style.SUCCESS('🚀 Starting Provider Management')
            )
            
            # Get provider registry
            registry = get_provider_registry()
            
            # Determine operation mode
            if options['health_check']:
                self._perform_health_check(registry, options)
            elif options['stats']:
                self._show_provider_stats(registry, options)
            elif options['provider']:
                self._sync_single_provider(registry, options['provider'], options)
            elif options['all']:
                self._sync_all_providers(registry, options)
            else:
                # Default: show available providers and basic stats
                self._show_available_providers(registry, options)
            
            # Show summary
            elapsed = time.time() - start_time
            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Provider management completed in {elapsed:.1f}s'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Provider management failed: {e}')
            )
            logger.error(f"Provider management command failed: {e}")
            raise CommandError(f"Command failed: {e}")
    
    def _sync_all_providers(self, registry, options):
        """Sync all active providers."""
        
        self.stdout.write("🔄 Syncing all active providers...")
        
        available_providers = registry.get_available_providers()
        
        if not available_providers:
            self.stdout.write("⚠️  No active providers found")
            return
        
        total_synced = 0
        total_errors = 0
        
        for provider_name in available_providers:
            try:
                synced_count = self._sync_provider(registry, provider_name, options)
                total_synced += synced_count
                
            except Exception as e:
                self.stdout.write(f"❌ Failed to sync {provider_name}: {e}")
                total_errors += 1
                logger.error(f"Provider sync failed for {provider_name}: {e}")
        
        self.stdout.write(
            f"🔄 All providers sync complete: {total_synced} currencies synced, {total_errors} errors"
        )
        
        # Update rates if requested
        if options['with_rates'] and not options['dry_run']:
            self._update_rates_after_sync(options)
    
    def _sync_single_provider(self, registry, provider_name: str, options):
        """Sync a specific provider."""
        
        self.stdout.write(f"🔄 Syncing provider: {provider_name}")
        
        try:
            synced_count = self._sync_provider(registry, provider_name, options)
            self.stdout.write(f"✅ {provider_name} sync complete: {synced_count} currencies")
            
            # Update rates if requested
            if options['with_rates'] and not options['dry_run']:
                self._update_rates_after_sync(options)
                
        except Exception as e:
            self.stdout.write(f"❌ Failed to sync {provider_name}: {e}")
            logger.error(f"Provider sync failed for {provider_name}: {e}")
            raise CommandError(f"Provider sync failed: {e}")
    
    def _sync_provider(self, registry, provider_name: str, options) -> int:
        """Sync currencies for a specific provider."""
        
        try:
            provider = registry.get_provider(provider_name)
            if not provider:
                raise CommandError(f"Provider '{provider_name}' not available")
            
            self.stdout.write(f"   📡 Fetching currencies from {provider_name}...")
            
            if options['dry_run']:
                self.stdout.write(f"   [DRY RUN] Would sync {provider_name} currencies")
                return 0
            
            # Use provider's sync method
            sync_result = provider.sync_currencies_to_db()
            
            if sync_result.errors:
                for error in sync_result.errors:
                    self.stdout.write(f"   ⚠️  {error}")
            
            synced_count = sync_result.currencies_created + sync_result.currencies_updated
            
            self.stdout.write(
                f"   ✅ {provider_name}: {sync_result.currencies_created} created, "
                f"{sync_result.currencies_updated} updated, "
                f"{sync_result.provider_currencies_created} provider mappings created"
            )
            
            if options['verbose']:
                self._show_provider_sync_details(sync_result)
            
            return synced_count
            
        except Exception as e:
            logger.error(f"Provider sync failed for {provider_name}: {e}")
            raise
    
    def _perform_health_check(self, registry, options):
        """Perform health check on all providers."""
        
        self.stdout.write("🏥 Performing provider health check...")
        
        available_providers = registry.get_available_providers()
        
        if not available_providers:
            self.stdout.write("⚠️  No providers configured")
            return
        
        healthy_count = 0
        unhealthy_count = 0
        
        for provider_name in available_providers:
            try:
                provider = registry.get_provider(provider_name)
                
                if not provider:
                    self.stdout.write(f"   ❌ {provider_name}: Not available")
                    unhealthy_count += 1
                    continue
                
                # Check if provider is enabled
                if not provider.is_enabled():
                    self.stdout.write(f"   ⏸️  {provider_name}: Disabled")
                    continue
                
                # Perform basic health check (try to get currencies)
                start_time = time.time()
                
                try:
                    currencies = provider.get_parsed_currencies()
                    response_time = time.time() - start_time
                    
                    if currencies and len(currencies.currencies) > 0:
                        self.stdout.write(
                            f"   ✅ {provider_name}: Healthy "
                            f"({len(currencies.currencies)} currencies, {response_time:.2f}s)"
                        )
                        healthy_count += 1
                    else:
                        self.stdout.write(f"   ⚠️  {provider_name}: No currencies returned")
                        unhealthy_count += 1
                        
                except Exception as e:
                    response_time = time.time() - start_time
                    self.stdout.write(
                        f"   ❌ {provider_name}: Error ({response_time:.2f}s) - {str(e)[:50]}"
                    )
                    unhealthy_count += 1
                    
            except Exception as e:
                self.stdout.write(f"   ❌ {provider_name}: Critical error - {e}")
                unhealthy_count += 1
        
        self.stdout.write(
            f"🏥 Health check complete: {healthy_count} healthy, {unhealthy_count} unhealthy"
        )
    
    def _show_provider_stats(self, registry, options):
        """Show detailed provider statistics."""
        
        self.stdout.write("📊 Provider Statistics:")
        
        # Registry stats
        available_providers = registry.get_available_providers()
        self.stdout.write(f"\n🔧 Registry Status:")
        self.stdout.write(f"   Available providers: {len(available_providers)}")
        
        for provider_name in available_providers:
            provider = registry.get_provider(provider_name)
            status = "✅ Enabled" if provider and provider.is_enabled() else "❌ Disabled"
            self.stdout.write(f"   - {provider_name}: {status}")
        
        # Database stats
        self.stdout.write(f"\n💾 Database Statistics:")
        
        total_provider_currencies = ProviderCurrency.objects.count()
        enabled_provider_currencies = ProviderCurrency.objects.filter(is_enabled=True).count()
        
        self.stdout.write(f"   Total provider currencies: {total_provider_currencies}")
        self.stdout.write(f"   Enabled: {enabled_provider_currencies}")
        
        # Stats by provider
        from django.db.models import Count, Q
        
        provider_stats = ProviderCurrency.objects.values('provider').annotate(
            total=Count('id'),
            enabled=Count('id', filter=Q(is_enabled=True))
        ).order_by('-total')
        
        if provider_stats:
            self.stdout.write(f"\n📈 By Provider:")
            for stat in provider_stats:
                self.stdout.write(
                    f"   - {stat['provider']}: {stat['total']} total, {stat['enabled']} enabled"
                )
        
        # Recent activity
        recent_threshold = timezone.now() - timedelta(hours=24)
        recent_updates = ProviderCurrency.objects.filter(
            updated_at__gte=recent_threshold
        ).count()
        
        self.stdout.write(f"\n🕐 Recent Activity (24h):")
        self.stdout.write(f"   Updated currencies: {recent_updates}")
        
        # Rate coverage
        currencies_with_rates = ProviderCurrency.objects.filter(
            is_enabled=True
        ).count()
        
        rate_coverage = (currencies_with_rates / total_provider_currencies * 100) if total_provider_currencies > 0 else 0
        
        self.stdout.write(f"\n💱 Rate Coverage:")
        self.stdout.write(f"   Currencies with USD rates: {currencies_with_rates} ({rate_coverage:.1f}%)")
    
    def _show_available_providers(self, registry, options):
        """Show available providers and basic info."""
        
        self.stdout.write("📋 Available Providers:")
        
        available_providers = registry.get_available_providers()
        
        if not available_providers:
            self.stdout.write("   No providers configured")
            return
        
        for provider_name in available_providers:
            try:
                provider = registry.get_provider(provider_name)
                
                if provider:
                    status = "✅ Enabled" if provider.is_enabled() else "❌ Disabled"
                    
                    # Get currency count from database
                    currency_count = ProviderCurrency.objects.filter(
                        provider_name=provider_name
                    ).count()
                    
                    self.stdout.write(
                        f"   - {provider_name}: {status} ({currency_count} currencies)"
                    )
                else:
                    self.stdout.write(f"   - {provider_name}: ❌ Not available")
                    
            except Exception as e:
                self.stdout.write(f"   - {provider_name}: ❌ Error - {e}")
        
        self.stdout.write(f"\nUse --all to sync all providers or --provider <name> for specific provider")
    
    def _show_provider_sync_details(self, sync_result):
        """Show detailed sync results."""
        
        self.stdout.write("   📋 Sync Details:")
        self.stdout.write(f"      Currencies created: {sync_result.currencies_created}")
        self.stdout.write(f"      Currencies updated: {sync_result.currencies_updated}")
        self.stdout.write(f"      Networks created: {sync_result.networks_created}")
        self.stdout.write(f"      Provider currencies created: {sync_result.provider_currencies_created}")
        self.stdout.write(f"      Provider currencies updated: {sync_result.provider_currencies_updated}")
        
        if sync_result.errors:
            self.stdout.write(f"      Errors: {len(sync_result.errors)}")
    
    def _update_rates_after_sync(self, options):
        """Update USD rates after provider sync."""
        
        self.stdout.write("💱 Updating USD rates after sync...")
        
        try:
            from django.core.management import call_command
            
            # Update rates for currencies that were just synced
            if options['currencies']:
                currency_codes = options['currencies'].split(',')
                for code in currency_codes:
                    call_command('manage_currencies', '--currency', code.strip(), '--rates-only')
            else:
                call_command('manage_currencies', '--rates-only')
                
            self.stdout.write("💱 Rate update completed")
            
        except Exception as e:
            self.stdout.write(f"⚠️  Rate update failed: {e}")
            logger.warning(f"Rate update after sync failed: {e}")
