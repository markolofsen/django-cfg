"""System section for dashboard."""

from typing import Any, Dict

from .base import DataSection


class SystemSection(DataSection):
    """
    System management section.
    """

    template_name = "admin/sections/system_section.html"
    title = "System Management"
    icon = "settings"

    def get_data(self) -> Dict[str, Any]:
        """Get system data."""
        return {
            'health': self.get_health_check(),
            'services': self.get_services_status(),
            'configuration': self.get_configuration(),
        }

    def get_health_check(self) -> Dict[str, Any]:
        """Get health check status."""
        import psutil

        return {
            'status': 'healthy',
            'checks': {
                'database': self.check_database(),
                'cache': self.check_cache(),
                'disk_space': psutil.disk_usage('/').percent < 90,
                'memory': psutil.virtual_memory().percent < 90,
            }
        }

    def check_database(self) -> bool:
        """Check database connectivity."""
        from django.db import connection

        try:
            connection.ensure_connection()
            return True
        except Exception:
            return False

    def check_cache(self) -> bool:
        """Check cache availability."""
        from django.core.cache import cache

        try:
            cache.set('health_check', True, 1)
            return cache.get('health_check') is True
        except Exception:
            return False

    def get_services_status(self) -> Dict[str, Any]:
        """Get services status."""
        # TODO: Implement services status check
        return {}

    def get_configuration(self) -> Dict[str, Any]:
        """Get system configuration."""
        from django_cfg.core.config import get_current_config

        config = get_current_config()

        return {
            'debug': config.debug,
            'env_mode': config.env_mode,
            'project_name': config.project_name,
        }
