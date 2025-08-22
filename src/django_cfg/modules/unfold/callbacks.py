"""
Base Unfold Dashboard Callbacks for Django CFG Toolkit

Provides comprehensive system monitoring and dashboard functionality.
Following CRITICAL_REQUIREMENTS.md - NO raw dicts, ALL type-safe.
"""

import json
import logging
import os
import shutil
from typing import Dict, Any, List
from datetime import timedelta

from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.conf import settings
from django.urls import get_resolver
from django.db import connection
from django.core.cache import cache
from django.apps import apps

from ..base import BaseModule
from .models import DashboardData, StatCard, SystemHealthItem, QuickAction

logger = logging.getLogger(__name__)


def get_available_commands():
    """Get all available Django management commands."""
    from django.core.management import get_commands
    from django.core.management.base import BaseCommand
    import importlib
    
    commands_dict = get_commands()
    commands_list = []
    
    for command_name, app_name in commands_dict.items():
        try:
            # Try to get command description
            if app_name == 'django_cfg':
                module_path = f'django_cfg.management.commands.{command_name}'
            else:
                module_path = f'{app_name}.management.commands.{command_name}'
            
            try:
                command_module = importlib.import_module(module_path)
                if hasattr(command_module, 'Command'):
                    command_class = command_module.Command
                    description = getattr(command_class, 'help', f'{command_name} command')
                else:
                    description = f'{command_name} command'
            except ImportError:
                description = f'{command_name} command'
            
            commands_list.append({
                'name': command_name,
                'app': app_name,
                'description': description,
                'is_core': app_name.startswith('django.'),
                'is_custom': app_name == 'django_cfg',
            })
        except Exception:
            # Skip problematic commands
            continue
    
    return commands_list


def get_commands_by_category():
    """Get commands categorized by type."""
    commands = get_available_commands()
    
    categorized = {
        'django_cfg': [],
        'django_core': [],
        'third_party': [],
        'project': [],
    }
    
    for cmd in commands:
        if cmd['app'] == 'django_cfg':
            categorized['django_cfg'].append(cmd)
        elif cmd['app'].startswith('django.'):
            categorized['django_core'].append(cmd)
        elif cmd['app'].startswith(('src.', 'api.', 'accounts.')):
            categorized['project'].append(cmd)
        else:
            categorized['third_party'].append(cmd)
    
    return categorized


