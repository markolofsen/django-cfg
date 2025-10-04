"""
RPC Dashboard for django-cfg-rpc-client.

Provides real-time monitoring and visualization of RPC activity.
"""

default_app_config = 'django_cfg.modules.django_ipc_client.dashboard.apps.RPCDashboardConfig'

from .monitor import RPCMonitor

__all__ = ['RPCMonitor']
