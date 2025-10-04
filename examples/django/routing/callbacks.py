"""
Dashboard Callback System

Provides callback utilities for Unfold dashboard integration.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.conf import settings
from ..modules.base import BaseCfgModule


def dashboard_callback(request: HttpRequest, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Default dashboard callback for Unfold admin.
    
    Returns enhanced context with dashboard data.
    """
    User = get_user_model()
    
    # Get basic stats
    user_count = User.objects.count()
    
    # Database info
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM django_session")
        session_count = cursor.fetchone()[0]
    
    # Add dashboard data to context
    context.update({
        "dashboard": [
            {
                "title": "System Overview",
                "metric": f"{user_count} users",
                "footer": f"{session_count} active sessions",
                "chart": {
                    "labels": ["Users", "Sessions"],
                    "data": [user_count, session_count],
                }
            },
            {
                "title": "Quick Actions",
                "metric": "Admin Tools",
                "footer": "Manage your system",
                "link": "/admin/",
            }
        ]
    })
    
    return context


def environment_callback(request: HttpRequest) -> Dict[str, Any]:
    """
    Environment callback for Unfold admin.
    
    Returns environment information and system status.
    """

    
    # Use BaseCfgModule to get config
    base_module = BaseCfgModule()
    config = base_module.get_config()
    
    return {
        "environment": getattr(config, 'environment', 'development'),
        "debug": getattr(config, 'debug', False),
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "database": {
            "engine": "PostgreSQL" if config and hasattr(config, 'database_default') else "Unknown",
            "name": config.database_default.name if config and hasattr(config, 'database_default') else "Unknown",
        },
        "cache": {
            "backend": "Redis" if config and hasattr(config, 'cache_default') else "default",
        },
        "features": {
            "unfold": True,  # Unfold always enabled
            "revolution": True,  # Revolution always enabled
            "constance": getattr(config, 'enable_constance', False) if config else False,
        }
    }


def permission_callback(request: HttpRequest) -> Dict[str, Any]:
    """
    Permission callback for Unfold admin.
    
    Returns user permission information.
    """
    if not request.user.is_authenticated:
        return {"permissions": [], "groups": []}
    
    user_permissions = list(request.user.get_all_permissions())
    user_groups = list(request.user.groups.values_list('name', flat=True))
    
    return {
        "permissions": user_permissions,
        "groups": user_groups,
        "is_staff": request.user.is_staff,
        "is_superuser": request.user.is_superuser,
    }


def search_callback(request: HttpRequest, query: str) -> List[Dict[str, Any]]:
    """
    Search callback for Unfold admin.
    
    Provides search functionality across models.
    """

    
    results = []
    
    if len(query) < 2:
        return results
    
    # Search users
    User = get_user_model()
    users = User.objects.filter(
        username__icontains=query
    ).values('id', 'username', 'email')[:5]
    
    for user in users:
        results.append({
            "title": f"User: {user['username']}",
            "url": f"/admin/auth/user/{user['id']}/change/",
            "description": user.get('email', ''),
        })
    
    # Search content types (as a proxy for apps/models)
    content_types = ContentType.objects.filter(
        model__icontains=query
    ).values('app_label', 'model')[:5]
    
    for ct in content_types:
        results.append({
            "title": f"Model: {ct['app_label']}.{ct['model']}",
            "url": f"/admin/{ct['app_label']}/{ct['model']}/",
            "description": f"Manage {ct['model']} objects",
        })
    
    return results


def badge_callback(request: HttpRequest) -> List[Dict[str, Any]]:
    """
    Badge callback for Unfold admin.
    
    Returns notification badges and counters.
    """
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Count new users in last 24 hours
    from datetime import datetime, timedelta
    yesterday = datetime.now() - timedelta(days=1)
    new_users = User.objects.filter(date_joined__gte=yesterday).count()
    
    badges = []
    
    if new_users > 0:
        badges.append({
            "title": "New Users",
            "count": new_users,
            "color": "primary",
            "url": "/admin/auth/user/?date_joined__gte=" + yesterday.strftime('%Y-%m-%d'),
        })
    
    # Add system health badge
    badges.append({
        "title": "System",
        "count": "OK",
        "color": "success",
        "url": "/admin/",
    })
    
    return badges


# Helper function to register callbacks in Unfold config
def get_unfold_callbacks() -> Dict[str, str]:
    """
    Get callback function paths for Unfold configuration.
    
    Returns dictionary mapping callback types to function paths.
    """
    return {
        "dashboard_callback": "django_cfg.routing.callbacks.dashboard_callback",
        "environment_callback": "django_cfg.routing.callbacks.environment_callback", 
        "permission_callback": "django_cfg.routing.callbacks.permission_callback",
        "search_callback": "django_cfg.routing.callbacks.search_callback",
        "badge_callback": "django_cfg.routing.callbacks.badge_callback",
    }
