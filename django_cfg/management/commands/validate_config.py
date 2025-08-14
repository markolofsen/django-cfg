"""
Django management command to validate configuration.

Usage:
    python manage.py validate_config
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_config_toolkit import ConfigToolkit


class Command(BaseCommand):
    help = 'Validate Django Config Toolkit configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--show-details',
            action='store_true',
            help='Show detailed configuration information',
        )
        parser.add_argument(
            '--check-connections',
            action='store_true', 
            help='Test database and cache connections',
        )

    def handle(self, *args, **options):
        """Validate configuration and optionally show details."""
        self.stdout.write(
            self.style.HTTP_INFO('🚀 Django Config Toolkit - Configuration Validation')
        )
        self.stdout.write('=' * 60)
        
        try:
            # Initialize toolkit
            toolkit = ConfigToolkit()
            
            # Basic validation
            self.stdout.write(
                self.style.SUCCESS(f'✅ Configuration loaded successfully')
            )
            self.stdout.write(f'   Environment: {toolkit.environment}')
            self.stdout.write(f'   Debug: {toolkit.debug}')
            self.stdout.write(f'   Configs loaded: {toolkit._config_count}')
            self.stdout.write(f'   Init time: {toolkit._init_time_ms:.2f}ms')
            
            # Check secret key
            if len(toolkit.secret_key) >= 50:
                self.stdout.write(self.style.SUCCESS('✅ Secret key is secure'))
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️  Secret key is too short (< 50 chars)')
                )
            
            # Check extended features
            self.stdout.write('\n🎨 Extended Features:')
            features = [
                ('Unfold Admin', toolkit.unfold_enabled),
                ('Revolution API', toolkit.revolution_enabled), 
                ('Constance Settings', toolkit.constance_enabled),
                ('Advanced Logging', toolkit.logging_enabled),
            ]
            
            for name, enabled in features:
                status = '✅' if enabled else '❌'
                self.stdout.write(f'   {status} {name}')
            
            # Detailed information
            if options['show_details']:
                self._show_detailed_config(toolkit)
            
            # Connection tests
            if options['check_connections']:
                self._test_connections(toolkit)
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Configuration validation failed: {e}')
            )
            raise CommandError(f'Configuration error: {e}')
        
        self.stdout.write('=' * 60)
        self.stdout.write(
            self.style.SUCCESS('✨ Configuration validation completed!')
        )

    def _show_detailed_config(self, toolkit):
        """Show detailed configuration information."""
        self.stdout.write('\n📋 Detailed Configuration:')
        
        # Database configuration
        self.stdout.write('\n🗄️  Database:')
        self.stdout.write(f'   Engine: {toolkit.database_engine}')
        self.stdout.write(f'   Name: {toolkit.database_name}')
        if hasattr(toolkit._db_config, 'has_multiple_databases'):
            self.stdout.write(f'   Multiple DBs: {toolkit._db_config.has_multiple_databases}')
        
        # Security configuration
        self.stdout.write('\n🔒 Security:')
        self.stdout.write(f'   CORS Enabled: {toolkit.cors_enabled}')
        self.stdout.write(f'   CSRF Enabled: {toolkit.csrf_enabled}')
        self.stdout.write(f'   SSL Redirect: {toolkit.ssl_enabled}')
        
        # API configuration
        self.stdout.write('\n🌐 API:')
        self.stdout.write(f'   Page Size: {toolkit.api_page_size}')
        self.stdout.write(f'   Rate Limiting: {toolkit.api_rate_limit_enabled}')
        self.stdout.write(f'   Docs Enabled: {toolkit.api_docs_enabled}')
        
        # Cache configuration
        self.stdout.write('\n💾 Cache:')
        self.stdout.write(f'   Backend: {toolkit.cache_backend}')
        self.stdout.write(f'   Timeout: {toolkit.cache_timeout}s')
        
        # Extended features details
        if toolkit.unfold_enabled:
            self.stdout.write('\n🎨 Unfold:')
            self.stdout.write(f'   Site Title: {toolkit.site_title}')
        
        if toolkit.revolution_enabled:
            self.stdout.write('\n🚀 Revolution:')
            self.stdout.write(f'   API Prefix: {toolkit.api_prefix}')
        
        if toolkit.constance_enabled:
            self.stdout.write('\n⚙️ Constance:')
            self.stdout.write(f'   Backend: {toolkit.constance_backend}')
        
        self.stdout.write('\n📝 Logging:')
        self.stdout.write(f'   Log Level: {toolkit.log_level}')

    def _test_connections(self, toolkit):
        """Test database and cache connections."""
        self.stdout.write('\n🔗 Connection Tests:')
        
        # Test database connections
        self.stdout.write('\n🗄️  Database connections:')
        try:
            from django.db import connections
            
            for db_name in connections:
                try:
                    connection = connections[db_name]
                    with connection.cursor() as cursor:
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'   ✅ {db_name}: Connected')
                    )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ {db_name}: {str(e)}')
                    )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Database test failed: {e}')
            )
        
        # Test cache connection
        self.stdout.write('\n💾 Cache connection:')
        try:
            from django.core.cache import cache
            
            test_key = 'config_validation_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 30)
            retrieved_value = cache.get(test_key)
            
            if retrieved_value == test_value:
                self.stdout.write(
                    self.style.SUCCESS('   ✅ Cache: Working')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('   ⚠️  Cache: Read/write test failed')
                )
        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Cache test failed: {e}')
            )