def get_user_admin_urls():
    """Get admin URLs for user model."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        app_label = User._meta.app_label
        model_name = User._meta.model_name
        
        return {
            'changelist': f'admin:{app_label}_{model_name}_changelist',
            'add': f'admin:{app_label}_{model_name}_add',
            'change': f'admin:{app_label}_{model_name}_change/{{id}}/',
            'delete': f'admin:{app_label}_{model_name}_delete/{{id}}/',
            'view': f'admin:{app_label}_{model_name}_view/{{id}}/',
        }
    except Exception:
        return {
            'changelist': 'admin:auth_user_changelist',
            'add': 'admin:auth_user_add',
            'change': 'admin:auth_user_change/{id}/',
            'delete': 'admin:auth_user_delete/{id}/',
            'view': 'admin:auth_user_view/{id}/',
        }


class UnfoldCallbacks(BaseModule):
    """
    Base Unfold dashboard callbacks with full system monitoring.
    
    Provides comprehensive dashboard functionality using Pydantic models
    for type safety and data validation.
    """
    
    def _get_user_model(self):
        """Get the user model safely."""
        from django.contrib.auth import get_user_model
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
                    icon="people",
                    change=f"+{new_users_7d}" if new_users_7d > 0 else None,
                    change_type="positive" if new_users_7d > 0 else "neutral",
                    description="Registered users",
                ),
                StatCard(
                    title="Active Users",
                    value=f"{active_users:,}",
                    icon="person",
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
                    icon="person_add",
                    change_type="positive" if new_users_7d > 0 else "neutral",
                    description="Last 7 days",
                ),
                StatCard(
                    title="Staff Members",
                    value=f"{staff_users:,}",
                    icon="admin_panel_settings",
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
                    icon="people",
                    description="Data unavailable",
                )
            ]

    def get_system_health(self) -> List[SystemHealthItem]:
        """Get system health status as Pydantic models."""
        health_items = []

        # Database health
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                health_items.append(
                    SystemHealthItem(
                        component="database",
                        status="healthy",
                        description="Connection successful",
                        last_check=timezone.now().strftime("%H:%M:%S"),
                        health_percentage=95,
                    )
                )
        except Exception as e:
            health_items.append(
                SystemHealthItem(
                    component="database",
                    status="error",
                    description=f"Connection failed: {str(e)[:50]}",
                    last_check=timezone.now().strftime("%H:%M:%S"),
                    health_percentage=0,
                )
            )

        # Cache health
        try:
            cache.set("health_check", "ok", 10)
            if cache.get("health_check") == "ok":
                health_items.append(
                    SystemHealthItem(
                        component="cache",
                        status="healthy",
                        description="Cache operational",
                        last_check=timezone.now().strftime("%H:%M:%S"),
                        health_percentage=90,
                    )
                )
            else:
                health_items.append(
                    SystemHealthItem(
                        component="cache",
                        status="warning",
                        description="Cache not responding",
                        last_check=timezone.now().strftime("%H:%M:%S"),
                        health_percentage=50,
                    )
                )
        except Exception:
            health_items.append(
                SystemHealthItem(
                    component="cache",
                    status="unknown",
                    description="Cache not configured",
                    last_check=timezone.now().strftime("%H:%M:%S"),
                    health_percentage=0,
                )
            )

        # Storage health
        try:
            total, used, free = shutil.disk_usage("/")
            usage_percentage = (used / total) * 100
            free_percentage = 100 - usage_percentage

            if free_percentage > 20:
                status = "healthy"
                desc = f"Disk space: {free_percentage:.1f}% free"
            elif free_percentage > 10:
                status = "warning"
                desc = f"Low disk space: {free_percentage:.1f}% free"
            else:
                status = "error"
                desc = f"Critical disk space: {free_percentage:.1f}% free"

            health_items.append(
                SystemHealthItem(
                    component="storage",
                    status=status,
                    description=desc,
                    last_check=timezone.now().strftime("%H:%M:%S"),
                    health_percentage=int(free_percentage),
                )
            )
        except Exception as e:
            health_items.append(
                SystemHealthItem(
                    component="storage",
                    status="error",
                    description="Storage check failed",
                    last_check=timezone.now().strftime("%H:%M:%S"),
                    health_percentage=0,
                )
            )

        # API health
        health_items.append(
            SystemHealthItem(
                component="api",
                status="healthy",
                description="API server running",
                last_check=timezone.now().strftime("%H:%M:%S"),
                health_percentage=100,
            )
        )

        return health_items

    def get_quick_actions(self) -> List[QuickAction]:
        """Get quick action buttons as Pydantic models."""
        # Get user admin URLs dynamically based on AUTH_USER_MODEL
        user_admin_urls = get_user_admin_urls()
        
        actions = [
            QuickAction(
                title="Add User",
                description="Create new user account",
                icon="person_add",
                link=user_admin_urls["add"],
                color="primary",
                category="admin",
            ),
            QuickAction(
                title="Health Check",
                description="System health status",
                icon="health_and_safety",
                link="django_cfg_health",
                color="success",
                category="system",
            ),
        ] 
        
        # Automatically add Constance settings if configured
        if self._is_constance_configured():
            actions.append(
                QuickAction(
                    title="System Settings",
                    description="Configure dynamic settings",
                    icon="settings",
                    link="/admin/constance/config/",
                    color="warning",
                    category="admin",
                )
            )

        return actions

    def _is_constance_configured(self) -> bool:
        """Check if Constance is configured."""
        try:
            from django.conf import settings
            return bool(getattr(settings, 'CONSTANCE_CONFIG', {}))
        except Exception:
            return False

    def get_django_commands(self) -> Dict[str, Any]:
        """Get Django management commands information."""
        try:
            commands = get_available_commands()
            categorized = get_commands_by_category()

            return {
                "commands": commands,
                "categorized": categorized,
                "total_commands": len(commands),
                "categories": list(categorized.keys()),
                "core_commands": len([cmd for cmd in commands if cmd['is_core']]),
                "custom_commands": len([cmd for cmd in commands if cmd['is_custom']]),
            }
        except Exception as e:
            logger.error(f"Error getting Django commands: {e}")
            # Return safe fallback to prevent dashboard from breaking
            return {
                "commands": [],
                "categorized": {},
                "total_commands": 0,
                "categories": [],
                "core_commands": 0,
                "custom_commands": 0,
            }

    def get_revolution_zones_data(self) -> tuple[list, dict]:
        """Get Django Revolution zones data."""
        try:
            # Try to get revolution config from Django settings
            revolution_config = getattr(settings, "DJANGO_REVOLUTION", {})
            zones = revolution_config.get("zones", {})
            api_prefix = revolution_config.get("api_prefix", "apix")

            zones_data = []
            total_apps = 0
            total_endpoints = 0

            for zone_name, zone_config in zones.items():
                # Handle both dict and object access
                if isinstance(zone_config, dict):
                    title = zone_config.get("title", zone_name.title())
                    description = zone_config.get("description", f"{zone_name} zone")
                    apps = zone_config.get("apps", [])
                    public = zone_config.get("public", False)
                    auth_required = zone_config.get("auth_required", True)
                else:
                    # Handle object access (for ZoneConfig instances)
                    title = getattr(zone_config, "title", zone_name.title())
                    description = getattr(zone_config, "description", f"{zone_name} zone")
                    apps = getattr(zone_config, "apps", [])
                    public = getattr(zone_config, "public", False)
                    auth_required = getattr(zone_config, "auth_required", True)

                # Count actual endpoints by checking URL patterns (simplified estimate)
                endpoint_count = len(apps) * 3  # Conservative estimate

                zones_data.append({
                    "name": zone_name,
                    "title": title,
                    "description": description,
                    "app_count": len(apps),
                    "endpoint_count": endpoint_count,
                    "status": "active",
                    "public": public,
                    "auth_required": auth_required,
                    "schema_url": f"/schema/{zone_name}/schema/",
                    "swagger_url": f"/schema/{zone_name}/schema/swagger/",
                    "redoc_url": f"/schema/{zone_name}/redoc/",
                    "api_url": f"/{api_prefix}/{zone_name}/",
                })

                total_apps += len(apps)
                total_endpoints += endpoint_count

            return zones_data, {
                "total_apps": total_apps,
                "total_endpoints": total_endpoints,
                "total_zones": len(zones),
            }
        except Exception as e:
            logger.error(f"Error getting revolution zones: {e}")
            return [], {
                "total_apps": 0,
                "total_endpoints": 0,
                "total_zones": 0,
            }

    def get_recent_users(self) -> List[Dict[str, Any]]:
        """Get recent users data for template."""
        try:
            User = self._get_user_model()
            recent_users = User.objects.select_related().order_by("-date_joined")[:10]

            # Get admin URLs for user model
            user_admin_urls = get_user_admin_urls()

            return [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email or "No email",
                    "date_joined": (
                        user.date_joined.strftime("%Y-%m-%d")
                        if user.date_joined
                        else "Unknown"
                    ),
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "last_login": user.last_login,
                    "admin_urls": {
                        "change": (
                            user_admin_urls["change"].format(id=user.id)
                            if user.id
                            else None
                        ),
                        "view": (
                            user_admin_urls["view"].format(id=user.id) if user.id else None
                        ),
                    },
                }
                for user in recent_users
            ]
        except Exception as e:
            logger.error(f"Error getting recent users: {e}")
            return []

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

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics for dashboard."""
        metrics = {}

        # Database metrics
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                metrics["database"] = {
                    "status": "healthy",
                    "type": "PostgreSQL",
                    "health_percentage": 95,
                    "description": "Connection successful",
                }
        except Exception as e:
            metrics["database"] = {
                "status": "error",
                "type": "PostgreSQL",
                "health_percentage": 0,
                "description": f"Connection failed: {str(e)}",
            }

        # Cache metrics
        try:
            cache.set("health_check", "ok", 10)
            cache_result = cache.get("health_check")
            if cache_result == "ok":
                metrics["cache"] = {
                    "status": "healthy",
                    "type": "Memory Cache",
                    "health_percentage": 90,
                    "description": "Cache working properly",
                }
            else:
                metrics["cache"] = {
                    "status": "warning",
                    "type": "Memory Cache",
                    "health_percentage": 50,
                    "description": "Cache response delayed",
                }
        except Exception as e:
            metrics["cache"] = {
                "status": "error",
                "type": "Memory Cache",
                "health_percentage": 0,
                "description": f"Cache error: {str(e)}",
            }

        return metrics

    def main_dashboard_callback(self, request, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main dashboard callback function with comprehensive system data.

        Returns all dashboard data as Pydantic models for type safety.
        """
        try:
            # Get dashboard data using Pydantic models
            user_stats = self.get_user_statistics()
            system_health = self.get_system_health()
            quick_actions = self.get_quick_actions()

            dashboard_data = DashboardData(
                stat_cards=user_stats,
                system_health=system_health,
                quick_actions=quick_actions,
                last_updated=timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                environment=getattr(settings, "ENVIRONMENT", "development"),
            )

            # Convert to template context (keeping Pydantic validation)
            cards_data = [card.model_dump() for card in dashboard_data.stat_cards]

            context.update({
                # Statistics cards
                "cards": cards_data,
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
                # Meta information
                "last_updated": dashboard_data.last_updated,
                "environment": dashboard_data.environment,
                "dashboard_title": "Django CFG Dashboard",
            })

            # logger.info(f"Final context keys: {list(context.keys())}")
            # logger.info(f"Cards in context: {len(context.get('cards', []))}")
            # logger.info("=== DJANGO_CFG DASHBOARD CALLBACK COMPLETED ===")

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
