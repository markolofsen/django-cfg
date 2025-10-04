"""
Views package for Django CFG Tasks app.

Provides organized views structure:
- api: DRF ViewSets for API endpoints
- dashboard: Dashboard template views
- base: Shared functionality and mixins
"""

from .api import TaskManagementViewSet
from .dashboard import dashboard_view

__all__ = [
    'TaskManagementViewSet',
    'dashboard_view'
]
