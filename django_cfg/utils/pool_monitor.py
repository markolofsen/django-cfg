"""
Connection Pool Monitoring for Django-CFG.

Provides utilities to monitor and inspect PostgreSQL connection pool status.
Works with Django 5.1+ native connection pooling (psycopg3).

Usage:
    from django_cfg.utils.pool_monitor import PoolMonitor

    # Get pool statistics
    monitor = PoolMonitor()
    stats = monitor.get_pool_stats()

    # Check pool health
    health = monitor.check_pool_health()

    # Log pool status
    monitor.log_pool_status()
"""

import logging
from typing import Any, Dict, Optional

from django.conf import settings
from django.db import connection

from .smart_defaults import _detect_asgi_mode, get_pool_config

logger = logging.getLogger('django_cfg.pool_monitor')


class PoolMonitor:
    """
    Monitor and inspect database connection pool.

    Provides methods to retrieve pool statistics, check health,
    and log pool status for operational visibility.
    """

    def __init__(self, database_alias: str = 'default'):
        """
        Initialize pool monitor.

        Args:
            database_alias: Database alias to monitor (default: 'default')
        """
        self.database_alias = database_alias

    def get_pool_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get current connection pool statistics.

        Returns:
            Dict with pool statistics:
            {
                'pool_size': int,          # Current pool size
                'pool_available': int,     # Available connections
                'pool_min_size': int,      # Configured minimum size
                'pool_max_size': int,      # Configured maximum size
                'pool_timeout': int,       # Connection timeout
                'is_asgi': bool,           # Deployment mode
                'environment': str,        # Environment name
                'backend': str,            # Database backend
                'has_pool': bool,          # Whether pooling is enabled
            }

            Returns None if connection pooling is not configured.

        Example:
            >>> monitor = PoolMonitor()
            >>> stats = monitor.get_pool_stats()
            >>> print(f"Pool size: {stats['pool_size']}/{stats['pool_max_size']}")
        """
        try:
            # Get database configuration
            db_config = settings.DATABASES.get(self.database_alias, {})
            backend = db_config.get('ENGINE', 'unknown')

            # Check if PostgreSQL with pooling
            if 'postgresql' not in backend:
                logger.debug(f"Database {self.database_alias} is not PostgreSQL, pooling not available")
                return None

            pool_options = db_config.get('OPTIONS', {}).get('pool', {})
            if not pool_options:
                logger.debug(f"No pool configuration found for database {self.database_alias}")
                return None

            # Detect environment and mode
            is_asgi = _detect_asgi_mode()
            environment = getattr(settings, 'ENVIRONMENT', 'production')

            # Get expected pool config
            expected_config = get_pool_config(environment, is_asgi=is_asgi)

            # Try to get actual pool statistics from psycopg3
            pool_size = None
            pool_available = None

            try:
                # Access underlying psycopg3 connection pool
                # This requires psycopg3 with connection pooling
                db_conn = connection.connection
                if db_conn and hasattr(db_conn, 'pgconn'):
                    pool = getattr(db_conn, 'pool', None)
                    if pool:
                        # psycopg3 ConnectionPool has these attributes
                        pool_size = getattr(pool, 'size', None)
                        pool_available = getattr(pool, 'available', None)
            except Exception as e:
                logger.debug(f"Could not retrieve live pool stats: {e}")

            return {
                'pool_size': pool_size,
                'pool_available': pool_available,
                'pool_min_size': pool_options.get('min_size', expected_config['min_size']),
                'pool_max_size': pool_options.get('max_size', expected_config['max_size']),
                'pool_timeout': pool_options.get('timeout', expected_config['timeout']),
                'max_lifetime': pool_options.get('max_lifetime', 3600),
                'max_idle': pool_options.get('max_idle', 600),
                'is_asgi': is_asgi,
                'environment': environment,
                'backend': backend,
                'has_pool': True,
            }

        except Exception as e:
            logger.error(f"Failed to get pool stats: {e}", exc_info=True)
            return None

    def check_pool_health(self) -> Dict[str, Any]:
        """
        Check connection pool health status.

        Returns:
            Dict with health information:
            {
                'healthy': bool,           # Overall health status
                'status': str,             # 'healthy', 'warning', 'critical', 'unavailable'
                'capacity_percent': float, # Pool capacity usage (0-100)
                'issues': list,            # List of detected issues
                'recommendations': list,   # Recommended actions
            }

        Health thresholds:
            - < 70% capacity: Healthy
            - 70-90% capacity: Warning
            - > 90% capacity: Critical

        Example:
            >>> monitor = PoolMonitor()
            >>> health = monitor.check_pool_health()
            >>> if not health['healthy']:
            ...     print(f"Issues: {', '.join(health['issues'])}")
        """
        stats = self.get_pool_stats()

        if not stats or not stats['has_pool']:
            return {
                'healthy': True,  # No pool = no problem (using regular connections)
                'status': 'unavailable',
                'capacity_percent': 0.0,
                'issues': ['Connection pooling not configured'],
                'recommendations': ['Consider enabling connection pooling for production'],
            }

        issues = []
        recommendations = []
        healthy = True
        status = 'healthy'

        # Calculate capacity if live stats available
        capacity_percent = 0.0
        if stats['pool_size'] is not None and stats['pool_max_size']:
            capacity_percent = (stats['pool_size'] / stats['pool_max_size']) * 100

            # Check capacity thresholds
            if capacity_percent >= 90:
                status = 'critical'
                healthy = False
                issues.append(f"Pool capacity critical: {capacity_percent:.1f}% used")
                recommendations.append("Increase DB_POOL_MAX_SIZE or scale database")
            elif capacity_percent >= 70:
                status = 'warning'
                issues.append(f"Pool capacity high: {capacity_percent:.1f}% used")
                recommendations.append("Monitor pool usage and consider increasing max_size")

        # Check if min_size is reasonable
        min_size = stats['pool_min_size']
        max_size = stats['pool_max_size']

        if min_size >= max_size * 0.9:
            issues.append(f"Min size ({min_size}) too close to max size ({max_size})")
            recommendations.append("Reduce DB_POOL_MIN_SIZE for better resource management")

        # Check timeout
        timeout = stats['pool_timeout']
        if timeout > 30:
            issues.append(f"Pool timeout high: {timeout}s")
            recommendations.append("Long timeouts may indicate slow queries or insufficient pool size")

        # Check ASGI vs WSGI pool sizing
        is_asgi = stats['is_asgi']
        mode = 'ASGI' if is_asgi else 'WSGI'

        expected_config = get_pool_config(stats['environment'], is_asgi=is_asgi)
        if max_size < expected_config['max_size'] * 0.5:
            issues.append(f"Pool size low for {mode} mode")
            recommendations.append(f"Consider increasing to {expected_config['max_size']} for {mode}")

        return {
            'healthy': healthy and len(issues) == 0,
            'status': status,
            'capacity_percent': capacity_percent,
            'issues': issues,
            'recommendations': recommendations,
        }

    def log_pool_status(self, level: str = 'info') -> None:
        """
        Log current pool status to Django logger.

        Args:
            level: Log level ('debug', 'info', 'warning', 'error')

        Example:
            >>> monitor = PoolMonitor()
            >>> monitor.log_pool_status(level='info')
        """
        stats = self.get_pool_stats()

        if not stats:
            logger.debug(f"No pool statistics available for database {self.database_alias}")
            return

        health = self.check_pool_health()

        log_func = getattr(logger, level, logger.info)

        mode = 'ASGI' if stats['is_asgi'] else 'WSGI'
        status_emoji = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '🔴',
            'unavailable': '⚪',
        }.get(health['status'], '❓')

        log_message = (
            f"[Pool Monitor] {status_emoji} Status: {health['status'].upper()} | "
            f"Mode: {mode} | Env: {stats['environment']} | "
            f"Pool: {stats['pool_size'] or '?'}/{stats['pool_max_size']} | "
            f"Capacity: {health['capacity_percent']:.1f}%"
        )

        log_func(log_message)

        if health['issues']:
            for issue in health['issues']:
                logger.warning(f"[Pool Monitor] Issue: {issue}")

        if health['recommendations']:
            for rec in health['recommendations']:
                logger.info(f"[Pool Monitor] Recommendation: {rec}")

    def get_pool_info_dict(self) -> Dict[str, Any]:
        """
        Get complete pool information as a dictionary.

        Combines statistics and health check into a single dict.
        Useful for API responses or structured logging.

        Returns:
            Dict with complete pool information including stats and health.

        Example:
            >>> monitor = PoolMonitor()
            >>> info = monitor.get_pool_info_dict()
            >>> print(json.dumps(info, indent=2))
        """
        stats = self.get_pool_stats()
        health = self.check_pool_health()

        if not stats:
            return {
                'available': False,
                'reason': 'Connection pooling not configured',
            }

        return {
            'available': True,
            'statistics': stats,
            'health': health,
            'timestamp': self._get_timestamp(),
        }

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


# Convenience function for quick pool status check
def get_pool_status(database_alias: str = 'default') -> Dict[str, Any]:
    """
    Convenience function to quickly get pool status.

    Args:
        database_alias: Database alias to check (default: 'default')

    Returns:
        Dict with pool information (same as PoolMonitor.get_pool_info_dict())

    Example:
        >>> from django_cfg.utils.pool_monitor import get_pool_status
        >>> status = get_pool_status()
        >>> print(status['health']['status'])
    """
    monitor = PoolMonitor(database_alias=database_alias)
    return monitor.get_pool_info_dict()
