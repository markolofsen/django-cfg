"""
Django management command to display connection pool status.

Usage:
    python manage.py pool_status
    python manage.py pool_status --database=secondary
    python manage.py pool_status --json
"""

import json

from django.core.management.base import BaseCommand

from django_cfg.utils.pool_monitor import PoolMonitor


class Command(BaseCommand):
    """Display database connection pool status."""

    help = 'Display database connection pool status and health information'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--database',
            default='default',
            help='Database alias to check (default: default)',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output in JSON format',
        )

    def handle(self, *args, **options):
        """Execute command."""
        database_alias = options['database']
        json_output = options['json']

        monitor = PoolMonitor(database_alias=database_alias)

        if json_output:
            self._handle_json_output(monitor)
        else:
            self._handle_pretty_output(monitor)

    def _handle_json_output(self, monitor: PoolMonitor):
        """Output pool status as JSON."""
        info = monitor.get_pool_info_dict()
        self.stdout.write(json.dumps(info, indent=2))

    def _handle_pretty_output(self, monitor: PoolMonitor):
        """Output pool status in pretty formatted text."""
        stats = monitor.get_pool_stats()

        if not stats:
            self.stdout.write(self.style.WARNING('\n⚠️  Connection Pooling: Not Configured'))
            self.stdout.write('')
            self.stdout.write('Database is not using connection pooling.')
            self.stdout.write('Consider enabling pooling for production environments.')
            self.stdout.write('')
            return

        health = monitor.check_pool_health()

        # Header
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('         DATABASE CONNECTION POOL STATUS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Deployment Information
        mode = 'ASGI' if stats['is_asgi'] else 'WSGI'
        mode_icon = '🚀' if stats['is_asgi'] else '🐍'

        self.stdout.write(self.style.HTTP_INFO('Deployment Information:'))
        self.stdout.write(f"  Mode:            {mode_icon} {mode}")
        self.stdout.write(f"  Environment:     {stats['environment'].title()}")
        self.stdout.write(f"  Database:        {monitor.database_alias}")
        self.stdout.write(f"  Backend:         {stats['backend']}")
        self.stdout.write('')

        # Pool Configuration
        self.stdout.write(self.style.HTTP_INFO('Pool Configuration:'))
        self.stdout.write(f"  Min Size:        {stats['pool_min_size']:3d} connections")
        self.stdout.write(f"  Max Size:        {stats['pool_max_size']:3d} connections")
        self.stdout.write(f"  Timeout:         {stats['pool_timeout']:3d} seconds")
        self.stdout.write(f"  Max Lifetime:    {stats['max_lifetime']:4d} seconds ({stats['max_lifetime'] // 60} min)")
        self.stdout.write(f"  Max Idle:        {stats['max_idle']:4d} seconds ({stats['max_idle'] // 60} min)")
        self.stdout.write('')

        # Current Status (if available)
        if stats['pool_size'] is not None:
            self.stdout.write(self.style.HTTP_INFO('Current Status:'))
            self.stdout.write(f"  Current Size:    {stats['pool_size']:3d} connections")
            if stats['pool_available'] is not None:
                self.stdout.write(f"  Available:       {stats['pool_available']:3d} connections")
            self.stdout.write(f"  Capacity:        {health['capacity_percent']:.1f}% used")
            self.stdout.write('')
        else:
            self.stdout.write(self.style.WARNING('Current Status:     Not available (pool not active yet)'))
            self.stdout.write('')

        # Health Check
        status_styles = {
            'healthy': self.style.SUCCESS,
            'warning': self.style.WARNING,
            'critical': self.style.ERROR,
            'unavailable': self.style.NOTICE,
        }
        status_icons = {
            'healthy': '✅',
            'warning': '⚠️',
            'critical': '🔴',
            'unavailable': '⚪',
        }

        status_style = status_styles.get(health['status'], self.style.NOTICE)
        status_icon = status_icons.get(health['status'], '❓')
        status_text = health['status'].upper()

        self.stdout.write(self.style.HTTP_INFO('Health Check:'))
        self.stdout.write(f"  Status:          {status_icon} " + status_style(status_text))

        if health['issues']:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('  Issues Detected:'))
            for issue in health['issues']:
                self.stdout.write(self.style.WARNING(f"    • {issue}"))

        if health['recommendations']:
            self.stdout.write('')
            self.stdout.write(self.style.NOTICE('  Recommendations:'))
            for rec in health['recommendations']:
                self.stdout.write(f"    • {rec}")

        # Footer
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        # Overall summary
        if health['healthy']:
            self.stdout.write(self.style.SUCCESS('✅ Pool is healthy and operating normally'))
        elif health['status'] == 'warning':
            self.stdout.write(self.style.WARNING('⚠️  Pool is functional but requires attention'))
        elif health['status'] == 'critical':
            self.stdout.write(self.style.ERROR('🔴 Pool is in critical state - immediate action required'))
        else:
            self.stdout.write(self.style.NOTICE('ℹ️  Pool status check completed'))

        self.stdout.write('')
