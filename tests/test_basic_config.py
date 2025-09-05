"""
Basic unit tests for django_cfg functionality.

Following TESTING_STANDARDS.md:
- Test individual components in isolation
- Verify configuration creation and validation
- Test error handling and edge cases
- Performance and memory usage tests
"""

import pytest
import os
import tempfile
import pydantic
from pathlib import Path
from typing import Dict, Any

from django_cfg import DjangoConfig, DatabaseConnection, CacheBackend
from django_cfg.exceptions import ConfigurationError, ValidationError
from .conftest import BaseDjangoConfig


class TestBasicConfiguration:
    """Test basic django_cfg configuration functionality."""
    
    def test_minimal_config_creation(self):
        """Test creating minimal configuration."""
        
        class MinimalConfig(BaseDjangoConfig):
            project_name: str = "Test Project"
            secret_key: str = "test-secret-key-that-is-definitely-long-enough-for-validation-requirements"
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
        
        config = MinimalConfig()
        
        # Verify basic properties
        assert config.project_name == "Test Project"
        assert len(config.secret_key) >= 50
        assert "default" in config.databases
        assert config.databases["default"].engine == "django.db.backends.sqlite3"
    
    def test_config_with_cache(self):
        """Test configuration with cache backend."""
        
        # Set production environment to avoid smart defaults limiting timeout
        import os
        old_env = os.environ.get('DJANGO_ENV')
        os.environ['DJANGO_ENV'] = 'production'
        
        try:
            class ConfigWithCache(BaseDjangoConfig):
                project_name: str = "Cache Test"
                secret_key: str = "cache-test-secret-key-that-is-definitely-long-enough-for-validation"
                
                databases: Dict[str, DatabaseConnection] = {
                    "default": DatabaseConnection(
                        engine="django.db.backends.sqlite3",
                        name=":memory:",
                    )
                }
                
                security_domains: list = ["example.com"]  # Required for production
                
                cache_default: CacheBackend = CacheBackend(
                    timeout=300,
                    max_connections=10,
                )
                
                cache_sessions: CacheBackend = CacheBackend(
                    timeout=3600,
                    max_connections=5,
                )
            
            config = ConfigWithCache()
            
            # Verify cache configuration
            assert config.cache_default is not None
            assert config.cache_default.timeout == 300
            assert config.cache_default.max_connections == 10
            
            assert config.cache_sessions is not None
            assert config.cache_sessions.timeout == 3600
            assert config.cache_sessions.max_connections == 5
        
        finally:
            # Restore original environment
            if old_env is not None:
                os.environ['DJANGO_ENV'] = old_env
            elif 'DJANGO_ENV' in os.environ:
                del os.environ['DJANGO_ENV']
    
    def test_django_settings_generation(self):
        """Test Django settings generation."""
        
        class SettingsTestConfig(BaseDjangoConfig):
            project_name: str = "Settings Test"
            secret_key: str = "settings-test-secret-key-that-is-definitely-long-enough-for-validation"
            debug: bool = True
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            project_apps: list = ["myapp", "anotherapp"]
        
        config = SettingsTestConfig()
        settings = config.get_all_settings()
        
        # Verify critical Django settings
        assert "SECRET_KEY" in settings
        assert "DEBUG" in settings
        assert "DATABASES" in settings
        assert "INSTALLED_APPS" in settings
        assert "MIDDLEWARE" in settings
        
        # Verify values
        assert settings["SECRET_KEY"] == config.secret_key
        assert settings["DEBUG"] is True
        
        # Verify database configuration
        assert "default" in settings["DATABASES"]
        assert settings["DATABASES"]["default"]["ENGINE"] == "django.db.backends.sqlite3"
        
        # Verify apps include both Django core and project apps
        installed_apps = settings["INSTALLED_APPS"]
        assert "django.contrib.admin" in installed_apps
        assert "django.contrib.auth" in installed_apps
        assert "myapp" in installed_apps
        assert "anotherapp" in installed_apps
        
        # Verify middleware includes WhiteNoise
        middleware = settings["MIDDLEWARE"]
        assert "whitenoise.middleware.WhiteNoiseMiddleware" in middleware
        assert "django.middleware.security.SecurityMiddleware" in middleware
    
    def test_validation_errors(self):
        """Test configuration validation errors."""
        
        # Test missing secret key
        with pytest.raises((ValidationError, ConfigurationError, pydantic.ValidationError)):
            class NoSecretConfig(BaseDjangoConfig):
                project_name: str = "No Secret"
                # secret_key missing
                
                databases: Dict[str, DatabaseConnection] = {
                    "default": DatabaseConnection(
                        engine="django.db.backends.sqlite3",
                        name=":memory:",
                    )
                }
            
            NoSecretConfig()
        
        # Test short secret key
        with pytest.raises((ValidationError, ConfigurationError, pydantic.ValidationError)):
            class ShortSecretConfig(BaseDjangoConfig):
                project_name: str = "Short Secret"
                secret_key: str = "short"  # Too short
                
                databases: Dict[str, DatabaseConnection] = {
                    "default": DatabaseConnection(
                        engine="django.db.backends.sqlite3",
                        name=":memory:",
                    )
                }
            
            ShortSecretConfig()
        
        # Test missing default database
        with pytest.raises((ValidationError, ConfigurationError, pydantic.ValidationError)):
            class NoDefaultDBConfig(BaseDjangoConfig):
                project_name: str = "No Default DB"
                secret_key: str = "no-default-db-secret-key-that-is-definitely-long-enough-for-validation"
                
                databases: Dict[str, DatabaseConnection] = {
                    "secondary": DatabaseConnection(
                        engine="django.db.backends.sqlite3",
                        name=":memory:",
                    )
                }
            
            NoDefaultDBConfig()
    
    def test_environment_detection(self):
        """Test environment detection."""
        
        class EnvTestConfig(BaseDjangoConfig):
            project_name: str = "Env Test"
            secret_key: str = "env-test-secret-key-that-is-definitely-long-enough-for-validation"
            security_domains: list = ["https://example.com", "http://localhost:8000"]
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
        
        # Test development environment
        os.environ['DJANGO_ENV'] = 'development'
        config = EnvTestConfig()
        assert config._environment == 'development'
        
        # Test production environment
        os.environ['DJANGO_ENV'] = 'production'
        config = EnvTestConfig()
        assert config._environment == 'production'
        
        # Clean up
        if 'DJANGO_ENV' in os.environ:
            del os.environ['DJANGO_ENV']
    
    def test_installed_apps_generation(self):
        """Test INSTALLED_APPS generation."""
        
        class AppsTestConfig(BaseDjangoConfig):
            project_name: str = "Apps Test"
            secret_key: str = "apps-test-secret-key-that-is-definitely-long-enough-for-validation"
            security_domains: list = ["https://example.com", "http://localhost:8000"]
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            project_apps: list = ["app1", "app2.submodule", "app3"]
        
        config = AppsTestConfig()
        apps = config.get_installed_apps()
        
        # Should include Django core apps
        core_apps = [
            "django.contrib.admin",
            "django.contrib.auth", 
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
        ]
        
        for app in core_apps:
            assert app in apps, f"Missing core app: {app}"
        
        # Should include project apps
        for app in ["app1", "app2.submodule", "app3"]:
            assert app in apps, f"Missing project app: {app}"
    
    def test_middleware_generation(self):
        """Test middleware generation."""
        
        class MiddlewareTestConfig(BaseDjangoConfig):
            project_name: str = "Middleware Test"
            secret_key: str = "middleware-test-secret-key-that-is-definitely-long-enough-for-validation"
            security_domains: list = ["https://example.com", "http://localhost:8000"]
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
            
            custom_middleware: list = ["myapp.middleware.CustomMiddleware"]
        
        config = MiddlewareTestConfig()
        middleware = config.get_middleware()
        
        # Should include Django core middleware
        core_middleware = [
            "django.middleware.security.SecurityMiddleware",
            "whitenoise.middleware.WhiteNoiseMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ]
        
        for mw in core_middleware:
            assert mw in middleware, f"Missing core middleware: {mw}"
        
        # Should include custom middleware
        assert "myapp.middleware.CustomMiddleware" in middleware
    
    def test_cache_invalidation(self):
        """Test cache invalidation mechanism."""
        
        class CacheTestConfig(BaseDjangoConfig):
            project_name: str = "Cache Test"
            secret_key: str = "cache-test-secret-key-that-is-definitely-long-enough-for-validation"
            security_domains: list = ["https://example.com", "http://localhost:8000"]
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
        
        config = CacheTestConfig()
        
        # Generate settings (should cache them)
        settings1 = config.get_all_settings()
        settings2 = config.get_all_settings()
        
        # Should be the same object (cached)
        assert settings1 is settings2
        
        # Invalidate cache
        config.invalidate_cache()
        
        # Should generate new settings
        settings3 = config.get_all_settings()
        assert settings1 is not settings3
        
        # Content should be mostly the same (except for dynamic values like cache locations)
        assert settings1["SECRET_KEY"] == settings3["SECRET_KEY"]
        assert settings1["INSTALLED_APPS"] == settings3["INSTALLED_APPS"]
        assert settings1["DATABASES"] == settings3["DATABASES"]
    
    @pytest.mark.slow
    def test_performance_settings_generation(self):
        """Test performance of settings generation."""
        import time
        
        class PerfTestConfig(BaseDjangoConfig):
            project_name: str = "Performance Test"
            secret_key: str = "performance-test-secret-key-that-is-definitely-long-enough-for-validation"
            security_domains: list = ["https://example.com", "http://localhost:8000"]
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name="default.db",
                ),
                **{
                    f"db_{i}": DatabaseConnection(
                        engine="django.db.backends.sqlite3",
                        name=f"test_{i}.db",
                    )
                    for i in range(10)  # Multiple databases
                }
            }
            
            project_apps: list = [f"app_{i}" for i in range(20)]  # Many apps
        
        config = PerfTestConfig()
        
        # Measure first generation (cold)
        start_time = time.time()
        settings1 = config.get_all_settings()
        cold_time = (time.time() - start_time) * 1000
        
        # Measure second generation (cached)
        start_time = time.time()
        settings2 = config.get_all_settings()
        cached_time = (time.time() - start_time) * 1000
        
        # Performance assertions
        assert cold_time < 500, f"Cold generation took {cold_time:.2f}ms (target: <500ms)"
        assert cached_time < 10, f"Cached generation took {cached_time:.2f}ms (target: <10ms)"
        
        # Verify settings completeness
        assert len(settings1) > 15  # Should have many Django settings
        assert len(settings1["DATABASES"]) == 11  # All databases (default + 10 test dbs)
        assert len([app for app in settings1["INSTALLED_APPS"] if app.startswith("app_")]) == 20  # All project apps
    
    def test_model_dump_for_django(self):
        """Test model_dump_for_django method."""
        
        class DumpTestConfig(BaseDjangoConfig):
            project_name: str = "Dump Test"
            secret_key: str = "dump-test-secret-key-that-is-definitely-long-enough-for-validation"
            security_domains: list = ["https://example.com", "http://localhost:8000"]
            
            databases: Dict[str, DatabaseConnection] = {
                "default": DatabaseConnection(
                    engine="django.db.backends.sqlite3",
                    name=":memory:",
                )
            }
        
        config = DumpTestConfig()
        dump = config.model_dump_for_django()
        
        # Should be a dictionary
        assert isinstance(dump, dict)
        
        # Should contain serialized data suitable for Django
        assert "project_name" in dump
        assert "secret_key" in dump
        assert "databases" in dump
        
        # Database should be serialized properly
        assert isinstance(dump["databases"], dict)
        assert "default" in dump["databases"]