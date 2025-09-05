"""
🧪 Test Configuration and Fixtures

Shared test configuration following KISS principles.
Provides base classes and fixtures for django-cfg tests.
"""

import pytest
from pathlib import Path
from django_cfg import DjangoConfig


class BaseDjangoConfig(DjangoConfig):
    """
    Base configuration class for tests.
    
    Disables automatic path resolution to avoid Django project detection
    issues when running tests in the django-cfg package directory.
    """
    
    def _resolve_paths(self) -> None:
        """Override to disable automatic path resolution in tests."""
        # Set minimal required paths for tests
        if self._base_dir is None:
            self._base_dir = Path(__file__).parent.parent
        
        # Set default values if not provided
        if not self.root_urlconf:
            self.root_urlconf = "tests.urls"
        
        if not self.wsgi_application:
            self.wsgi_application = "tests.wsgi.application"


@pytest.fixture
def temp_dir(tmp_path):
    """Provide a temporary directory for tests."""
    return tmp_path


@pytest.fixture
def sample_config():
    """Provide a basic test configuration."""
    class SampleTestConfig(BaseDjangoConfig):
        project_name: str = "Test Project"
        secret_key: str = "test-secret-key-that-is-definitely-long-enough-for-validation"
        security_domains: list = ["https://example.com", "http://localhost:8000"]
        
        databases: dict = {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            }
        }
    
    return SampleTestConfig()


# Pytest markers for test categorization
pytest_plugins = []

def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, with Django)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests (can be skipped with -m 'not slow')"
    )
    config.addinivalue_line(
        "markers", "django_db: Tests requiring database access"
    )
