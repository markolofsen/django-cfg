"""
Next.js Admin Integration Module

Provides seamless integration between Django admin and external Next.js admin panel.
"""

from .models.config import NextJsAdminConfig

__all__ = ['NextJsAdminConfig']

# Django app configuration
default_app_config = 'django_cfg.modules.nextjs_admin.apps.NextJsAdminConfig'
