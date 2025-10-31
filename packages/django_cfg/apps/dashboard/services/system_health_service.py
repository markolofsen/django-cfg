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
        Check task queue (ReArq) health via Redis connection.

        Returns:
            Health status dictionary
        """
        try:
            # Check Redis connection directly (used by task queue)
            from django.core.cache import cache

            # Try to ping Redis through cache backend
            cache_backend = cache._cache if hasattr(cache, '_cache') else cache

            # Simple check - if cache works, Redis is available
            test_key = 'queue_health_check'
            cache.set(test_key, 'ok', timeout=5)
            result = cache.get(test_key)

            if result == 'ok':
                cache.delete(test_key)
                return {
                    'component': 'queue',
                    'status': 'healthy',
                    'description': 'Queue system (Redis) is operational',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 100,
                }
            else:
                return {
                    'component': 'queue',
                    'status': 'warning',
                    'description': 'Queue system check inconclusive',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 50,
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

    def check_django_q2_health(self) -> Dict[str, Any]:
        """
        Check Django-Q2 task scheduling configuration and status.

        Returns:
            Health status dictionary with schedule count and cluster status
        """
        try:
            from django_cfg.core.config import get_current_config

            config = get_current_config()

            # Check if django_q2 is configured
            if not hasattr(config, 'django_q2') or not config.django_q2:
                return {
                    'component': 'django_q2',
                    'status': 'info',
                    'description': 'Django-Q2 scheduling not configured',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 100,
                    'details': {
                        'enabled': False,
                        'schedules_count': 0,
                    }
                }

            django_q2_config = config.django_q2

            # Check if enabled
            if not django_q2_config.enabled:
                return {
                    'component': 'django_q2',
                    'status': 'warning',
                    'description': 'Django-Q2 scheduling is disabled',
                    'last_check': datetime.now().isoformat(),
                    'health_percentage': 50,
                    'details': {
                        'enabled': False,
                        'schedules_count': len(django_q2_config.schedules) if django_q2_config.schedules else 0,
                    }
                }

            # Count schedules
            schedules_count = len(django_q2_config.schedules) if django_q2_config.schedules else 0

            # Try to check cluster status from database
            cluster_running = False
            try:
                from django_q.models import Schedule, Task
                from django.utils import timezone
                from datetime import timedelta

                # Check for recent task activity
                recent_task = Task.objects.filter(
                    started__gte=timezone.now() - timedelta(minutes=5)
                ).exists()
                cluster_running = recent_task
            except Exception:
                pass

            return {
                'component': 'django_q2',
                'status': 'healthy',
                'description': f'{schedules_count} schedule(s) configured, cluster {"running" if cluster_running else "idle"}',
                'last_check': datetime.now().isoformat(),
                'health_percentage': 100,
                'details': {
                    'enabled': True,
                    'schedules_count': schedules_count,
                    'cluster_running': cluster_running,
                    'workers': django_q2_config.workers,
                }
            }

        except Exception as e:
            self.logger.error(f"Django-Q2 health check failed: {e}")
            return {
                'component': 'django_q2',
                'status': 'error',
                'description': f'Django-Q2 check error: {str(e)}',
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
            self.check_django_q2_health(),
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
