"""
System health and metrics callbacks.
"""

import logging
import shutil
from typing import List, Dict, Any

from django.utils import timezone
from django.db import connection
from django.core.cache import cache

from ..models.dashboard import SystemHealthItem

logger = logging.getLogger(__name__)


class SystemCallbacks:
    """System health and metrics callbacks."""
    
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
