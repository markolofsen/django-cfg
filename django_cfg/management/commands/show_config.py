"""
Django management command to show current configuration.

Usage:
    python manage.py show_config
    python manage.py show_config --format json
"""

import json
from django.core.management.base import BaseCommand
from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = 'Show Django Config Toolkit configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            choices=['table', 'json'],
            default='table',
            help='Output format (default: table)',
        )
        parser.add_argument(
            '--include-secrets',
            action='store_true',
            help='Include sensitive information (use carefully)',
        )

    def handle(self, *args, **options):
        """Show configuration in requested format."""
        try:
            toolkit = ConfigToolkit()
            
            if options['format'] == 'json':
                self._show_json_format(toolkit, options['include_secrets'])
            else:
                self._show_table_format(toolkit, options['include_secrets'])
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to show configuration: {e}')
            )

    def _show_table_format(self, toolkit, include_secrets=False):
        """Show configuration in table format."""
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Django Config Toolkit - Current Configuration')
        )
        self.stdout.write('=' * 80)
        
        # Environment section
        self.stdout.write(self.style.SUCCESS('\n🌍 Environment'))
        self.stdout.write('-' * 40)
        env_data = [
            ('Environment', toolkit.environment),
            ('Debug Mode', toolkit.debug),
            ('Is Production', toolkit.is_production),
            ('Is Development', toolkit.is_development),
            ('Is Docker', toolkit.is_docker),
        ]
        
        if include_secrets:
            env_data.append(('Secret Key', toolkit.secret_key[:20] + '...'))
        else:
            env_data.append(('Secret Key', '[HIDDEN]'))
        
        for key, value in env_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # Database section
        self.stdout.write(self.style.SUCCESS('\n🗄️  Database'))
        self.stdout.write('-' * 40)
        db_data = [
            ('Engine', toolkit.database_engine),
            ('URL', toolkit.database_url[:50] + '...' if not include_secrets else toolkit.database_url),
            ('Max Connections', toolkit.database_max_connections),
            ('Is SQLite', toolkit.is_sqlite),
            ('Is PostgreSQL', toolkit.is_postgresql),
        ]
        
        for key, value in db_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # Security section
        self.stdout.write(self.style.SUCCESS('\n🔒 Security'))
        self.stdout.write('-' * 40)
        security_data = [
            ('CORS Enabled', toolkit.cors_enabled),
            ('CSRF Enabled', toolkit.csrf_enabled),
            ('SSL Redirect', toolkit.ssl_enabled),
        ]
        
        for key, value in security_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # API section
        self.stdout.write(self.style.SUCCESS('\n🌐 API'))
        self.stdout.write('-' * 40)
        api_data = [
            ('Page Size', toolkit.api_page_size),
            ('Max Page Size', toolkit.api_max_page_size),
            ('Rate Limiting', toolkit.api_rate_limit_enabled),
            ('Docs Enabled', toolkit.api_docs_enabled),
        ]
        
        for key, value in api_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # Cache section
        self.stdout.write(self.style.SUCCESS('\n💾 Cache'))
        self.stdout.write('-' * 40)
        cache_data = [
            ('Backend', toolkit.cache_backend),
            ('Timeout', f'{toolkit.cache_timeout}s'),
        ]
        
        for key, value in cache_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # Email section
        self.stdout.write(self.style.SUCCESS('\n📧 Email'))
        self.stdout.write('-' * 40)
        email_data = [
            ('Backend', toolkit.email_backend),
            ('Host', toolkit.email_host),
            ('From Email', toolkit.email_from),
        ]
        
        for key, value in email_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # Extended features
        self.stdout.write(self.style.SUCCESS('\n🎨 Extended Features'))
        self.stdout.write('-' * 40)
        
        if toolkit.unfold_enabled:
            self.stdout.write(f'  {"Unfold Admin":<20}: ✅ Enabled')
            self.stdout.write(f'  {"Site Title":<20}: {toolkit.site_title}')
        else:
            self.stdout.write(f'  {"Unfold Admin":<20}: ❌ Disabled')
        
        if toolkit.revolution_enabled:
            self.stdout.write(f'  {"Revolution API":<20}: ✅ Enabled')
            self.stdout.write(f'  {"API Prefix":<20}: {toolkit.api_prefix}')
        else:
            self.stdout.write(f'  {"Revolution API":<20}: ❌ Disabled')
        
        if toolkit.constance_enabled:
            self.stdout.write(f'  {"Constance":<20}: ✅ Enabled')
            self.stdout.write(f'  {"Backend":<20}: {toolkit.constance_backend}')
        else:
            self.stdout.write(f'  {"Constance":<20}: ❌ Disabled')
        
        self.stdout.write(f'  {"Logging":<20}: ✅ Enabled')
        self.stdout.write(f'  {"Log Level":<20}: {toolkit.log_level}')
        
        # Performance section
        self.stdout.write(self.style.SUCCESS('\n⚡ Performance'))
        self.stdout.write('-' * 40)
        perf_data = [
            ('Config Count', toolkit._config_count),
            ('Init Time', f'{toolkit._init_time_ms:.2f}ms'),
        ]
        
        for key, value in perf_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        self.stdout.write('\n' + '=' * 80)

    def _show_json_format(self, toolkit, include_secrets=False):
        """Show configuration in JSON format."""
        config_data = {
            'environment': {
                'environment': toolkit.environment,
                'debug': toolkit.debug,
                'is_production': toolkit.is_production,
                'is_development': toolkit.is_development,
                'is_docker': toolkit.is_docker,
            },
            'database': {
                'engine': toolkit.database_engine,
                'url': toolkit.database_url if include_secrets else '[HIDDEN]',
                'max_connections': toolkit.database_max_connections,
                'is_sqlite': toolkit.is_sqlite,
                'is_postgresql': toolkit.is_postgresql,
            },
            'security': {
                'cors_enabled': toolkit.cors_enabled,
                'csrf_enabled': toolkit.csrf_enabled,
                'ssl_enabled': toolkit.ssl_enabled,
            },
            'api': {
                'page_size': toolkit.api_page_size,
                'max_page_size': toolkit.api_max_page_size,
                'rate_limit_enabled': toolkit.api_rate_limit_enabled,
                'docs_enabled': toolkit.api_docs_enabled,
            },
            'cache': {
                'backend': toolkit.cache_backend,
                'timeout': toolkit.cache_timeout,
            },
            'email': {
                'backend': toolkit.email_backend,
                'host': toolkit.email_host,
                'from_email': toolkit.email_from,
            },
            'extended_features': {
                'unfold': {
                    'enabled': toolkit.unfold_enabled,
                    'site_title': toolkit.site_title if toolkit.unfold_enabled else None,
                },
                'revolution': {
                    'enabled': toolkit.revolution_enabled,
                    'api_prefix': toolkit.api_prefix if toolkit.revolution_enabled else None,
                },
                'constance': {
                    'enabled': toolkit.constance_enabled,
                    'backend': toolkit.constance_backend if toolkit.constance_enabled else None,
                },
                'logging': {
                    'enabled': toolkit.logging_enabled,
                    'log_level': toolkit.log_level,
                },
            },
            'performance': {
                'config_count': toolkit._config_count,
                'init_time_ms': toolkit._init_time_ms,
            }
        }
        
        if include_secrets:
            config_data['environment']['secret_key'] = toolkit.secret_key
        
        self.stdout.write(json.dumps(config_data, indent=2))
