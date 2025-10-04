"""
Django app configuration for django_cfg.

Handles automatic registration of integrations like Constance admin.
"""

from django.apps import AppConfig
from django.conf import settings
from django.contrib import admin

class DjangoCfgConfig(AppConfig):
    """Configuration for django_cfg app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg"
    verbose_name = "Django Configuration"

    def ready(self):
        """Called when Django is ready - register integrations."""
        self._register_constance_admin()
    
    def _register_constance_admin(self):
        """Register Constance admin with Unfold integration."""
        try:
            
            # Check if Constance is configured
            if not (hasattr(settings, 'CONSTANCE_CONFIG') and settings.CONSTANCE_CONFIG):
                return
            
            # Import required modules
            from constance.admin import Config, ConstanceAdmin
            from unfold.admin import ModelAdmin

            # Create custom admin class that inherits from both ConstanceAdmin and Unfold ModelAdmin
            class ConstanceConfigAdmin(ConstanceAdmin, ModelAdmin):
                """Constance admin with Unfold integration."""
                pass
            
            # Directly override the registry entry to replace default admin
            admin.site._registry[Config] = ConstanceConfigAdmin(Config, admin.site)
            
        except ImportError:
            # Constance not available - skip registration
            pass
        except Exception:
            # Any other error - skip registration silently
            pass
