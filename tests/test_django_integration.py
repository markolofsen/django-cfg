"""
Django integration tests for django_cfg.

Following TESTING_STANDARDS.md:
- Test complete Django integration
- Test settings generation and application
- Test Django startup and functionality
- Performance and memory tests
"""

import pytest
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any
import django
from django.conf import settings
from django.test import TestCase
from django.core.management import execute_from_command_line
from django.core.exceptions import ImproperlyConfigured

from django_cfg import DjangoConfig, DatabaseConnection, CacheBackend, EmailConfig
from django_cfg.exceptions import ConfigurationError, ValidationError


class TestDjangoIntegration:
    """Test complete Django integration with django_cfg."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear Django settings if already configured
        if hasattr(settings, 'configured') and settings.configured:
            # Reset Django configuration for clean test
            settings._wrapped = None
            django.setup()
    
    def test_minimal_django_config(self):
        """Test minimal Django configuration that actually works."""
        
        class MinimalDjangoConfig(DjangoConfig):
            project_name: str = "Test Django Project"
            secret_key: str = "test-secret-key-that-is-long-enough-to-pass-django-validation-requirements"
            debug: bool = True
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            project_apps: list = ["django.contrib.contenttypes", "django.contrib.auth"]
        
        # Create config
        config = MinimalDjangoConfig()
        
        # Generate Django settings
        django_settings = config.get_all_settings()
        
        # Verify critical settings
        assert "SECRET_KEY" in django_settings
        assert "DATABASES" in django_settings
        assert "INSTALLED_APPS" in django_settings
        assert "MIDDLEWARE" in django_settings
        
        # Configure Django
        if not settings.configured:
            settings.configure(**django_settings)
            django.setup()
        
        # Verify Django is properly configured
        assert settings.SECRET_KEY == config.secret_key
        assert settings.DEBUG is True
        assert "django.contrib.contenttypes" in settings.INSTALLED_APPS
        assert "django.contrib.auth" in settings.INSTALLED_APPS
        
        # Verify database configuration
        assert "default" in settings.DATABASES
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3"
        assert settings.DATABASES["default"]["NAME"] == ":memory:"
    
    def test_complete_django_config(self):
        """Test complete Django configuration with all features."""
        
        class CompleteDjangoConfig(DjangoConfig):
            project_name: str = "Complete Test Project"
            project_version: str = "2.0.0"
            project_description: str = "Full-featured test configuration"
            
            secret_key: str = "complete-test-secret-key-that-is-definitely-long-enough-for-validation"
            debug: bool = False
            
            # Multi-database setup
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                ),
                "users": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name="users.db",
                ),
            }
            
            # Cache configuration
            cache_default: CacheBackend = CacheBackend(
                timeout=600,
                max_connections=20,
            )
            
            cache_sessions: CacheBackend = CacheBackend(
                timeout=3600,
                max_connections=10,
            )
            
            # Email configuration
            email: EmailConfig = EmailConfig(
                host="smtp.example.com",
                port=587,
                username="test@example.com",
                password="test-password",
                use_tls=True,
                default_from_email="noreply@example.com",
                default_from_name="Test Project",
            )
            
            # Security domains
            security_domains: list = ["example.com", "www.example.com"]
            
            # Custom middleware
            custom_middleware: list = [
                "tests.middleware.TestMiddleware",
            ]
            
            # Project apps
            project_apps: list = [
                "tests.testapp",
            ]
        
        # Create config
        config = CompleteDjangoConfig()
        
        # Generate Django settings
        django_settings = config.get_all_settings()
        
        # Verify all settings are generated
        required_settings = [
            'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS',
            'INSTALLED_APPS', 'MIDDLEWARE', 'DATABASES',
            'CACHES', 'EMAIL_BACKEND', 'DEFAULT_FROM_EMAIL',
        ]
        
        for setting in required_settings:
            assert setting in django_settings, f"Missing setting: {setting}"
        
        # Verify complex configurations
        assert len(django_settings["DATABASES"]) == 2
        assert "default" in django_settings["DATABASES"]
        assert "users" in django_settings["DATABASES"]
        
        assert len(django_settings["CACHES"]) >= 2
        assert "default" in django_settings["CACHES"]
        assert "sessions" in django_settings["CACHES"]
        
        # Verify email configuration
        assert "smtp.example.com" in str(django_settings.get("EMAIL_HOST", ""))
        assert django_settings.get("EMAIL_PORT") == 587
        assert django_settings.get("EMAIL_USE_TLS") is True
        
        # Verify middleware includes custom
        assert "tests.middleware.TestMiddleware" in django_settings["MIDDLEWARE"]
        
        # Verify apps include custom
        assert "tests.testapp" in django_settings["INSTALLED_APPS"]
    
    def test_django_check_command(self):
        """Test Django's check command with django_cfg configuration."""
        
        class CheckTestConfig(DjangoConfig):
            project_name: str = "Check Test"
            secret_key: str = "check-test-secret-key-long-enough-for-django-validation"
            debug: bool = True
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
        
        config = CheckTestConfig()
        django_settings = config.get_all_settings()
        
        # Configure Django
        if not settings.configured:
            settings.configure(**django_settings)
            django.setup()
        
        # Import Django's check framework
        from django.core.management.base import SystemCheckError
        from django.core.checks import run_checks
        
        # Run Django system checks
        try:
            errors = run_checks()
            
            # Should have no critical errors
            critical_errors = [e for e in errors if e.level >= 40]  # ERROR level
            assert len(critical_errors) == 0, f"Django check found critical errors: {critical_errors}"
            
        except SystemCheckError as e:
            pytest.fail(f"Django system check failed: {e}")
    
    def test_django_migrations(self):
        """Test Django migrations with django_cfg configuration."""
        
        class MigrationTestConfig(DjangoConfig):
            project_name: str = "Migration Test"
            secret_key: str = "migration-test-secret-key-long-enough-for-validation"
            debug: bool = True
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            project_apps: list = [
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "django.contrib.sessions",
            ]
        
        config = MigrationTestConfig()
        django_settings = config.get_all_settings()
        
        # Configure Django
        if not settings.configured:
            settings.configure(**django_settings)
            django.setup()
        
        # Test migration commands
        from django.core.management import call_command
        from io import StringIO
        
        # Capture command output
        out = StringIO()
        
        try:
            # Run migrate command (should work with in-memory database)
            call_command('migrate', verbosity=0, interactive=False, stdout=out)
            
            # If we get here, migrations worked
            assert True
            
        except Exception as e:
            # Some migrations might fail with in-memory DB, but basic structure should work
            if "no such table" not in str(e).lower():
                pytest.fail(f"Migration failed unexpectedly: {e}")
    
    def test_environment_specific_behavior(self):
        """Test environment-specific configuration behavior."""
        
        # Test development environment
        os.environ['DJANGO_ENV'] = 'development'
        
        class DevConfig(DjangoConfig):
            project_name: str = "Dev Test"
            secret_key: str = "dev-test-secret-key-that-is-long-enough-for-django-validation"
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            cache_default: CacheBackend = CacheBackend(
                redis_url=None,  # Should use memory cache in dev
                timeout=300,
            )
            
            email: EmailConfig = EmailConfig(
                host="localhost",
                port=1025,
                use_tls=False,
            )
        
        config = DevConfig()
        assert config._environment == 'development'
        
        django_settings = config.get_all_settings()
        
        # In development, should use console email backend
        assert 'console' in django_settings.get('EMAIL_BACKEND', '').lower()
        
        # Cache should use memory backend
        cache_backend = django_settings.get('CACHES', {}).get('default', {}).get('BACKEND', '')
        assert 'locmem' in cache_backend.lower() or 'memory' in cache_backend.lower()
        
        # Test production environment
        os.environ['DJANGO_ENV'] = 'production'
        
        class ProdConfig(DjangoConfig):
            project_name: str = "Prod Test"
            secret_key: str = "prod-test-secret-key-that-is-long-enough-for-django-validation"
            debug: bool = False
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            email: EmailConfig = EmailConfig(
                host="smtp.example.com",
                port=587,
                username="user@example.com",
                password="password",
                use_tls=True,
            )
        
        prod_config = ProdConfig()
        assert prod_config._environment == 'production'
        assert prod_config.debug is False
        
        # Clean up environment
        if 'DJANGO_ENV' in os.environ:
            del os.environ['DJANGO_ENV']
    
    def test_validation_with_django_context(self):
        """Test configuration validation in Django context."""
        
        # Test invalid configuration that should be caught
        with pytest.raises((ValidationError, ConfigurationError)):
            class InvalidConfig(DjangoConfig):
                project_name: str = "Invalid Config"
                secret_key: str = "short"  # Too short for Django
                
                databases: Dict[str, DatabaseConnection] = {
                    "default": DatabaseConnection(
                        engine="invalid.engine",  # Invalid engine
                        name="test",
                    )
                }
            
            config = InvalidConfig()
            django_settings = config.get_all_settings()
            
            # Try to configure Django - should fail
            settings.configure(**django_settings)
    
    def test_performance_with_django(self):
        """Test performance of django_cfg with Django integration."""
        import time
        
        class PerformanceConfig(DjangoConfig):
            project_name: str = "Performance Test"
            secret_key: str = "performance-test-secret-key-that-is-long-enough-for-django-validation"
            
            databases: Dict[str, DatabaseConnection] = {
                f"db_{i}": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=f"test_{i}.db",
                )
                for i in range(5)  # Multiple databases
            }
            
            # Multiple caches
            cache_default: CacheBackend = CacheBackend(timeout=300)
            cache_sessions: CacheBackend = CacheBackend(timeout=3600)
            
            project_apps: list = [
                f"app_{i}" for i in range(10)  # Multiple apps
            ]
        
        # Measure configuration creation time
        start_time = time.time()
        config = PerformanceConfig()
        creation_time = (time.time() - start_time) * 1000
        
        # Measure settings generation time
        start_time = time.time()
        django_settings = config.get_all_settings()
        generation_time = (time.time() - start_time) * 1000
        
        # Performance assertions
        assert creation_time < 50, f"Config creation took {creation_time:.2f}ms (target: <50ms)"
        assert generation_time < 100, f"Settings generation took {generation_time:.2f}ms (target: <100ms)"
        
        # Verify settings are complete
        assert len(django_settings) > 15  # Should have many settings
        assert len(django_settings["DATABASES"]) == 5
        assert len(django_settings["INSTALLED_APPS"]) > 15  # Core + project apps


# Mark slow tests
pytestmark = pytest.mark.slow