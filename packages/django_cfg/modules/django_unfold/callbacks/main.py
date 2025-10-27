"""
Main Unfold Dashboard Callbacks

Combines all callback modules into a single interface.
"""

import json
import logging
from typing import Any, Dict

from django.template.loader import render_to_string
from django.utils import timezone

from django_cfg.core.state import get_current_config
from django_cfg.modules.django_dashboard.debug import save_dashboard_render
from django_cfg.modules.django_dashboard.sections.commands import CommandsSection
from django_cfg.modules.django_dashboard.sections.documentation import DocumentationSection

# Import new dashboard sections
from django_cfg.modules.django_dashboard.sections.overview import OverviewSection
from django_cfg.modules.django_dashboard.sections.stats import StatsSection
from django_cfg.modules.django_dashboard.sections.system import SystemSection
from django_cfg.modules.django_dashboard.sections.widgets import WidgetsSection

from ...base import BaseCfgModule
from ..models.dashboard import DashboardData
from .actions import ActionsCallbacks
from .base import get_user_admin_urls
from .charts import ChartsCallbacks
from .commands import CommandsCallbacks
from .apizones import OpenAPIClientCallbacks
from .statistics import StatisticsCallbacks
from .system import SystemCallbacks
from .users import UsersCallbacks

logger = logging.getLogger(__name__)


