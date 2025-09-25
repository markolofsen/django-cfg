"""
Payment configuration module.

Handles loading and managing payment configurations from project settings.
"""

from typing import Optional
from django_cfg.modules.django_logger import get_logger

from django_cfg.modules.base import BaseCfgModule
from .settings import PaymentsSettings

logger = get_logger("config_module")


class PaymentsCfgModule(BaseCfgModule):
    """Payment configuration module for django-cfg."""
    
    def __init__(self):
        super().__init__()
        self.settings_class = PaymentsSettings
        self._settings_cache = None
    
    def get_config(self) -> PaymentsSettings:
        """Get payments configuration."""
        if self._settings_cache is None:
            project_config = super().get_config()
            if project_config:
                self._settings_cache = self.load_from_project_config(project_config)
            else:
                self._settings_cache = PaymentsSettings()
        return self._settings_cache
    
    def reset_cache(self):
        """Reset configuration cache."""
        self._settings_cache = None
    
    def load_from_project_config(self, config) -> PaymentsSettings:
        """Load payments configuration from main project config."""
        
        # Load from new PaymentsConfig if available
        if hasattr(config, 'payments') and config.payments:
            # Convert List[PaymentProviderConfig] to Dict[str, PaymentProviderConfig]
            providers = {}
            for provider in config.payments.providers:
                providers[provider.name] = provider
            
            return PaymentsSettings(
                enabled=config.payments.enabled,
                debug_mode=getattr(config, 'debug', False),
                providers=providers,
                security=config.payments.security,
                rate_limits=config.payments.rate_limits,
                notifications=config.payments.notifications,
                subscriptions=config.payments.subscriptions,
                enable_crypto_payments=config.payments.enable_crypto_payments,
                enable_fiat_payments=config.payments.enable_fiat_payments,
                enable_subscription_system=config.payments.enable_subscription_system,
                enable_balance_system=config.payments.enable_balance_system,
                enable_api_key_system=config.payments.enable_api_key_system,
                enable_webhook_processing=config.payments.enable_webhook_processing,
                enable_billing_utils=config.payments.enable_billing_utils
            )
        else:
            # Fallback: Return default settings if no PaymentsConfig found
            logger.warning("No PaymentsConfig found, using default settings")
            return PaymentsSettings(
                enabled=False,
                debug_mode=getattr(config, 'debug', False)
            )