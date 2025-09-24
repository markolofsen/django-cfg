"""
Statistics callbacks for dashboard.
"""

import logging
from typing import List, Dict, Any
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.apps import apps

from ..models.dashboard import StatCard
from ..icons import Icons

logger = logging.getLogger(__name__)


class StatisticsCallbacks:
    """Statistics-related callbacks."""
    
    def _get_user_model(self):
        """Get the user model safely."""
        return get_user_model()
    
    def get_user_statistics(self) -> List[StatCard]:
        """Get user-related statistics as Pydantic models."""
        try:
            User = self._get_user_model()

            total_users = User.objects.count()
            active_users = User.objects.filter(is_active=True).count()
            new_users_7d = User.objects.filter(
                date_joined__gte=timezone.now() - timedelta(days=7)
            ).count()
            staff_users = User.objects.filter(is_staff=True).count()

            return [
                StatCard(
                    title="Total Users",
                    value=f"{total_users:,}",
                    icon=Icons.PEOPLE,
                    change=f"+{new_users_7d}" if new_users_7d > 0 else None,
                    change_type="positive" if new_users_7d > 0 else "neutral",
                    description="Registered users",
                ),
                StatCard(
                    title="Active Users",
                    value=f"{active_users:,}",
                    icon=Icons.PERSON,
                    change=(
                        f"{(active_users/total_users*100):.1f}%"
                        if total_users > 0
                        else "0%"
                    ),
                    change_type=(
                        "positive" if active_users > total_users * 0.7 else "neutral"
                    ),
                    description="Currently active",
                ),
                StatCard(
                    title="New This Week",
                    value=f"{new_users_7d:,}",
                    icon=Icons.PERSON_ADD,
                    change_type="positive" if new_users_7d > 0 else "neutral",
                    description="Last 7 days",
                ),
                StatCard(
                    title="Staff Members",
                    value=f"{staff_users:,}",
                    icon=Icons.ADMIN_PANEL_SETTINGS,
                    change=(
                        f"{(staff_users/total_users*100):.1f}%" if total_users > 0 else "0%"
                    ),
                    change_type="neutral",
                    description="Administrative access",
                ),
            ]
        except Exception as e:
            logger.error(f"Error getting user statistics: {e}")
            return [
                StatCard(
                    title="Users",
                    value="N/A",
                    icon=Icons.PEOPLE,
                    description="Data unavailable",
                )
            ]

    def get_support_statistics(self) -> List[StatCard]:
        """Get support ticket statistics as Pydantic models."""
        try:
            # Check if support is enabled
            if not self.is_support_enabled():
                return []
                
            from django_cfg.apps.support.models import Ticket
            
            total_tickets = Ticket.objects.count()
            open_tickets = Ticket.objects.filter(status='open').count()
            resolved_tickets = Ticket.objects.filter(status='resolved').count()
            new_tickets_7d = Ticket.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count()
            
            return [
                StatCard(
                    title="Total Tickets",
                    value=f"{total_tickets:,}",
                    icon=Icons.SUPPORT_AGENT,
                    change=f"+{new_tickets_7d}" if new_tickets_7d > 0 else None,
                    change_type="positive" if new_tickets_7d > 0 else "neutral",
                    description="All support tickets",
                ),
                StatCard(
                    title="Open Tickets",
                    value=f"{open_tickets:,}",
                    icon=Icons.PENDING,
                    change=(
                        f"{(open_tickets/total_tickets*100):.1f}%"
                        if total_tickets > 0
                        else "0%"
                    ),
                    change_type=(
                        "negative" if open_tickets > total_tickets * 0.3 
                        else "positive" if open_tickets == 0 
                        else "neutral"
                    ),
                    description="Awaiting response",
                ),
                StatCard(
                    title="Resolved",
                    value=f"{resolved_tickets:,}",
                    icon=Icons.CHECK_CIRCLE,
                    change=(
                        f"{(resolved_tickets/total_tickets*100):.1f}%"
                        if total_tickets > 0
                        else "0%"
                    ),
                    change_type="positive",
                    description="Successfully resolved",
                ),
                StatCard(
                    title="New This Week",
                    value=f"{new_tickets_7d:,}",
                    icon=Icons.NEW_RELEASES,
                    change_type="positive" if new_tickets_7d > 0 else "neutral",
                    description="Last 7 days",
                ),
            ]
        except Exception as e:
            logger.error(f"Error getting support statistics: {e}")
            return [
                StatCard(
                    title="Support",
                    value="N/A",
                    icon=Icons.SUPPORT_AGENT,
                    description="Data unavailable",
                )
            ]

    def get_app_statistics(self) -> Dict[str, Any]:
        """Get statistics for all apps and their models."""
        stats = {"apps": {}, "total_records": 0, "total_models": 0, "total_apps": 0}

        # Get all installed apps
        for app_config in apps.get_app_configs():
            app_label = app_config.label

            # Skip system apps
            if app_label in ["admin", "contenttypes", "sessions", "auth"]:
                continue

            app_stats = self._get_app_stats(app_label)
            if app_stats:
                stats["apps"][app_label] = app_stats
                stats["total_records"] += app_stats.get("total_records", 0)
                stats["total_models"] += app_stats.get("model_count", 0)
                stats["total_apps"] += 1

        return stats

    def _get_app_stats(self, app_label: str) -> Dict[str, Any]:
        """Get statistics for a specific app."""
        try:
            app_config = apps.get_app_config(app_label)
            # Convert generator to list to avoid len() error
            models_list = list(app_config.get_models())

            if not models_list:
                return None

            app_stats = {
                "name": app_config.verbose_name or app_label.title(),
                "models": {},
                "total_records": 0,
                "model_count": len(models_list),
            }

            for model in models_list:
                try:
                    # Get model statistics
                    model_stats = self._get_model_stats(model)
                    if model_stats:
                        app_stats["models"][model._meta.model_name] = model_stats
                        app_stats["total_records"] += model_stats.get("count", 0)
                except Exception:
                    continue

            return app_stats

        except Exception:
            return None

    def _get_model_stats(self, model) -> Dict[str, Any]:
        """Get statistics for a specific model."""
        try:
            # Get basic model info
            model_stats = {
                "name": model._meta.verbose_name_plural
                or model._meta.verbose_name
                or model._meta.model_name,
                "count": model.objects.count(),
                "fields_count": len(model._meta.fields),
                "admin_url": f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist",
            }

            return model_stats

        except Exception:
            return None

    def is_support_enabled(self) -> bool:
        """Check if support module is enabled."""
        try:
            from django_cfg.apps.support.models import Ticket
            return True
        except ImportError:
            return False
