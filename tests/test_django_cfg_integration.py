"""
Simple integration test for django_cfg without full Django setup.

Tests that django_cfg generates valid Django settings that would work.
"""

import pytest
import os
from typing import Dict

from django_cfg import DjangoConfig, DatabaseConnection, CacheBackend, EmailConfig


class TestDjangoCfgIntegration:
    """Test django_cfg integration without full Django environment."""
    
    def test_settings_generation_complete(self):
        """Test that django_cfg generates complete Django settings."""
        
        class TestConfig(DjangoConfig):
            project_name: str = "Integration Test"
            secret_key: str = "integration-test-secret-key-that-is-definitely-long-enough-for-validation"
            debug: bool = True
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            root_urlconf: str = "tests.urls"
        
        config = TestConfig()
        settings = config.get_all_settings()
        
        # Test all required Django settings are present
        required_settings = [
            'SECRET_KEY',
            'DEBUG', 
            'ALLOWED_HOSTS',
            'INSTALLED_APPS',
            'MIDDLEWARE',
            'DATABASES',
            'CACHES',
            'ROOT_URLCONF',
            'TEMPLATES',
            'STATIC_URL',
            'DEFAULT_AUTO_FIELD',
            'USE_I18N',
            'USE_TZ',
            'LANGUAGE_CODE',
            'TIME_ZONE',
        ]
        
        for setting in required_settings:
            assert setting in settings, f"Missing required Django setting: {setting}"
        
        # Test setting values
        assert settings['SECRET_KEY'] == config.secret_key
        assert settings['DEBUG'] is True
        assert settings['ROOT_URLCONF'] == "tests.urls"
        
        # Test database configuration
        assert 'default' in settings['DATABASES']
        assert settings['DATABASES']['default']['ENGINE'] == "django.db.backends.sqlite3"
        assert settings['DATABASES']['default']['NAME'] == ":memory:"
        
        # Test installed apps include Django core
        installed_apps = settings['INSTALLED_APPS']
        core_apps = [
            'django.contrib.admin',
            'django.contrib.auth', 
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
        ]
        
        for app in core_apps:
            assert app in installed_apps, f"Missing core Django app: {app}"
        
        # Test middleware includes Django core
        middleware = settings['MIDDLEWARE']
        core_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.middleware.clickjacking.XFrameOptionsMiddleware',
        ]
        
        for mw in core_middleware:
            assert mw in middleware, f"Missing core Django middleware: {mw}"
    
    def test_multi_database_configuration(self):
        """Test multiple database configuration."""
        
        class MultiDBConfig(DjangoConfig):
            project_name: str = "Multi DB Test"
            secret_key: str = "multi-db-test-secret-key-that-is-definitely-long-enough-for-validation"
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name="default.db",
                ),
                "users": DatabaseConnection(
                    engine="django.db.backends.sqlite3", 
                    name="users.db",
                ),
                "analytics": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name="analytics.db",
                ),
            }
        
        config = MultiDBConfig()
        settings = config.get_all_settings()
        
        # Should have all databases
        databases = settings['DATABASES']
        assert len(databases) == 3
        assert 'default' in databases
        assert 'users' in databases
        assert 'analytics' in databases
        
        # Each should have proper configuration
        for db_name, db_config in databases.items():
            assert 'ENGINE' in db_config
            assert 'NAME' in db_config
            assert db_config['ENGINE'] == "django.db.backends.sqlite3"
            assert db_config['NAME'] == f"{db_name}.db"
    
    def test_cache_configuration(self):
        """Test cache configuration generation."""
        
        class CacheConfig(DjangoConfig):
            project_name: str = "Cache Test"
            secret_key: str = "cache-test-secret-key-that-is-definitely-long-enough-for-validation"
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            cache_default: CacheBackend = CacheBackend(
                timeout=600,
                max_connections=20,
            )
            
            cache_sessions: CacheBackend = CacheBackend(
                timeout=3600,
                max_connections=10,
            )
        
        config = CacheConfig()
        settings = config.get_all_settings()
        
        # Should have cache configuration
        caches = settings['CACHES']
        assert 'default' in caches
        assert 'sessions' in caches
        
        # Test cache settings
        default_cache = caches['default']
        assert 'BACKEND' in default_cache
        assert 'TIMEOUT' in default_cache
        assert default_cache['TIMEOUT'] == 600
        
        sessions_cache = caches['sessions']
        assert 'BACKEND' in sessions_cache
        assert 'TIMEOUT' in sessions_cache
        assert sessions_cache['TIMEOUT'] == 3600
    
    def test_email_configuration(self):
        """Test email configuration generation."""
        
        class EmailTestConfig(DjangoConfig):
            project_name: str = "Email Test"
            secret_key: str = "email-test-secret-key-that-is-definitely-long-enough-for-validation"
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            email: EmailConfig = EmailConfig(
                host="smtp.example.com",
                port=587,
                username="test@example.com",
                password="test-password",
                use_tls=True,
                default_from_email="noreply@example.com",
                default_from_name="Test Project",
            )
        
        config = EmailTestConfig()
        settings = config.get_all_settings()
        
        # Should have email configuration
        assert 'EMAIL_BACKEND' in settings
        assert 'EMAIL_HOST' in settings
        assert 'EMAIL_PORT' in settings
        assert 'EMAIL_HOST_USER' in settings
        assert 'EMAIL_HOST_PASSWORD' in settings
        assert 'EMAIL_USE_TLS' in settings
        assert 'DEFAULT_FROM_EMAIL' in settings
        
        # Test values
        assert settings['EMAIL_HOST'] == "smtp.example.com"
        assert settings['EMAIL_PORT'] == 587
        assert settings['EMAIL_HOST_USER'] == "test@example.com"
        assert settings['EMAIL_HOST_PASSWORD'] == "test-password"
        assert settings['EMAIL_USE_TLS'] is True
        assert settings['DEFAULT_FROM_EMAIL'] == "noreply@example.com"
    
    def test_environment_specific_settings(self):
        """Test environment-specific settings generation."""
        
        # Test development environment
        os.environ['DJANGO_ENV'] = 'development'
        
        class DevConfig(DjangoConfig):
            project_name: str = "Dev Test"
            secret_key: str = "dev-test-secret-key-that-is-definitely-long-enough-for-validation"
            debug: bool = True
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
        
        config = DevConfig()
        settings = config.get_all_settings()
        
        # In development, should have development-specific settings
        assert settings['DEBUG'] is True
        
        # Email should use console backend in development
        assert 'console' in settings.get('EMAIL_BACKEND', '').lower()
        
        # Test production environment
        os.environ['DJANGO_ENV'] = 'production'
        
        class ProdConfig(DjangoConfig):
            project_name: str = "Prod Test"
            secret_key: str = "prod-test-secret-key-that-is-definitely-long-enough-for-validation"
            debug: bool = False
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
        
        prod_config = ProdConfig()
        prod_settings = prod_config.get_all_settings()
        
        # In production, should have production-specific settings
        assert prod_settings['DEBUG'] is False
        
        # Clean up
        if 'DJANGO_ENV' in os.environ:
            del os.environ['DJANGO_ENV']
    
    def test_custom_middleware_integration(self):
        """Test custom middleware integration."""
        
        class MiddlewareConfig(DjangoConfig):
            project_name: str = "Middleware Test"
            secret_key: str = "middleware-test-secret-key-that-is-definitely-long-enough-for-validation"
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            custom_middleware: list = [
                "tests.middleware.TestMiddleware",
                "tests.middleware.AnotherMiddleware",
            ]
        
        config = MiddlewareConfig()
        settings = config.get_all_settings()
        
        middleware = settings['MIDDLEWARE']
        
        # Should include both core Django middleware and custom
        assert "tests.middleware.TestMiddleware" in middleware
        assert "tests.middleware.AnotherMiddleware" in middleware
        
        # Should still have core Django middleware
        assert 'django.middleware.security.SecurityMiddleware' in middleware
        assert 'django.contrib.auth.middleware.AuthenticationMiddleware' in middleware
    
    def test_project_apps_integration(self):
        """Test project apps integration."""
        
        class AppsConfig(DjangoConfig):
            project_name: str = "Apps Test"
            secret_key: str = "apps-test-secret-key-that-is-definitely-long-enough-for-validation"
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            project_apps: list = [
                "myapp",
                "myapp.submodule",
                "another_app",
            ]
        
        config = AppsConfig()
        settings = config.get_all_settings()
        
        installed_apps = settings['INSTALLED_APPS']
        
        # Should include both Django core apps and project apps
        assert "myapp" in installed_apps
        assert "myapp.submodule" in installed_apps
        assert "another_app" in installed_apps
        
        # Should still have Django core apps
        assert 'django.contrib.admin' in installed_apps
        assert 'django.contrib.auth' in installed_apps
        assert 'django.contrib.contenttypes' in installed_apps
    
    def test_settings_validation(self):
        """Test that generated settings pass basic validation."""
        
        class ValidConfig(DjangoConfig):
            project_name: str = "Valid Test"
            secret_key: str = "valid-test-secret-key-that-is-definitely-long-enough-for-validation"
            debug: bool = False
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name="production.db",
                )
            }
        
        config = ValidConfig()
        settings = config.get_all_settings()
        
        # Basic validation checks
        assert len(settings['SECRET_KEY']) >= 50
        assert isinstance(settings['ALLOWED_HOSTS'], list)
        assert len(settings['ALLOWED_HOSTS']) > 0
        assert isinstance(settings['INSTALLED_APPS'], list)
        assert len(settings['INSTALLED_APPS']) > 0
        assert isinstance(settings['MIDDLEWARE'], list)
        assert len(settings['MIDDLEWARE']) > 0
        assert isinstance(settings['DATABASES'], dict)
        assert 'default' in settings['DATABASES']
        
        # No None values in critical settings
        critical_settings = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS', 'DATABASES']
        for setting in critical_settings:
            assert settings[setting] is not None, f"Critical setting {setting} is None"