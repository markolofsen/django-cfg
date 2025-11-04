"""
Django management command to check all API endpoints status.

Usage:
    python manage.py check_endpoints
    python manage.py check_endpoints --include-unnamed
    python manage.py check_endpoints --timeout 10
    python manage.py check_endpoints --json
"""

import json

from django.urls import reverse

from django_cfg.apps.api.endpoints.endpoints_status.checker import check_all_endpoints
from django_cfg.management.utils import SafeCommand


class Command(SafeCommand):
    help = 'Check status of all Django CFG API endpoints'

    def add_arguments(self, parser):
        parser.add_argument(
            '--include-unnamed',
            action='store_true',
            help='Include unnamed URL patterns in the check',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            help='Request timeout in seconds (default: 5)',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON',
        )
        parser.add_argument(
            '--url',
            type=str,
            help='Check specific endpoint by URL name (e.g., "endpoints_status")',
        )
        parser.add_argument(
            '--no-auth',
            action='store_true',
            help='Disable automatic JWT authentication retry (default: enabled)',
        )

    def handle(self, *args, **options):
        include_unnamed = options['include_unnamed']
        timeout = options['timeout']
        output_json = options['json']
        url_name = options.get('url')
        auto_auth = not options['no_auth']  # Auto-auth enabled by default

        # If specific URL requested, just resolve and display it
        if url_name:
            try:
                url = reverse(url_name)
                self.stdout.write(self.style.SUCCESS(f'✅ URL name "{url_name}" resolves to: {url}'))
                return
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error resolving URL "{url_name}": {e}'))
                return

        # Check all endpoints
        auth_msg = "with auto-auth" if auto_auth else "without auth"
        self.stdout.write(self.style.WARNING(f'🔍 Checking endpoints (timeout: {timeout}s, {auth_msg})...'))

        status_data = check_all_endpoints(
            include_unnamed=include_unnamed,
            timeout=timeout,
            auto_auth=auto_auth
        )

        # Output as JSON if requested
        if output_json:
            self.stdout.write(json.dumps(status_data, indent=2))
            return

        # Pretty print results
        self._print_results(status_data)

    def _print_results(self, data):
        """Print formatted results to console."""

        # Overall status
        status = data['status']
        if status == 'healthy':
            status_style = self.style.SUCCESS
            emoji = '✅'
        elif status == 'degraded':
            status_style = self.style.WARNING
            emoji = '⚠️'
        else:
            status_style = self.style.ERROR
            emoji = '❌'

        self.stdout.write('')
        self.stdout.write(status_style(f'{emoji} Overall Status: {status.upper()}'))
        self.stdout.write('')

        # Summary
        self.stdout.write(self.style.HTTP_INFO('📊 Summary:'))
        self.stdout.write(f'  Total endpoints: {data["total_endpoints"]}')
        self.stdout.write(self.style.SUCCESS(f'  ✅ Healthy: {data["healthy"]}'))
        self.stdout.write(self.style.WARNING(f'  ⚠️  Warnings: {data["warnings"]}'))
        self.stdout.write(self.style.ERROR(f'  ❌ Unhealthy: {data["unhealthy"]}'))
        self.stdout.write(self.style.ERROR(f'  ❌ Errors: {data["errors"]}'))
        self.stdout.write(f'  ⏭️  Skipped: {data["skipped"]}')
        self.stdout.write('')

        # Endpoints details
        self.stdout.write(self.style.HTTP_INFO('🔗 Endpoints:'))

        for endpoint in data['endpoints']:
            name = endpoint.get('url_name') or 'unnamed'
            url = endpoint['url']
            status = endpoint['status']

            if status == 'healthy':
                icon = '✅'
                style = self.style.SUCCESS
            elif status == 'degraded':
                icon = '⚠️'
                style = self.style.WARNING
            else:
                icon = '❌'
                style = self.style.ERROR

            self.stdout.write(f'  {icon} {name}')

            # Show both pattern and resolved URL for parametrized endpoints
            if endpoint.get('has_parameters') and endpoint.get('url_pattern'):
                self.stdout.write(f'     Pattern: {endpoint["url_pattern"]}')
                self.stdout.write(f'     Resolved: {url}')
            else:
                self.stdout.write(f'     URL: {url}')

            # Show status with status code
            status_code = endpoint.get('status_code')
            if status_code:
                self.stdout.write(style(f'     Status: {status} ({status_code})'))
            else:
                self.stdout.write(style(f'     Status: {status}'))

            if endpoint.get('response_time_ms'):
                self.stdout.write(f'     Response time: {endpoint["response_time_ms"]:.2f}ms')

            if endpoint.get('error'):
                error_type = endpoint.get('error_type', 'general')
                if error_type == 'database':
                    self.stdout.write(self.style.WARNING(f'     ⚠️  DB Error (multi-db): {endpoint["error"]}'))
                else:
                    self.stdout.write(self.style.ERROR(f'     Error: {endpoint["error"]}'))

            # Show reason for warnings (e.g., 404 explanations)
            if endpoint.get('reason') and status == 'warning':
                self.stdout.write(self.style.WARNING(f'     ⚠️  {endpoint["reason"]}'))

            if endpoint.get('required_auth'):
                self.stdout.write('     🔐 Required JWT authentication')

            if endpoint.get('rate_limited'):
                self.stdout.write('     ⏱️  Rate limited (429)')

            self.stdout.write('')

        # Timestamp
        self.stdout.write(self.style.HTTP_INFO(f'🕐 Checked at: {data["timestamp"]}'))
