"""
Django CFG Settings Checker

Comprehensive validation and debugging tool for django-cfg configuration.
Helps diagnose email, database, and other configuration issues.
"""

import os
import sys
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import get_connection
from datetime import datetime


class Command(BaseCommand):
    """Command to check and debug django-cfg settings."""

    help = "Check and debug django-cfg configuration settings"

    def add_arguments(self, parser):
        parser.add_argument(
            '--email-test',
            action='store_true',
            help='Test email configuration and SMTP connection'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed configuration information'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        self.stdout.write(self.style.SUCCESS("\n🔍 Django CFG Settings Checker\n"))
        
        # Show basic info
        self.show_environment_info()
        self.show_email_config()
        
        if options['verbose']:
            self.show_database_config()
            self.show_app_config()
            self.show_cors_config()
        
        if options['email_test']:
            self.test_email_connection()

    def show_environment_info(self):
        """Show environment and debug information."""
        self.stdout.write(self.style.SUCCESS("🌍 Environment Information:"))
        
        # Debug mode
        debug = getattr(settings, 'DEBUG', False)
        self.stdout.write(f"  🐞 DEBUG: {debug}")
        
        # Environment detection
        env_vars = {
            'DJANGO_SETTINGS_MODULE': os.environ.get('DJANGO_SETTINGS_MODULE', 'Not set'),
            'ENVIRONMENT': os.environ.get('ENVIRONMENT', 'Not set'),
        }
        
        for key, value in env_vars.items():
            self.stdout.write(f"  📝 {key}: {value}")

    def show_email_config(self):
        """Show detailed email configuration."""
        self.stdout.write(self.style.SUCCESS("\n📧 Email Configuration:"))
        
        # Basic email settings
        email_settings = {
            'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', 'Not set'),
            'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', 'Not set'),
            'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', 'Not set'),
            'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', 'Not set'),
            'EMAIL_USE_SSL': getattr(settings, 'EMAIL_USE_SSL', 'Not set'),
            'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', 'Not set'),
            'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set'),
        }
        
        # Show password status (not actual password)
        password_set = bool(getattr(settings, 'EMAIL_HOST_PASSWORD', None))
        email_settings['EMAIL_HOST_PASSWORD'] = '***SET***' if password_set else 'Not set'
        
        for key, value in email_settings.items():
            icon = "✅" if value != 'Not set' else "❌"
            self.stdout.write(f"  {icon} {key}: {value}")
        
        # Analyze backend type
        backend = email_settings['EMAIL_BACKEND']
        if 'console' in backend:
            self.stdout.write(self.style.WARNING("  ⚠️  Console backend - emails will be printed to console"))
        elif 'locmem' in backend:
            self.stdout.write(self.style.WARNING("  ⚠️  Local memory backend - emails stored in memory"))
        elif 'filebased' in backend:
            self.stdout.write(self.style.WARNING("  ⚠️  File backend - emails saved to files"))
        elif 'smtp' in backend:
            self.stdout.write(self.style.SUCCESS("  📤 SMTP backend - emails will be sent via SMTP"))
        
        # Check django-cfg email service
        try:
            from django_cfg.modules.django_email import DjangoEmailService
            email_service = DjangoEmailService()
            backend_info = email_service.get_backend_info()
            
            self.stdout.write(f"\n  🔧 Django CFG Email Service:")
            self.stdout.write(f"    Backend: {backend_info['backend']}")
            self.stdout.write(f"    Configured: {backend_info['configured']}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Django CFG Email Service error: {e}"))

    def show_database_config(self):
        """Show database configuration."""
        self.stdout.write(self.style.SUCCESS("\n🗄️  Database Configuration:"))
        
        databases = getattr(settings, 'DATABASES', {})
        for db_name, db_config in databases.items():
            engine = db_config.get('ENGINE', 'Unknown')
            name = db_config.get('NAME', 'Unknown')
            host = db_config.get('HOST', 'localhost')
            port = db_config.get('PORT', 'default')
            
            self.stdout.write(f"  📊 {db_name}:")
            self.stdout.write(f"    Engine: {engine}")
            self.stdout.write(f"    Name: {name}")
            if host and host != 'localhost':
                self.stdout.write(f"    Host: {host}:{port}")

    def show_app_config(self):
        """Show installed apps configuration."""
        self.stdout.write(self.style.SUCCESS("\n📦 Django CFG Apps:"))
        
        installed_apps = getattr(settings, 'INSTALLED_APPS', [])
        cfg_apps = [app for app in installed_apps if 'django_cfg' in app]
        
        for app in cfg_apps:
            self.stdout.write(f"  ✅ {app}")
        
        if not cfg_apps:
            self.stdout.write("  ❌ No django_cfg apps found")

    def show_cors_config(self):
        """Show CORS and security configuration."""
        self.stdout.write(self.style.SUCCESS("\n🌐 CORS & Security Configuration:"))
        
        # Get current config
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
            
            if config:
                self.stdout.write(f"  📋 Security Domains: {config.security_domains}")
                self.stdout.write(f"  🔗 CORS Headers: {config.cors_allow_headers}")
                self.stdout.write(f"  🔒 SSL Redirect: {config.ssl_redirect}")
            else:
                self.stdout.write("  ⚠️  No django-cfg config instance found")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Error getting config: {e}"))
        
        # Show Django settings
        cors_settings = {
            'CORS_ALLOW_ALL_ORIGINS': getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', None),
            'CORS_ALLOWED_ORIGINS': getattr(settings, 'CORS_ALLOWED_ORIGINS', None),
            'CORS_ALLOW_CREDENTIALS': getattr(settings, 'CORS_ALLOW_CREDENTIALS', None),
            'CORS_ALLOW_HEADERS': getattr(settings, 'CORS_ALLOW_HEADERS', None),
            'CSRF_TRUSTED_ORIGINS': getattr(settings, 'CSRF_TRUSTED_ORIGINS', None),
        }
        
        self.stdout.write("\n  🔧 Generated Django Settings:")
        for key, value in cors_settings.items():
            if value is not None:
                icon = "✅"
                if key == 'CORS_ALLOW_HEADERS' and isinstance(value, list):
                    # Show first few headers for readability
                    display_value = value[:3] + ['...'] if len(value) > 3 else value
                    self.stdout.write(f"  {icon} {key}: {display_value} ({len(value)} total)")
                elif key in ['CORS_ALLOWED_ORIGINS', 'CSRF_TRUSTED_ORIGINS'] and isinstance(value, list):
                    self.stdout.write(f"  {icon} {key}: {value}")
                else:
                    self.stdout.write(f"  {icon} {key}: {value}")
            else:
                self.stdout.write(f"  ⭕ {key}: Not set")
        
        # Analysis
        self.stdout.write("\n  📊 CORS Analysis:")
        if cors_settings['CORS_ALLOW_ALL_ORIGINS']:
            self.stdout.write("  🟡 Development mode: All origins allowed")
        elif cors_settings['CORS_ALLOWED_ORIGINS']:
            origins_count = len(cors_settings['CORS_ALLOWED_ORIGINS'])
            self.stdout.write(f"  🟢 Production mode: {origins_count} specific origins allowed")
        else:
            self.stdout.write("  🔴 No CORS origins configured")

    def test_email_connection(self):
        """Test email connection."""
        self.stdout.write(self.style.SUCCESS("\n🧪 Testing Email Connection:"))
        
        try:
            # Test Django's email connection
            connection = get_connection()
            connection.open()
            self.stdout.write("  ✅ Django email connection successful")
            connection.close()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Django email connection failed: {e}"))
        
        try:
            # Test django-cfg email service
            from django_cfg.modules.django_email import DjangoEmailService
            email_service = DjangoEmailService()
            
            # Try to send a test email (dry run)
            self.stdout.write("  🔍 Testing django-cfg email service...")
            
            # Just check if service can be initialized
            backend_info = email_service.get_backend_info()
            if backend_info['configured']:
                self.stdout.write("  ✅ Django CFG email service is properly configured")
            else:
                self.stdout.write(self.style.WARNING("  ⚠️  Django CFG email service configuration incomplete"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  ❌ Django CFG email service test failed: {e}"))
        
        # Show recommendations
        self.show_email_recommendations()

    def show_email_recommendations(self):
        """Show email configuration recommendations."""
        self.stdout.write(self.style.SUCCESS("\n💡 Email Configuration Recommendations:"))
        
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        debug = getattr(settings, 'DEBUG', False)
        
        if 'console' in backend and not debug:
            self.stdout.write("  ⚠️  Console backend in production - emails won't be delivered")
            self.stdout.write("     Consider switching to SMTP backend")
        
        if 'smtp' in backend:
            host = getattr(settings, 'EMAIL_HOST', '')
            user = getattr(settings, 'EMAIL_HOST_USER', '')
            password = getattr(settings, 'EMAIL_HOST_PASSWORD', '')
            
            if not host:
                self.stdout.write("  ❌ SMTP host not configured")
            if not user:
                self.stdout.write("  ❌ SMTP username not configured")
            if not password:
                self.stdout.write("  ❌ SMTP password not configured")
            
            if host and user and password:
                self.stdout.write("  ✅ SMTP configuration appears complete")
        
        self.stdout.write("\n  📚 For more help:")
        self.stdout.write("     - Check your config.dev.yaml email settings")
        self.stdout.write("     - Verify SMTP credentials with your email provider")
        self.stdout.write("     - Test with: python manage.py test_email")