class UnfoldCallbacks(
    BaseCfgModule,
    StatisticsCallbacks,
    SystemCallbacks,
    ActionsCallbacks,
    ChartsCallbacks,
    CommandsCallbacks,
    OpenAPIClientCallbacks,
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
            # Get current config for debug and environment settings
            config = get_current_config()

            # Log debug status
            debug_enabled = config and config.debug
            logger.info(f"[DEBUG MODE] Dashboard rendering with debug={debug_enabled} (config.debug={getattr(config, 'debug', 'N/A')})")

            # Get dashboard data first
            user_stats = self.get_user_statistics()
            support_stats = self.get_support_statistics()
            system_health = self.get_system_health()
            quick_actions = self.get_quick_actions()

            # Parse time range from query parameters (default: 7 days)
            try:
                time_range = int(request.GET.get('range', 7))
                # Validate range
                if time_range not in [7, 30, 90]:
                    time_range = 7
            except (ValueError, TypeError):
                time_range = 7

            # Create navigation for time range filter
            navigation = [
                {
                    "title": "7 Days",
                    "link": "?range=7",
                    "active": time_range == 7,
                    "icon": "calendar_today"
                },
                {
                    "title": "30 Days",
                    "link": "?range=30",
                    "active": time_range == 30,
                    "icon": "date_range"
                },
                {
                    "title": "90 Days",
                    "link": "?range=90",
                    "active": time_range == 90,
                    "icon": "event"
                },
            ]

            # Render new dashboard sections
            try:
                # Create overview section and pass quick_actions + time_range + navigation
                overview_sec = OverviewSection(request)
                # Add quick_actions, time_range, and navigation to render context
                overview_section = overview_sec.render(
                    quick_actions=[action.model_dump() for action in quick_actions],
                    time_range=time_range,
                    navigation=navigation
                )
            except Exception as e:
                logger.error(f"Failed to render overview section: {e}", exc_info=True)
                overview_section = None

            try:
                stats_section = StatsSection(request).render()
            except Exception as e:
                logger.error(f"Failed to render stats section: {e}", exc_info=True)
                stats_section = None

            try:
                system_section = SystemSection(request).render()
            except Exception as e:
                logger.error(f"Failed to render system section: {e}", exc_info=True)
                system_section = None

            try:
                # Generate documentation content first
                doc_section = DocumentationSection(request)
                doc_data = doc_section.get_data_old()  # Get markdown/HTML content
                documentation_content = doc_data.get('documentation_content') or doc_data.get('readme_content', '')
                documentation_section = doc_section.render()
            except Exception as e:
                logger.error(f"Failed to render documentation section: {e}", exc_info=True)
                documentation_section = None
                documentation_content = None

            try:
                # Render commands section with documentation content
                commands_section = CommandsSection(request).render(
                    documentation_content=documentation_content
                )
            except Exception as e:
                logger.error(f"Failed to render commands section: {e}", exc_info=True)
                commands_section = None

            # Extract custom widgets from context if provided by project's dashboard_callback
            custom_widgets = context.get('custom_widgets', [])
            custom_metrics = {}

            # Extract all metric-like variables from context for widget template resolution
            # This allows dashboard_callback to add metrics like: context['total_users'] = 123
            for key, value in context.items():
                if key not in ['request', 'cards', 'system_health', 'quick_actions'] and isinstance(value, (int, float, str)):
                    custom_metrics[key] = value

            try:
                # Render widgets section with custom widgets and metrics from callback
                widgets_section = WidgetsSection(request).render(
                    custom_widgets=custom_widgets,
                    custom_metrics=custom_metrics
                )
            except Exception as e:
                logger.error(f"Failed to render widgets section: {e}", exc_info=True)
                widgets_section = None

            # Combine all stat cards (data already loaded above)
            all_stats = user_stats + support_stats

            dashboard_data = DashboardData(
                stat_cards=all_stats,
                system_health=system_health,
                quick_actions=quick_actions,
                last_updated=timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                environment=getattr(config.environment, 'name', 'development') if config and hasattr(config, 'environment') else "development",
            )

            # Convert to template context (using to_dict for Unfold compatibility)
            cards_data = [card.to_dict() for card in dashboard_data.stat_cards]

            context.update({
                # New dashboard sections (rendered HTML)
                "overview_section": overview_section,
                "stats_section": stats_section,
                "system_section": system_section,
                "commands_section": commands_section,
                "documentation_section": documentation_section,
                "widgets_section": widgets_section,

                # Documentation content for commands tab
                "documentation_content": documentation_content,

                # Statistics cards
                "cards": cards_data,
                "user_stats": [card.to_dict() for card in user_stats],
                "support_stats": [card.to_dict() for card in support_stats],

                # System health (convert to dict for template)
                "system_health": {
                    item.component + "_status": item.status
                    for item in dashboard_data.system_health
                },

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

                # OpenAPI Client groups
                "zones_table": {
                    "headers": [
                        {"label": "Zone"},
                        {"label": "Title"},
                        {"label": "Apps"},
                        {"label": "Endpoints"},
                        {"label": "Status"},
                        {"label": "Actions"},
                    ],
                    "rows": OpenAPIClientCallbacks().get_openapi_groups_data()[0],
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
            # charts_data = context.get('charts', {})
            # # logger.info(f"Charts data added to context: {list(charts_data.keys())}")
            # if 'user_registrations' in charts_data:
            #     reg_data = charts_data['user_registrations']
            #     logger.info(f"Registration chart labels: {reg_data.get('labels', [])}")
            # if 'user_activity' in charts_data:
            #     act_data = charts_data['user_activity']
            #     logger.info(f"Activity chart labels: {act_data.get('labels', [])}")

            # # Log recent users data for debugging
            # recent_users_data = context.get('recent_users', [])
            # logger.info(f"Recent users data count: {len(recent_users_data)}")
            # if recent_users_data:
            #     logger.info(f"First user: {recent_users_data[0].get('username', 'N/A')}")

            # # Log activity tracker data for debugging
            # activity_tracker_data = context.get('activity_tracker', [])
            # logger.info(f"Activity tracker data count: {len(activity_tracker_data)}")

            # Debug: save full rendered page (only in debug mode)
            # DISABLED: Commenting out dashboard render saving to disk
            # if config and config.debug:
            #     try:
            #         full_html = render_to_string('admin/index.html', context, request)
            #         save_dashboard_render(full_html, name='dashboard_full_page', context=context)
            #     except Exception as e:
            #         logger.error(f"Failed to save full dashboard render: {e}", exc_info=True)

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
