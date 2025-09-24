"""
Quick actions callbacks.
"""

import logging
from typing import List

from ..models.dashboard import QuickAction
from ..icons import Icons
from .base import get_user_admin_urls

logger = logging.getLogger(__name__)


class ActionsCallbacks:
    """Quick actions callbacks."""
    
    def get_quick_actions(self) -> List[QuickAction]:
        """Get quick action buttons as Pydantic models."""
        # Get user admin URLs dynamically based on AUTH_USER_MODEL
        user_admin_urls = get_user_admin_urls()
        
        actions = [
            QuickAction(
                title="Add User",
                description="Create new user account",
                icon=Icons.PERSON_ADD,
                link=user_admin_urls["add"],
                color="primary",
                category="admin",
            ),
            QuickAction(
                title="Support Tickets",
                description="Manage support tickets",
                icon=Icons.SUPPORT_AGENT,
                link="admin:django_cfg_support_ticket_changelist",
                color="primary",
                category="support",
            ),
            QuickAction(
                title="Health Check",
                description="System health status",
                icon=Icons.HEALTH_AND_SAFETY,
                link="/cfg/health/",
                color="success",
                category="system",
            ),
        ] 
        
        return actions
