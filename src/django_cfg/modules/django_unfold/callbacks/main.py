"""
Main Unfold Dashboard Callbacks

Combines all callback modules into a single interface.
"""

import logging
import json
from typing import Dict, Any

from django.utils import timezone
from django.conf import settings

from ...base import BaseCfgModule
from ..models.dashboard import DashboardData

from .statistics import StatisticsCallbacks
from .system import SystemCallbacks
from .actions import ActionsCallbacks
from .charts import ChartsCallbacks
from .commands import CommandsCallbacks
from .revolution import RevolutionCallbacks
from .users import UsersCallbacks
from .base import get_user_admin_urls

logger = logging.getLogger(__name__)


class UnfoldCallbacks(
    BaseCfgModule,
    StatisticsCallbacks,
    SystemCallbacks,
    ActionsCallbacks,
    ChartsCallbacks,
    CommandsCallbacks,
    RevolutionCallbacks,
    UsersCallbacks
):
    """
    Main Unfold dashboard callbacks with full system monitoring.
    
    Combines all callback modules using multiple inheritance for
    clean separation of concerns while maintaining a single interface.
    """
    
    def main_dashboard_callback(self, request, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main dashboard callback function with comprehensive system data.

        Returns all dashboard data as Pydantic models for type safety.
        """
        try:
            # Get dashboard data using Pydantic models
            user_stats = self.get_user_statistics()
            support_stats = self.get_support_statistics()
            system_health = self.get_system_health()
            quick_actions = self.get_quick_actions()
            
            # Combine all stat cards
            all_stats = user_stats + support_stats

            dashboard_data = DashboardData(
                stat_cards=all_stats,
                system_health=system_health,
                quick_actions=quick_actions,
                last_updated=timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                environment=getattr(settings, "ENVIRONMENT", "development"),
            )

            # Convert to template context (using to_dict for Unfold compatibility)
            cards_data = [card.to_dict() for card in dashboard_data.stat_cards]

            context.update({
                # Statistics cards
                "cards": cards_data,
                "user_stats": [card.to_dict() for card in user_stats],
                "support_stats": [card.to_dict() for card in support_stats],
                
                # System health (convert to dict for template)
                "system_health": {
                    item.component + "_status": item.status
                    for item in dashboard_data.system_health
                },
                
                # System metrics
                "system_metrics": self.get_system_metrics(),
                
                # Quick actions
                "quick_actions": [
                    action.model_dump() for action in dashboard_data.quick_actions
                ],
                
                # Additional categorized actions
                "admin_actions": [
                    action.model_dump()
                    for action in dashboard_data.quick_actions
                    if action.category == "admin"
                ],
                "support_actions": [
                    action.model_dump()
                    for action in dashboard_data.quick_actions
                    if action.category == "support"
                ],
                "system_actions": [
                    action.model_dump()
                    for action in dashboard_data.quick_actions
                    if action.category == "system"
                ],
                
                # Revolution zones
                "zones_table": {
                    "headers": [
                        {"label": "Zone"},
                        {"label": "Title"},
                        {"label": "Apps"},
                        {"label": "Endpoints"},
                        {"label": "Status"},
                        {"label": "Actions"},
                    ],
                    "rows": self.get_revolution_zones_data()[0],
                },
                
                # Recent users
                "recent_users": self.get_recent_users(),
                "user_admin_urls": get_user_admin_urls(),
                
                # App statistics
                "app_statistics": self.get_app_statistics(),
                
                # Django commands
                "django_commands": self.get_django_commands(),
                
                   # Charts data - serialize to JSON for JavaScript
                   "charts": {
                       "user_registrations_json": json.dumps(self.get_user_registration_chart_data()),
                       "user_activity_json": json.dumps(self.get_user_activity_chart_data()),
                       "user_registrations": self.get_user_registration_chart_data(),
                       "user_activity": self.get_user_activity_chart_data(),
                   },
                   
                   # Activity tracker data
                   "activity_tracker": self.get_activity_tracker_data(),
                
                
                # Meta information
                "last_updated": dashboard_data.last_updated,
                "environment": dashboard_data.environment,
                "dashboard_title": "Django CFG Dashboard",
            })

            # Log charts data for debugging
            charts_data = context.get('charts', {})
            logger.info(f"Charts data added to context: {list(charts_data.keys())}")
            if 'user_registrations' in charts_data:
                reg_data = charts_data['user_registrations']
                logger.info(f"Registration chart labels: {reg_data.get('labels', [])}")
            if 'user_activity' in charts_data:
                act_data = charts_data['user_activity']
                logger.info(f"Activity chart labels: {act_data.get('labels', [])}")
            
            # Log recent users data for debugging
            recent_users_data = context.get('recent_users', [])
            logger.info(f"Recent users data count: {len(recent_users_data)}")
            if recent_users_data:
                logger.info(f"First user: {recent_users_data[0].get('username', 'N/A')}")
            
            # Log activity tracker data for debugging
            activity_tracker_data = context.get('activity_tracker', [])
            logger.info(f"Activity tracker data count: {len(activity_tracker_data)}")

            return context

        except Exception as e:
            logger.error(f"Dashboard callback error: {e}")
            # Return minimal safe defaults
            context.update({
                "cards": [
                    {
                        "title": "System Error",
                        "value": "N/A",
                        "icon": "error",
                        "color": "danger",
                        "description": "Dashboard data unavailable"
                    }
                ],
                "system_health": {},
                "quick_actions": [],
                "last_updated": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": f"Dashboard error: {str(e)}",
            })
            return context
