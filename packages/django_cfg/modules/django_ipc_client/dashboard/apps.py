"""
Django AppConfig for RPC Dashboard.

Enables template and static file discovery.
"""

from django.apps import AppConfig


class RPCDashboardConfig(AppConfig):
    """
    RPC Dashboard application configuration.

    Enables:
    - Template discovery from templates/django_ipc_dashboard/
    - Static file discovery from static/django_ipc_dashboard/
    """

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_cfg.modules.django_ipc_client.dashboard'
    label = 'django_ipc_dashboard'
    verbose_name = 'Django-CFG RPC Dashboard'
