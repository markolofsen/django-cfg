"""
Universal Payment System v2.0 - Django App Configuration.

Simplified payment system focused on NowPayments with extensible architecture.
"""

from django.apps import AppConfig
from django_cfg.modules.django_logger import get_logger

logger = get_logger("payments")


class PaymentsConfig(AppConfig):
    """Payment system app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.apps.payments'
    verbose_name = 'Universal Payment System v2.0'
    
    def ready(self):
        """Initialize payment system when Django starts."""
        logger.info("Initializing Universal Payment System v2.0")
        
        # Import signals to register them
        try:
            from . import signals  # noqa: F401
            logger.info("Payment signals registered successfully")
        except ImportError as e:
            logger.warning(f"Failed to import payment signals: {e}")
        
        # Initialize provider registry
        try:
            from .services.providers.registry import get_provider_registry
            registry = get_provider_registry()
            logger.info(f"Provider registry initialized with {len(registry.get_available_providers())} providers")
        except Exception as e:
            logger.error(f"Failed to initialize provider registry: {e}")
        
        # Initialize cache services
        try:
            from .services.cache import get_cache_service
            cache_service = get_cache_service()
            logger.info("Cache service initialized successfully")
        except Exception as e:
            logger.warning(f"Cache service initialization failed: {e}")
        
        logger.info("Universal Payment System v2.0 ready")
