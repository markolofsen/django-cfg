"""
Check Settings Command for Django Config Toolkit
Comprehensive validation of Django settings and configuration.
"""

import os
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import questionary
from datetime import datetime

from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = 'Comprehensive validation of Django settings and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all checks'
        )
        parser.add_argument(
            '--security',
            action='store_true',
            help='Check security settings only'
        )
        parser.add_argument(
            '--database',
            action='store_true',
            help='Check database settings only'
        )
        parser.add_argument(
            '--email',
            action='store_true',
            help='Check email settings only'
        )
        parser.add_argument(
            '--cache',
            action='store_true',
            help='Check cache settings only'
        )
        parser.add_argument(
            '--static',
            action='store_true',
            help='Check static files settings only'
        )
        parser.add_argument(
            '--export',
            type=str,
            help='Export settings report to file'
        )

    def handle(self, *args, **options):
        if options['all']:
            self.run_all_checks()
        elif options['security']:
            self.check_security_settings()
        elif options['database']:
            self.check_database_settings()
        elif options['email']:
            self.check_email_settings()
        elif options['cache']:
            self.check_cache_settings()
        elif options['static']:
            self.check_static_settings()
        elif options['export']:
            self.export_settings_report(options['export'])
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with settings check options"""
        self.stdout.write(self.style.SUCCESS('\n🔍 Settings Validation Tool - Django Config Toolkit\n'))

        choices = [
            questionary.Choice('🔍 Run All Checks', value='all'),
            questionary.Choice('🔒 Security Settings', value='security'),
            questionary.Choice('🗄️  Database Settings', value='database'),
            questionary.Choice('📧 Email Settings', value='email'),
            questionary.Choice('💾 Cache Settings', value='cache'),
            questionary.Choice('📁 Static Files Settings', value='static'),
            questionary.Choice('📊 Export Settings Report', value='export'),
            questionary.Choice('❌ Exit', value='exit')
        ]

        choice = questionary.select(
            'Select check type:',
            choices=choices
        ).ask()

        if choice == 'all':
            self.run_all_checks()
        elif choice == 'security':
            self.check_security_settings()
        elif choice == 'database':
            self.check_database_settings()
        elif choice == 'email':
            self.check_email_settings()
        elif choice == 'cache':
            self.check_cache_settings()
        elif choice == 'static':
            self.check_static_settings()
        elif choice == 'export':
            filename = questionary.text('Export filename:', default='settings_report.txt').ask()
            self.export_settings_report(filename)
        elif choice == 'exit':
            self.stdout.write('Goodbye! 👋')
            return

    def run_all_checks(self):
        """Run all settings checks"""
        self.stdout.write(self.style.SUCCESS('🔍 Running All Settings Checks...\n'))
        
        checks = [
            ('🔒 Security Settings', self.check_security_settings),
            ('🗄️  Database Settings', self.check_database_settings),
            ('📧 Email Settings', self.check_email_settings),
            ('💾 Cache Settings', self.check_cache_settings),
            ('📁 Static Files Settings', self.check_static_settings),
            ('⚙️  ConfigToolkit Settings', self.check_config_toolkit_settings),
        ]
        
        results = {}
        for name, check_func in checks:
            self.stdout.write(f'\n{name}:')
            try:
                result = check_func(silent=True)
                results[name] = result
            except Exception as e:
                self.stdout.write(f'  ❌ Error: {e}')
                results[name] = False
        
        # Summary
        self.stdout.write('\n📊 Summary:')
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        self.stdout.write(f'  ✅ Passed: {passed}/{total}')
        self.stdout.write(f'  ❌ Failed: {total - passed}/{total}')

    def check_security_settings(self, silent=False):
        """Check security settings"""
        if not silent:
            self.stdout.write(self.style.SUCCESS('🔒 Checking Security Settings...'))
        
        issues = []
        warnings = []
        
        # SECRET_KEY
        if not hasattr(settings, 'SECRET_KEY') or not settings.SECRET_KEY:
            issues.append('SECRET_KEY is not configured')
        elif len(settings.SECRET_KEY) < 50:
            warnings.append('SECRET_KEY is too short (should be at least 50 characters)')
        
        # DEBUG
        if settings.DEBUG:
            warnings.append('DEBUG is enabled (should be False in production)')
        
        # ALLOWED_HOSTS
        if not hasattr(settings, 'ALLOWED_HOSTS') or not settings.ALLOWED_HOSTS:
            issues.append('ALLOWED_HOSTS is not configured')
        elif '*' in settings.ALLOWED_HOSTS:
            warnings.append('ALLOWED_HOSTS contains wildcard (*) - security risk')
        
        # CSRF
        if not hasattr(settings, 'CSRF_COOKIE_SECURE') or not settings.CSRF_COOKIE_SECURE:
            warnings.append('CSRF_COOKIE_SECURE should be True in production')
        
        # Session
        if not hasattr(settings, 'SESSION_COOKIE_SECURE') or not settings.SESSION_COOKIE_SECURE:
            warnings.append('SESSION_COOKIE_SECURE should be True in production')
        
        # HTTPS
        if not hasattr(settings, 'SECURE_SSL_REDIRECT') or not settings.SECURE_SSL_REDIRECT:
            warnings.append('SECURE_SSL_REDIRECT should be True in production')
        
        if not silent:
            self._print_issues_and_warnings(issues, warnings)
        
        return len(issues) == 0

    def check_database_settings(self, silent=False):
        """Check database settings"""
        if not silent:
            self.stdout.write(self.style.SUCCESS('🗄️  Checking Database Settings...'))
        
        issues = []
        warnings = []
        
        # DATABASES
        if not hasattr(settings, 'DATABASES'):
            issues.append('DATABASES setting is missing')
            return False
        
        if 'default' not in settings.DATABASES:
            issues.append('Default database is not configured')
            return False
        
        default_db = settings.DATABASES['default']
        
        # Engine
        if 'ENGINE' not in default_db:
            issues.append('Database ENGINE is not configured')
        else:
            engine = default_db['ENGINE']
            if 'sqlite' in engine.lower() and not settings.DEBUG:
                warnings.append('SQLite is not recommended for production')
        
        # Connection settings
        if 'NAME' not in default_db:
            issues.append('Database NAME is not configured')
        
        # Connection pooling
        if 'CONN_MAX_AGE' not in default_db:
            warnings.append('CONN_MAX_AGE not configured (recommended: 600)')
        
        # Multiple databases
        if len(settings.DATABASES) > 1:
            self.stdout.write(f'  📊 Multiple databases configured: {len(settings.DATABASES)}')
            
            # Check routing
            if not hasattr(settings, 'DATABASE_ROUTERS'):
                warnings.append('Multiple databases detected but no DATABASE_ROUTERS configured')
        
        if not silent:
            self._print_issues_and_warnings(issues, warnings)
        
        return len(issues) == 0

    def check_email_settings(self, silent=False):
        """Check email settings"""
        if not silent:
            self.stdout.write(self.style.SUCCESS('📧 Checking Email Settings...'))
        
        issues = []
        warnings = []
        
        # EMAIL_BACKEND
        if not hasattr(settings, 'EMAIL_BACKEND'):
            warnings.append('EMAIL_BACKEND not configured')
        else:
            backend = settings.EMAIL_BACKEND
            if 'console' in backend and not settings.DEBUG:
                warnings.append('Console email backend in production')
        
        # SMTP settings
        if hasattr(settings, 'EMAIL_HOST'):
            if not settings.EMAIL_HOST:
                issues.append('EMAIL_HOST is empty')
            
            if hasattr(settings, 'EMAIL_PORT') and not settings.EMAIL_PORT:
                issues.append('EMAIL_PORT is not configured')
            
            if hasattr(settings, 'EMAIL_HOST_USER') and not settings.EMAIL_HOST_USER:
                warnings.append('EMAIL_HOST_USER not configured')
            
            if hasattr(settings, 'EMAIL_HOST_PASSWORD') and not settings.EMAIL_HOST_PASSWORD:
                warnings.append('EMAIL_HOST_PASSWORD not configured')
        
        # DEFAULT_FROM_EMAIL
        if not hasattr(settings, 'DEFAULT_FROM_EMAIL') or not settings.DEFAULT_FROM_EMAIL:
            warnings.append('DEFAULT_FROM_EMAIL not configured')
        
        if not silent:
            self._print_issues_and_warnings(issues, warnings)
        
        return len(issues) == 0

    def check_cache_settings(self, silent=False):
        """Check cache settings"""
        if not silent:
            self.stdout.write(self.style.SUCCESS('💾 Checking Cache Settings...'))
        
        issues = []
        warnings = []
        
        # CACHES
        if not hasattr(settings, 'CACHES'):
            warnings.append('CACHES setting not configured')
        else:
            if 'default' not in settings.CACHES:
                issues.append('Default cache is not configured')
            else:
                default_cache = settings.CACHES['default']
                
                # Backend
                if 'BACKEND' not in default_cache:
                    issues.append('Cache BACKEND not configured')
                else:
                    backend = default_cache['BACKEND']
                    if 'locmem' in backend and not settings.DEBUG:
                        warnings.append('Local memory cache in production')
                
                # Location
                if 'LOCATION' not in default_cache:
                    warnings.append('Cache LOCATION not configured')
                
                # Timeout
                if 'TIMEOUT' not in default_cache:
                    warnings.append('Cache TIMEOUT not configured')
        
        if not silent:
            self._print_issues_and_warnings(issues, warnings)
        
        return len(issues) == 0

    def check_static_settings(self, silent=False):
        """Check static files settings"""
        if not silent:
            self.stdout.write(self.style.SUCCESS('📁 Checking Static Files Settings...'))
        
        issues = []
        warnings = []
        
        # STATIC_URL
        if not hasattr(settings, 'STATIC_URL') or not settings.STATIC_URL:
            issues.append('STATIC_URL not configured')
        
        # STATIC_ROOT
        if not hasattr(settings, 'STATIC_ROOT') or not settings.STATIC_ROOT:
            warnings.append('STATIC_ROOT not configured (required for collectstatic)')
        else:
            static_root = Path(settings.STATIC_ROOT)
            if not static_root.exists():
                warnings.append(f'STATIC_ROOT directory does not exist: {settings.STATIC_ROOT}')
        
        # STATICFILES_DIRS
        if hasattr(settings, 'STATICFILES_DIRS'):
            for static_dir in settings.STATICFILES_DIRS:
                if not Path(static_dir).exists():
                    warnings.append(f'Static directory does not exist: {static_dir}')
        
        # Media files
        if hasattr(settings, 'MEDIA_URL') and not hasattr(settings, 'MEDIA_ROOT'):
            warnings.append('MEDIA_URL configured but MEDIA_ROOT not set')
        
        if not silent:
            self._print_issues_and_warnings(issues, warnings)
        
        return len(issues) == 0

    def check_config_toolkit_settings(self, silent=False):
        """Check ConfigToolkit settings"""
        if not silent:
            self.stdout.write(self.style.SUCCESS('⚙️  Checking ConfigToolkit Settings...'))
        
        issues = []
        warnings = []
        
        try:
            config = ConfigToolkit()
            
            # Check if configuration is loaded
            if hasattr(config, 'debug'):
                self.stdout.write(f'  ✅ Debug mode: {config.debug}')
            
            if hasattr(config, 'database_url'):
                self.stdout.write(f'  ✅ Database URL: {config.database_url[:50]}...')
            
            # Check environment detection
            if hasattr(config, 'environment'):
                self.stdout.write(f'  ✅ Environment: {config.environment}')
            
        except Exception as e:
            issues.append(f'ConfigToolkit error: {e}')
        
        if not silent:
            self._print_issues_and_warnings(issues, warnings)
        
        return len(issues) == 0

    def _print_issues_and_warnings(self, issues, warnings):
        """Print issues and warnings"""
        if issues:
            self.stdout.write(self.style.ERROR('  ❌ Issues:'))
            for issue in issues:
                self.stdout.write(f'    - {issue}')
        
        if warnings:
            self.stdout.write(self.style.WARNING('  ⚠️  Warnings:'))
            for warning in warnings:
                self.stdout.write(f'    - {warning}')
        
        if not issues and not warnings:
            self.stdout.write(self.style.SUCCESS('  ✅ All checks passed'))

    def export_settings_report(self, filename):
        """Export settings report to file"""
        self.stdout.write(self.style.SUCCESS(f'📊 Exporting Settings Report to {filename}...'))
        
        # Create reports directory
        reports_dir = Path('reports')
        reports_dir.mkdir(exist_ok=True)
        
        report_path = reports_dir / filename
        
        with open(report_path, 'w') as f:
            f.write('Django Settings Report\n')
            f.write('=====================\n\n')
            f.write(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
            f.write(f'Django Version: {self._get_django_version()}\n')
            f.write(f'Python Version: {sys.version}\n\n')
            
            # Run all checks and capture output
            checks = [
                ('Security Settings', self.check_security_settings),
                ('Database Settings', self.check_database_settings),
                ('Email Settings', self.check_email_settings),
                ('Cache Settings', self.check_cache_settings),
                ('Static Files Settings', self.check_static_settings),
                ('ConfigToolkit Settings', self.check_config_toolkit_settings),
            ]
            
            for name, check_func in checks:
                f.write(f'{name}:\n')
                f.write('-' * len(name) + '\n')
                
                # Capture stdout temporarily
                import io
                from contextlib import redirect_stdout
                
                output = io.StringIO()
                with redirect_stdout(output):
                    try:
                        check_func(silent=True)
                    except Exception as e:
                        f.write(f'Error: {e}\n')
                
                f.write(output.getvalue())
                f.write('\n')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Report exported to: {report_path}'))

    def _get_django_version(self):
        """Get Django version"""
        try:
            import django
            return django.get_version()
        except:
            return 'Unknown'
