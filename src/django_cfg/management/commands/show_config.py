"""
Django management command to show current configuration.

Usage:
    python manage.py show_config
    python manage.py show_config --format json
"""

import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Show Django Config configuration'

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
            # Get the config instance from Django settings
            config = self._get_config_instance()
            
            if options['format'] == 'json':
                self._show_json_format(config, options['include_secrets'])
            else:
                self._show_table_format(config, options['include_secrets'])
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to show configuration: {e}')
            )

    def _get_config_instance(self):
        """Get the DjangoConfig instance from Django settings."""
        # Try to get config from settings module
        settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
        if not settings_module:
            raise ValueError("DJANGO_SETTINGS_MODULE environment variable not set")
        
        # Import the settings module and get the config
        import importlib
        settings_mod = importlib.import_module(settings_module)
        
        if hasattr(settings_mod, 'config'):
            return settings_mod.config
        else:
            # Fallback: create a minimal config from Django settings
            from django_cfg import DjangoConfig
            return DjangoConfig(
                project_name=getattr(settings, 'PROJECT_NAME', 'Django Project'),
                secret_key=settings.SECRET_KEY,
                debug=settings.DEBUG,
                allowed_hosts=settings.ALLOWED_HOSTS,
            )

    def _show_table_format(self, config, include_secrets=False):
        """Show configuration in table format."""
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Django Config - Current Configuration')
        )
        self.stdout.write('=' * 80)
        
        # Project section
        self.stdout.write(self.style.SUCCESS('\n📋 Project'))
        self.stdout.write('-' * 40)
        project_data = [
            ('Name', config.project_name),
            ('Version', getattr(config, 'project_version', 'N/A')),
            ('Description', getattr(config, 'project_description', 'N/A')),
        ]
        
        for key, value in project_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # Environment section
        self.stdout.write(self.style.SUCCESS('\n🌍 Environment'))
        self.stdout.write('-' * 40)
        env_data = [
            ('Environment', getattr(config, '_environment', 'auto-detected')),
            ('Debug Mode', config.debug),
            ('Allowed Hosts', ', '.join(config.allowed_hosts)),
        ]
        
        if include_secrets:
            env_data.append(('Secret Key', config.secret_key[:20] + '...'))
        else:
            env_data.append(('Secret Key', '[HIDDEN]'))
        
        for key, value in env_data:
            self.stdout.write(f'  {key:<20}: {value}')
        
        # Database section
        self.stdout.write(self.style.SUCCESS('\n🗄️  Databases'))
        self.stdout.write('-' * 40)
        
        for db_name, db_config in config.databases.items():
            self.stdout.write(f'  {db_name}:')
            self.stdout.write(f'    Engine: {db_config.engine}')
            if include_secrets:
                self.stdout.write(f'    Name: {db_config.name}')
                self.stdout.write(f'    Host: {db_config.host}')
                self.stdout.write(f'    Port: {db_config.port}')
            else:
                self.stdout.write(f'    Name: [HIDDEN]')
                self.stdout.write(f'    Host: [HIDDEN]')
                self.stdout.write(f'    Port: [HIDDEN]')
        
        # Cache section
        cache_configured = False
        if hasattr(config, 'cache_default') and config.cache_default:
            cache_configured = True
        
        if cache_configured:
            self.stdout.write(self.style.SUCCESS('\n⚡ Cache'))
            self.stdout.write('-' * 40)
            cache_data = [
                ('Default Cache', 'Configured'),
                ('Sessions Cache', 'Configured' if hasattr(config, 'cache_sessions') and config.cache_sessions else 'Not configured'),
            ]
            
            for key, value in cache_data:
                self.stdout.write(f'  {key:<20}: {value}')
        
        # Services section
        services_configured = []
        if hasattr(config, 'email') and config.email:
            services_configured.append(('Email', 'Configured'))
        if hasattr(config, 'telegram') and config.telegram:
            services_configured.append(('Telegram', 'Configured'))
        
        if services_configured:
            self.stdout.write(self.style.SUCCESS('\n🔧 Services'))
            self.stdout.write('-' * 40)
            
            for key, value in services_configured:
                self.stdout.write(f'  {key:<20}: {value}')
        
        # Apps section
        if hasattr(config, 'project_apps') and config.project_apps:
            self.stdout.write(self.style.SUCCESS('\n📦 Project Apps'))
            self.stdout.write('-' * 40)
            
            for app in config.project_apps:
                self.stdout.write(f'  • {app}')
        
        # Custom Middleware section
        if hasattr(config, 'custom_middleware') and config.custom_middleware:
            self.stdout.write(self.style.SUCCESS('\n🛡️  Custom Middleware'))
            self.stdout.write('-' * 40)
            
            for middleware in config.custom_middleware:
                self.stdout.write(f'  • {middleware}')
        
        self.stdout.write('\n' + '=' * 80)

    def _show_json_format(self, config, include_secrets=False):
        """Show configuration in JSON format."""
        config_data = {
            'project': {
                'name': config.project_name,
                'version': getattr(config, 'project_version', None),
                'description': getattr(config, 'project_description', None),
            },
            'environment': {
                'environment': getattr(config, '_environment', 'auto-detected'),
                'debug': config.debug,
                'allowed_hosts': config.allowed_hosts,
            },
            'databases': {},
            'cache': {
                'default_configured': hasattr(config, 'cache_default') and config.cache_default is not None,
                'sessions_configured': hasattr(config, 'cache_sessions') and config.cache_sessions is not None,
            },
            'services': {
                'email_configured': hasattr(config, 'email') and config.email is not None,
                'telegram_configured': hasattr(config, 'telegram') and config.telegram is not None,
            },
            'apps': {
                'project_apps': getattr(config, 'project_apps', []),
                'custom_middleware': getattr(config, 'custom_middleware', []),
            }
        }
        
        # Add database info
        for db_name, db_config in config.databases.items():
            config_data['databases'][db_name] = {
                'engine': db_config.engine,
                'name': db_config.name if include_secrets else '[HIDDEN]',
                'host': db_config.host if include_secrets else '[HIDDEN]',
                'port': db_config.port if include_secrets else '[HIDDEN]',
            }
        
        if include_secrets:
            config_data['environment']['secret_key'] = config.secret_key
        
        self.stdout.write(json.dumps(config_data, indent=2, default=str))