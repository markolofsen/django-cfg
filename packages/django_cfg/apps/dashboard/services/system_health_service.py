"""
System Health Service

Monitors system components health status.
Checks database, cache, queue, storage, and API availability.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Literal

logger = logging.getLogger(__name__)


class SystemHealthService:
    """
    Service for monitoring system component health.

    %%PRIORITY:HIGH%%
    %%AI_HINT: Checks health of various system components%%

    TAGS: health, monitoring, system, service
    DEPENDS_ON: [django.db.connection, django.core.cache, redis]
    """

    def __init__(self):
        """Initialize system health service."""
        self.logger = logger

    def check_database_health(self) -> Dict[str, Any]:
        """
        Check database connectivity and health.

        Returns:
            Health status dictionary with status, description, last_check
        """
        try:
            from django.db import connection

            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            return {
                'component': 'database',
                'status': 'healthy',
                'description': 'Database connection is working',
                'last_check': datetime.now().isoformat(),
                'health_percentage': 100,
            }
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return {
                'component': 'database',
                'status': 'error',
                'description': f'Database error: {str(e)}',
                'last_check': datetime.now().isoformat(),
                'health_percentage': 0,
            }

    def check_cache_health(self) -> Dict[str, Any]:
        """
        Check cache (Redis/Memcached) connectivity and health.

        Returns:
            Health status dictionary
        """
        try:
            from django.core.cache import cache

            # Test cache by setting and getting a test value
            test_key = 'health_check_test'
            test_value = 'ok'
            cache.set(test_key, test_value, timeout=10)
            result = cache.get(test_key)

            if result == test_value:
                cache.delete(test_key)
                return {
                    'component': 'cache',
                    'status': 'healthy',
                    'description': 'Cache is working correctly',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 100,
                }
            else:
                return {
                    'component': 'cache',
                    'status': 'warning',
                    'description': 'Cache test failed',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 50,
                }

        except Exception as e:
            self.logger.error(f"Cache health check failed: {e}")
            return {
                'component': 'cache',
                'status': 'error',
                'description': f'Cache error: {str(e)}',
                'last_check': datetime.now().isoformat(),
                'health_percentage': 0,
            }

    def check_queue_health(self) -> Dict[str, Any]:
        """
        Check task queue (Celery/Dramatiq) health.

        Returns:
            Health status dictionary
        """
        try:
            # TODO: Add real queue health check
            # Example: Check Redis connection, queue sizes, worker status
            from django_cfg.modules.django_tasks import DjangoTasks

            tasks = DjangoTasks()
            redis_client = tasks.get_redis_client()

            if redis_client and redis_client.ping():
                return {
                    'component': 'queue',
                    'status': 'healthy',
                    'description': 'Queue system is operational',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 100,
                }
            else:
                return {
                    'component': 'queue',
                    'status': 'error',
                    'description': 'Queue system unavailable',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 0,
                }

        except Exception as e:
            self.logger.error(f"Queue health check failed: {e}")
            return {
                'component': 'queue',
                'status': 'error',
                'description': f'Queue error: {str(e)}',
                'last_check': datetime.now().isoformat(),
                'health_percentage': 0,
            }

    def check_storage_health(self) -> Dict[str, Any]:
        """
        Check storage/file system health.

        Returns:
            Health status dictionary
        """
        try:
            import os
            from django.conf import settings

            # Check if media directory is writable
            media_root = getattr(settings, 'MEDIA_ROOT', None)

            if media_root and os.path.exists(media_root) and os.access(media_root, os.W_OK):
                return {
                    'component': 'storage',
                    'status': 'healthy',
                    'description': 'Storage is accessible and writable',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 100,
                }
            else:
                return {
                    'component': 'storage',
                    'status': 'warning',
                    'description': 'Storage may have limited access',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 70,
                }

        except Exception as e:
            self.logger.error(f"Storage health check failed: {e}")
            return {
                'component': 'storage',
                'status': 'error',
                'description': f'Storage error: {str(e)}',
                'last_check': datetime.now().isoformat(),
                'health_percentage': 0,
            }

    def get_all_health_checks(self) -> List[Dict[str, Any]]:
        """
        Run all health checks and return aggregated results.

        Returns:
            List of health check results for all components

        USED_BY: DashboardViewSet.system_health endpoint
        """
        checks = [
            self.check_database_health(),
            self.check_cache_health(),
            self.check_queue_health(),
            self.check_storage_health(),
        ]

        return checks

    def get_overall_health_status(self) -> Dict[str, Any]:
        """
        Get overall system health status.

        Returns:
            Dictionary with overall status, percentage, and component details
        """
        checks = self.get_all_health_checks()

        # Calculate overall health percentage
        total_health = sum(check.get('health_percentage', 0) for check in checks)
        overall_percentage = total_health // len(checks) if checks else 0

        # Determine overall status
        statuses = [check.get('status') for check in checks]
        if 'error' in statuses:
            overall_status = 'error'
        elif 'warning' in statuses:
            overall_status = 'warning'
        else:
            overall_status = 'healthy'

        return {
            'overall_status': overall_status,
            'overall_health_percentage': overall_percentage,
            'components': checks,
            'timestamp': datetime.now().isoformat(),
        }

    def get_quick_actions(self) -> List[Dict[str, Any]]:
        """
        Get quick action buttons for dashboard.

        Returns:
            List of quick action dictionaries

        %%AI_HINT: Actions link to admin pages or trigger common tasks%%
        """
        actions = [
            {
                'title': 'User Management',
                'description': 'Manage users and permissions',
                'icon': 'people',
                'link': '/admin/auth/user/',
                'color': 'primary',
                'category': 'admin',
            },
            {
                'title': 'View Logs',
                'description': 'Check system logs',
                'icon': 'description',
                'link': '/admin/django_cfg/logs/',
                'color': 'secondary',
                'category': 'system',
            },
            {
                'title': 'Clear Cache',
                'description': 'Clear application cache',
                'icon': 'refresh',
                'link': '/cfg/admin/cache/clear/',
                'color': 'warning',
                'category': 'system',
            },
            {
                'title': 'Run Backup',
                'description': 'Create system backup',
                'icon': 'backup',
                'link': '/cfg/admin/backup/create/',
                'color': 'success',
                'category': 'system',
            },
        ]

        return actions
