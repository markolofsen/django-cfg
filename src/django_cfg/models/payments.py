"""
Payments configuration model for Django-CFG.

Simple, clean configuration following django-cfg philosophy.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class PaymentsConfig(BaseModel):
    """
    Payments app configuration for django-cfg.
    
    Static configuration that doesn't change at runtime.
    Dynamic settings (API keys, secrets) are handled by Constance.
    """
    
    # Core settings
    enabled: bool = Field(
        default=False, 
        description="Enable payments app"
    )
    
    # Middleware settings
    middleware_enabled: bool = Field(
        default=True,
        description="Enable payments middleware"
    )
    
    # Whitelist approach - only these paths require API key
    protected_paths: List[str] = Field(
        default=[
            '/api/admin/',  # Admin API endpoints
            '/api/private/',  # Private API endpoints
            '/api/secure/',  # Secure API endpoints
        ],
        description="Paths that require API key authentication (whitelist approach)"
    )
    
    protected_patterns: List[str] = Field(
        default=[
            r'^/api/admin/.*$',  # All admin API endpoints
            r'^/api/private/.*$',  # All private API endpoints  
            r'^/api/secure/.*$',  # All secure API endpoints
        ],
        description="Regex patterns for paths that require API key authentication"
    )
    
    # Rate limiting defaults
    rate_limiting_enabled: bool = Field(
        default=True,
        description="Enable rate limiting middleware"
    )
    
    default_rate_limits: Dict[str, int] = Field(
        default={
            'anonymous': 60,
            'authenticated': 300,
            'free': 100,
            'basic': 500,
            'premium': 2000,
            'enterprise': 10000,
        },
        description="Default rate limits (requests per minute) by tier"
    )
    
    # Usage tracking
    usage_tracking_enabled: bool = Field(
        default=True,
        description="Enable usage tracking middleware"
    )
    
    track_anonymous_usage: bool = Field(
        default=False,
        description="Track anonymous user requests"
    )
    
    # Cache settings
    cache_timeouts: Dict[str, int] = Field(
        default={
            'api_key': 300,      # 5 minutes
            'rate_limit': 3600,  # 1 hour
            'session': 1800,     # 30 minutes
            'default': 600       # 10 minutes
        },
        description="Cache timeout settings in seconds"
    )
    
    def get_middleware_classes(self) -> List[str]:
        """
        Get middleware classes to add to Django MIDDLEWARE setting.
        
        Returns:
            List of middleware class paths
        """
        if not self.enabled or not self.middleware_enabled:
            return []
        
        middleware = []
        
        # Always add API access middleware first
        middleware.append('django_cfg.apps.payments.middleware.APIAccessMiddleware')
        
        # Add rate limiting if enabled
        if self.rate_limiting_enabled:
            middleware.append('django_cfg.apps.payments.middleware.RateLimitingMiddleware')
        
        # Add usage tracking if enabled
        if self.usage_tracking_enabled:
            middleware.append('django_cfg.apps.payments.middleware.UsageTrackingMiddleware')
        
        return middleware
    
    def should_enable_tasks(self) -> bool:
        """
        Check if payments app requires Celery tasks.
        
        Returns:
            True if tasks should be enabled
        """
        return self.enabled  # Enable tasks if payments is enabled
    
    # Navigation and UI feature checks
    def show_webhook_dashboard(self) -> bool:
        """Check if webhook dashboard should be shown in navigation."""
        return self.enabled
    
    def show_payment_creation(self) -> bool:
        """Check if payment creation should be shown in navigation."""
        return self.enabled
    
    def show_currency_converter(self) -> bool:
        """Check if currency converter should be shown in navigation."""
        return self.enabled
    
    def show_api_management(self) -> bool:
        """Check if API key management should be shown in navigation."""
        return self.enabled
    
    def show_subscription_management(self) -> bool:
        """Check if subscription management should be shown in navigation."""
        return self.enabled
    
    def show_balance_management(self) -> bool:
        """Check if balance management should be shown in navigation."""
        return self.enabled
    
    def show_transaction_history(self) -> bool:
        """Check if transaction history should be shown in navigation."""
        return self.enabled
    
    def show_currency_management(self) -> bool:
        """Check if currency management should be shown in navigation."""
        return self.enabled
    
    def show_rate_limiting_features(self) -> bool:
        """Check if rate limiting features should be shown."""
        return self.enabled and self.rate_limiting_enabled
    
    def show_usage_tracking_features(self) -> bool:
        """Check if usage tracking features should be shown."""
        return self.enabled and self.usage_tracking_enabled
    
    def get_enabled_navigation_items(self) -> List[str]:
        """
        Get list of enabled navigation items for dynamic UI generation.
        
        Returns:
            List of enabled navigation item identifiers
        """
        items = []
        
        if not self.enabled:
            return items
        
        # Core features (always enabled if payments is enabled)
        items.extend([
            'payment_dashboard',
            'payments_admin',
            'currencies_admin',
            'networks_admin',
            'provider_currencies_admin',
        ])
        
        # Optional features based on configuration
        if self.show_webhook_dashboard():
            items.append('webhook_dashboard')
        
        if self.show_payment_creation():
            items.append('payment_creation')
        
        if self.show_currency_converter():
            items.append('currency_converter')
        
        if self.show_api_management():
            items.extend(['api_keys_admin', 'endpoint_groups_admin'])
        
        if self.show_subscription_management():
            items.extend(['subscriptions_admin', 'tariffs_admin'])
        
        if self.show_balance_management():
            items.append('balances_admin')
        
        if self.show_transaction_history():
            items.append('transactions_admin')
        
        return items
    
    @classmethod
    def get_current_config(cls) -> 'PaymentsConfig':
        """
        Get current payments configuration from django-cfg.
        
        Uses PaymentsConfigManager for consistent access.
        """
        try:
            # Import here to avoid circular dependencies
            from django_cfg.apps.payments.config.django_cfg_integration import PaymentsConfigManager
            return PaymentsConfigManager.get_payments_config_safe()
        except Exception:
            return cls()
