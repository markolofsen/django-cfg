"""
URLs for Django CFG RPC Dashboard admin integration.

Automatically included when django_ipc is enabled.
"""

from .urls import urlpatterns, app_name

__all__ = ['urlpatterns', 'app_name']
