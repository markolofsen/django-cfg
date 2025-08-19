"""
Django settings for testing django_cfg module.

This demonstrates how django_cfg should be used in a real project.
"""

from django_cfg import DjangoConfig, DatabaseConnection, CacheBackend

class TestDjangoConfig(DjangoConfig):
    """Test configuration using django_cfg."""
    
    project_name: str = "Django CFG Tests"
    project_version: str = "1.0.0"
    project_description: str = "Test suite for django_cfg module"
    
    secret_key: str = "django-test-secret-key-that-is-definitely-long-enough-for-testing-purposes-and-validation"
    debug: bool = True
    
    # Test database configuration
    @property
    def databases(self):
        return {
            "default": DatabaseConnection(
                engine="django.db.backends.sqlite3",
                name=":memory:",
            )
        }
    
    # Cache configuration for tests
    cache_default: CacheBackend = CacheBackend(
        backend_override="django.core.cache.backends.dummy.DummyCache",
        timeout=1,
    )
    
    # URL configuration
    root_urlconf: str = "tests.urls"
    
    # Project apps for testing
    project_apps: list = []
    
    # Disable integrations for testing
    unfold = None
    revolution = None

# Initialize configuration
config = TestDjangoConfig()

# Apply ALL Django settings from django_cfg
globals().update(config.get_all_settings())
