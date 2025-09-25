"""
Provider Fallback Service.

Handles automatic provider switching when providers become unavailable,
ensuring payment system resilience and high availability.
"""

from django_cfg.modules.django_logger import get_logger
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

from django.core.cache import cache
from django.utils import timezone
from pydantic import BaseModel, Field

from ..monitoring.provider_health import get_health_monitor, HealthStatus
from ..providers.registry import ProviderRegistry
from ...models.events import PaymentEvent

logger = get_logger("fallback_service")


class FallbackStrategy(Enum):
    """Provider fallback strategies."""
    ROUND_ROBIN = "round_robin"
    PRIORITY_BASED = "priority_based"
    HEALTH_BASED = "health_based"
    RANDOM = "random"


class ProviderPriority(BaseModel):
    """Provider priority configuration."""
    provider_name: str = Field(..., description="Provider name")
    priority: int = Field(..., description="Priority (1=highest)")
    enabled: bool = Field(default=True, description="Is provider enabled for fallback")
    max_retry_attempts: int = Field(default=3, description="Max retry attempts before fallback")


class FallbackResult(BaseModel):
    """Result of fallback provider selection."""
    success: bool = Field(..., description="Whether fallback was successful")
    original_provider: str = Field(..., description="Original provider that failed")
    fallback_provider: Optional[str] = Field(None, description="Selected fallback provider")
    reason: str = Field(..., description="Reason for fallback")
    retry_attempt: int = Field(default=0, description="Current retry attempt")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ProviderFallbackService:
    """
    Manages provider fallback logic for payment processing.
    
    Features:
    - Multiple fallback strategies
    - Provider priority management
    - Health-based switching
    - Retry logic with exponential backoff
    - Fallback event tracking
    """
    
    def __init__(self):
        """Initialize fallback service."""
        self.health_monitor = get_health_monitor()
        self.provider_registry = ProviderRegistry()
        
        # Default provider priorities (can be configured)
        self.provider_priorities = [
            ProviderPriority(provider_name="cryptapi", priority=1, enabled=True),
            ProviderPriority(provider_name="cryptomus", priority=2, enabled=True),
            ProviderPriority(provider_name="nowpayments", priority=3, enabled=True),
            ProviderPriority(provider_name="stripe", priority=4, enabled=True),
        ]
        
        self.default_strategy = FallbackStrategy.HEALTH_BASED
        self.max_fallback_attempts = 3
        self.fallback_cache_timeout = 600  # 10 minutes
    
    def get_fallback_provider(
        self,
        failed_provider: str,
        currency: str = None,
        strategy: FallbackStrategy = None,
        retry_attempt: int = 0
    ) -> FallbackResult:
        """
        Get fallback provider when primary provider fails.
        
        Args:
            failed_provider: Name of the provider that failed
            currency: Required currency (for provider compatibility)
            strategy: Fallback strategy to use
            retry_attempt: Current retry attempt number
            
        Returns:
            FallbackResult with fallback provider selection
        """
        if retry_attempt >= self.max_fallback_attempts:
            return FallbackResult(
                success=False,
                original_provider=failed_provider,
                reason=f"Max fallback attempts ({self.max_fallback_attempts}) exceeded",
                retry_attempt=retry_attempt
            )
        
        strategy = strategy or self.default_strategy
        
        try:
            # Get available providers based on strategy
            fallback_provider = self._select_fallback_provider(
                failed_provider=failed_provider,
                currency=currency,
                strategy=strategy
            )
            
            if not fallback_provider:
                return FallbackResult(
                    success=False,
                    original_provider=failed_provider,
                    reason="No healthy fallback providers available",
                    retry_attempt=retry_attempt
                )
            
            # Record fallback event
            self._record_fallback_event(
                failed_provider=failed_provider,
                fallback_provider=fallback_provider,
                strategy=strategy.value,
                retry_attempt=retry_attempt
            )
            
            # Cache fallback selection temporarily
            cache_key = f"fallback_{failed_provider}_{fallback_provider}"
            cache.set(cache_key, True, self.fallback_cache_timeout)
            
            logger.info(f"Fallback selected: {failed_provider} -> {fallback_provider} (attempt {retry_attempt + 1})")
            
            return FallbackResult(
                success=True,
                original_provider=failed_provider,
                fallback_provider=fallback_provider,
                reason=f"Fallback using {strategy.value} strategy",
                retry_attempt=retry_attempt,
                metadata={
                    'strategy': strategy.value,
                    'currency_filter': currency
                }
            )
            
        except Exception as e:
            logger.error(f"Error selecting fallback provider: {e}")
            return FallbackResult(
                success=False,
                original_provider=failed_provider,
                reason=f"Fallback selection error: {str(e)}",
                retry_attempt=retry_attempt
            )
    
    def _select_fallback_provider(
        self,
        failed_provider: str,
        currency: str = None,
        strategy: FallbackStrategy = FallbackStrategy.HEALTH_BASED
    ) -> Optional[str]:
        """
        Select fallback provider based on strategy.
        
        Args:
            failed_provider: Provider that failed
            currency: Required currency
            strategy: Fallback strategy
            
        Returns:
            Name of fallback provider or None
        """
        # Get all available providers
        available_providers = list(self.provider_registry.get_all_providers().keys())
        
        # Remove failed provider
        available_providers = [p for p in available_providers if p != failed_provider]
        
        if not available_providers:
            return None
        
        # Filter by enabled providers
        enabled_providers = [
            p for p in available_providers 
            if self._is_provider_enabled(p)
        ]
        
        if not enabled_providers:
            return None
        
        # Filter by currency support if specified
        if currency:
            currency_compatible = []
            for provider_name in enabled_providers:
                provider = self.provider_registry.get_provider(provider_name)
                if provider and hasattr(provider, 'get_supported_currencies'):
                    supported = provider.get_supported_currencies()
                    if currency.upper() in [c.upper() for c in supported]:
                        currency_compatible.append(provider_name)
            enabled_providers = currency_compatible
        
        if not enabled_providers:
            return None
        
        # Apply fallback strategy
        if strategy == FallbackStrategy.HEALTH_BASED:
            return self._select_by_health(enabled_providers)
        elif strategy == FallbackStrategy.PRIORITY_BASED:
            return self._select_by_priority(enabled_providers)
        elif strategy == FallbackStrategy.ROUND_ROBIN:
            return self._select_round_robin(enabled_providers)
        elif strategy == FallbackStrategy.RANDOM:
            import random
            return random.choice(enabled_providers)
        else:
            # Default to health-based
            return self._select_by_health(enabled_providers)
    
    def _select_by_health(self, providers: List[str]) -> Optional[str]:
        """Select provider based on health status and response time."""
        healthy_providers = self.health_monitor.get_healthy_providers()
        
        # Filter to only healthy providers from the available list
        candidates = [p for p in providers if p in healthy_providers]
        
        if not candidates:
            # No healthy providers, try degraded ones
            all_health = self.health_monitor.check_all_providers()
            degraded = [
                p.provider_name for p in all_health.providers 
                if p.status == HealthStatus.DEGRADED and p.provider_name in providers
            ]
            candidates = degraded
        
        if not candidates:
            return None
        
        # Select provider with best response time among healthy ones
        if len(candidates) == 1:
            return candidates[0]
        
        # Get response times and select fastest
        best_provider = None
        best_response_time = float('inf')
        
        for provider_name in candidates:
            health_check = self.health_monitor.check_provider_health(provider_name)
            if health_check.response_time_ms < best_response_time:
                best_response_time = health_check.response_time_ms
                best_provider = provider_name
        
        return best_provider
    
    def _select_by_priority(self, providers: List[str]) -> Optional[str]:
        """Select provider based on configured priority."""
        # Sort providers by priority
        provider_priorities = {p.provider_name: p.priority for p in self.provider_priorities}
        
        # Filter and sort available providers by priority
        available_with_priority = [
            (provider, provider_priorities.get(provider, 999))
            for provider in providers
            if provider in provider_priorities
        ]
        
        if not available_with_priority:
            # If no priorities configured, return first available
            return providers[0] if providers else None
        
        # Sort by priority (lower number = higher priority)
        available_with_priority.sort(key=lambda x: x[1])
        
        return available_with_priority[0][0]
    
    def _select_round_robin(self, providers: List[str]) -> Optional[str]:
        """Select provider using round-robin algorithm."""
        if not providers:
            return None
        
        # Get current round-robin index from cache
        cache_key = "fallback_round_robin_index"
        current_index = cache.get(cache_key, 0)
        
        # Select provider at current index
        selected_provider = providers[current_index % len(providers)]
        
        # Update index for next round
        next_index = (current_index + 1) % len(providers)
        cache.set(cache_key, next_index, 86400)  # Cache for 24 hours
        
        return selected_provider
    
    def _is_provider_enabled(self, provider_name: str) -> bool:
        """Check if provider is enabled for fallback."""
        for priority_config in self.provider_priorities:
            if priority_config.provider_name == provider_name:
                return priority_config.enabled
        
        # Default to enabled if not configured
        return True
    
    def _record_fallback_event(
        self,
        failed_provider: str,
        fallback_provider: str,
        strategy: str,
        retry_attempt: int
    ):
        """Record fallback event for audit trail."""
        try:
            PaymentEvent.objects.create(
                payment_id=f"fallback_{timezone.now().timestamp()}",
                event_type='provider_fallback',
                sequence_number=1,
                event_data={
                    'failed_provider': failed_provider,
                    'fallback_provider': fallback_provider,
                    'strategy': strategy,
                    'retry_attempt': retry_attempt,
                    'timestamp': timezone.now().isoformat()
                },
                processed_by='fallback_service',
                idempotency_key=f"fallback_{failed_provider}_{fallback_provider}_{timezone.now().timestamp()}"
            )
            
        except Exception as e:
            logger.error(f"Failed to record fallback event: {e}")
    
    def configure_provider_priority(self, provider_name: str, priority: int, enabled: bool = True):
        """
        Configure provider priority for fallback.
        
        Args:
            provider_name: Name of the provider
            priority: Priority level (1=highest)
            enabled: Whether provider is enabled for fallback
        """
        # Update existing priority or create new one
        for i, priority_config in enumerate(self.provider_priorities):
            if priority_config.provider_name == provider_name:
                self.provider_priorities[i] = ProviderPriority(
                    provider_name=provider_name,
                    priority=priority,
                    enabled=enabled
                )
                return
        
        # Add new priority configuration
        self.provider_priorities.append(ProviderPriority(
            provider_name=provider_name,
            priority=priority,
            enabled=enabled
        ))
        
        # Re-sort by priority
        self.provider_priorities.sort(key=lambda x: x.priority)
        
        logger.info(f"Updated priority for {provider_name}: priority={priority}, enabled={enabled}")
    
    def get_fallback_statistics(self, days: int = 7) -> Dict[str, Any]:
        """
        Get fallback statistics for the specified period.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dict with fallback statistics
        """
        try:
            since_date = timezone.now() - timezone.timedelta(days=days)
            
            fallback_events = PaymentEvent.objects.filter(
                event_type='provider_fallback',
                created_at__gte=since_date
            )
            
            stats = {
                'total_fallbacks': fallback_events.count(),
                'fallbacks_by_provider': {},
                'fallbacks_by_strategy': {},
                'most_failed_provider': None,
                'most_used_fallback': None,
                'period_days': days
            }
            
            # Analyze fallback patterns
            for event in fallback_events:
                data = event.event_data
                failed_provider = data.get('failed_provider')
                fallback_provider = data.get('fallback_provider')
                strategy = data.get('strategy')
                
                # Count by failed provider
                if failed_provider:
                    stats['fallbacks_by_provider'][failed_provider] = \
                        stats['fallbacks_by_provider'].get(failed_provider, 0) + 1
                
                # Count by strategy
                if strategy:
                    stats['fallbacks_by_strategy'][strategy] = \
                        stats['fallbacks_by_strategy'].get(strategy, 0) + 1
            
            # Find most problematic provider
            if stats['fallbacks_by_provider']:
                stats['most_failed_provider'] = max(
                    stats['fallbacks_by_provider'].items(),
                    key=lambda x: x[1]
                )[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get fallback statistics: {e}")
            return {
                'total_fallbacks': 0,
                'fallbacks_by_provider': {},
                'fallbacks_by_strategy': {},
                'error': str(e)
            }


# Global fallback service instance
fallback_service = ProviderFallbackService()


def get_fallback_service() -> ProviderFallbackService:
    """Get global fallback service instance."""
    return fallback_service
