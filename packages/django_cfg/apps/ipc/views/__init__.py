"""
Views for IPC/RPC module.
"""

from .dashboard import dashboard_view
from .viewsets import RPCMonitorViewSet

__all__ = ['RPCMonitorViewSet', 'dashboard_view']
