"""
Universal provider synchronization service.

Handles synchronization of currencies from all payment providers to database.
"""

from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from django_cfg.modules.django_logging import get_logger
from django_cfg.apps.payments.models import ProviderCurrency
from .models import CurrencySyncResult
from .registry import get_provider_registry
from .base import BaseProvider

logger = get_logger("provider_sync")


class ProviderSyncService:
    """Universal service for synchronizing all payment providers."""
    
    def __init__(self):
        """Initialize provider sync service."""
        self.registry = get_provider_registry()
    
    def sync_all_providers(
        self, 
        force_refresh: bool = False,
        provider_names: Optional[List[str]] = None
    ) -> Dict[str, CurrencySyncResult]:
        """
        Sync currencies from all available providers.
        
        Args:
            force_refresh: Force refresh even if recently synced
            provider_names: Specific providers to sync (None = all available)
            
        Returns:
            Dict[str, CurrencySyncResult]: Results by provider name
        """
        logger.info("Starting universal provider synchronization")
        
        # Get providers to sync
        if provider_names:
            providers_to_sync = []
            for name in provider_names:
                provider = self.registry.get_provider(name)
                if provider:
                    providers_to_sync.append((name, provider))
                else:
                    logger.warning(f"Provider {name} not available")
        else:
            available_providers = self.registry.get_available_providers()
            providers_to_sync = [
                (name, self.registry.get_provider(name)) 
                for name in available_providers
            ]
        
        if not providers_to_sync:
            logger.warning("No providers available for synchronization")
            return {}
        
        # Sync each provider
        results = {}
        total_currencies = 0
        total_errors = 0
        
        for provider_name, provider in providers_to_sync:
            try:
                logger.info(f"Syncing provider: {provider_name}")
                
                # Check if sync is needed
                if not force_refresh and self._is_recently_synced(provider_name):
                    logger.info(f"Provider {provider_name} recently synced, skipping")
                    results[provider_name] = CurrencySyncResult(
                        total_processed=0,
                        errors=[f"Skipped - recently synced (use --force-refresh to override)"]
                    )
                    continue
                
                # Perform sync
                sync_result = self._sync_single_provider(provider)
                results[provider_name] = sync_result
                
                # Update stats
                total_currencies += sync_result.currencies_created + sync_result.currencies_updated
                total_errors += len(sync_result.errors)
                
                # Mark sync time
                self._mark_sync_time(provider_name)
                
                logger.info(
                    f"Provider {provider_name} sync completed: "
                    f"{sync_result.currencies_created} created, "
                    f"{sync_result.currencies_updated} updated, "
                    f"{len(sync_result.errors)} errors"
                )
                
            except Exception as e:
                error_msg = f"Provider {provider_name} sync failed: {e}"
                logger.error(error_msg)
                results[provider_name] = CurrencySyncResult(
                    total_processed=0,
                    errors=[error_msg]
                )
                total_errors += 1
        
        logger.info(
            f"Universal provider sync completed: "
            f"{len(results)} providers processed, "
            f"{total_currencies} currencies synced, "
            f"{total_errors} errors"
        )
        
        return results
    
    def sync_provider(
        self, 
        provider_name: str, 
        force_refresh: bool = False
    ) -> CurrencySyncResult:
        """
        Sync currencies from a specific provider.
        
        Args:
            provider_name: Name of provider to sync
            force_refresh: Force refresh even if recently synced
            
        Returns:
            CurrencySyncResult: Sync operation result
        """
        provider = self.registry.get_provider(provider_name)
        if not provider:
            return CurrencySyncResult(
                total_processed=0,
                errors=[f"Provider {provider_name} not available"]
            )
        
        # Check if sync is needed
        if not force_refresh and self._is_recently_synced(provider_name):
            return CurrencySyncResult(
                total_processed=0,
                errors=[f"Provider {provider_name} recently synced (use force_refresh=True to override)"]
            )
        
        # Perform sync
        result = self._sync_single_provider(provider)
        
        # Mark sync time
        self._mark_sync_time(provider_name)
        
        return result
    
    def get_sync_statistics(self) -> Dict[str, any]:
        """
        Get synchronization statistics for all providers.
        
        Returns:
            Dict: Statistics by provider
        """
        stats = {}
        
        for provider_name in self.registry.list_providers():
            provider_stats = self._get_provider_stats(provider_name)
            stats[provider_name] = provider_stats
        
        return stats
    
    def _sync_single_provider(self, provider: BaseProvider) -> CurrencySyncResult:
        """Sync currencies from a single provider."""
        try:
            logger.debug(f"Starting sync for provider: {provider.name}")
            
            # Use provider's sync method
            result = provider.sync_currencies_to_db()
            
            logger.debug(
                f"Provider {provider.name} sync result: "
                f"{result.currencies_created} created, "
                f"{result.currencies_updated} updated, "
                f"{result.provider_currencies_created} provider currencies created"
            )
            
            return result
            
        except Exception as e:
            error_msg = f"Sync failed for provider {provider.name}: {e}"
            logger.error(error_msg)
            return CurrencySyncResult(
                total_processed=0,
                errors=[error_msg]
            )
    
    def _is_recently_synced(self, provider_name: str, hours: int = 1) -> bool:
        """Check if provider was recently synced."""
        try:
            # Check if any provider currencies were updated recently
            recent_threshold = timezone.now() - timedelta(hours=hours)
            
            recent_updates = ProviderCurrency.objects.filter(
                provider=provider_name,
                updated_at__gte=recent_threshold
            ).exists()
            
            return recent_updates
            
        except Exception as e:
            logger.warning(f"Failed to check sync status for {provider_name}: {e}")
            return False
    
    def _mark_sync_time(self, provider_name: str):
        """Mark sync time for provider (could be stored in cache/database)."""
        # For now, we rely on ProviderCurrency.updated_at
        # In future, could store in dedicated sync log table
        pass
    
    def _get_provider_stats(self, provider_name: str) -> Dict[str, any]:
        """Get statistics for a specific provider."""
        try:
            from django.db.models import Count, Q
            
            # Get provider currency stats
            provider_currencies = ProviderCurrency.objects.filter(provider=provider_name)
            
            total_currencies = provider_currencies.count()
            enabled_currencies = provider_currencies.filter(is_enabled=True).count()
            
            # Get recent activity
            recent_threshold = timezone.now() - timedelta(hours=24)
            recent_updates = provider_currencies.filter(
                updated_at__gte=recent_threshold
            ).count()
            
            # Get last sync time
            last_sync = None
            if provider_currencies.exists():
                last_sync = provider_currencies.order_by('-updated_at').first().updated_at
            
            return {
                'total_currencies': total_currencies,
                'enabled_currencies': enabled_currencies,
                'disabled_currencies': total_currencies - enabled_currencies,
                'recent_updates_24h': recent_updates,
                'last_sync': last_sync.isoformat() if last_sync else None,
                'is_recently_synced': self._is_recently_synced(provider_name)
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats for {provider_name}: {e}")
            return {
                'error': str(e),
                'total_currencies': 0,
                'enabled_currencies': 0,
                'disabled_currencies': 0,
                'recent_updates_24h': 0,
                'last_sync': None,
                'is_recently_synced': False
            }


# Global sync service instance
_global_sync_service: Optional[ProviderSyncService] = None


def get_provider_sync_service() -> ProviderSyncService:
    """
    Get global provider sync service instance.
    
    Returns:
        ProviderSyncService: Global sync service instance
    """
    global _global_sync_service
    if _global_sync_service is None:
        _global_sync_service = ProviderSyncService()
    return _global_sync_service
