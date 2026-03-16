"""
Environment Configuration Model

Core Django environment settings with Pydantic 2.
"""

import os
from pathlib import Path
from typing import List

from pydantic import Field, computed_field, field_validator

from ..base import BaseConfig


class EnvironmentConfig(BaseConfig):
    """
    🌍 Environment Configuration - Core Django Settings

    Handles all core Django environment settings with smart defaults
    and automatic environment detection.
    """

    # Core Django settings
    debug: bool = Field(
        default=False, description="Enable Django debug mode (True for development)"
    )

    secret_key: str = Field(
        min_length=50,
        description="Django secret key (minimum 50 characters for security)",
    )

    allowed_hosts: List[str] = Field(
        default_factory=list, description="List of allowed hosts for Django"
    )

    # Environment detection
    environment: str = Field(
        default="development",
        description="Environment name (development/production/staging/testing)",
    )

    # Path settings
    base_dir: Path = Field(
        default_factory=lambda: Path.cwd(), description="Application base directory"
    )

    # Django User Model
    auth_user_model: str = Field(
        default="django.contrib.auth.models.User",
        description="Django user model to use (e.g., 'accounts.CustomUser')",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is secure."""
        if len(v) < 50:
            raise ValueError(
                "Secret key must be at least 50 characters long for security"
            )

        # Check for common insecure values
        insecure_keys = [
            "change-me",
            "your-secret-key-here",
            "dev-secret-key",
            "django-insecure-",
            "your-secret-key-change-this",
        ]

        for insecure in insecure_keys:
            if insecure in v.lower():
                raise ValueError(
                    "Please change the secret key from default/example value"
                )

        return v

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def set_default_allowed_hosts(cls, v, info):
        """Set smart default allowed hosts based on debug mode."""
        if not v:  # If empty list or None
            # Try to get debug from field being validated
            debug = info.data.get("debug", False)

            if debug:
                return ["localhost", "127.0.0.1", "0.0.0.0", "*"]
            else:
                return []
        return v

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment name."""
        allowed = ["development", "production", "testing", "staging"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of: {allowed}")
        return v

    # Computed properties for easy access
    @computed_field
    @property
    def is_production(self) -> bool:
        """True if running in production environment."""
        return self.environment == "production" or not self.debug

    @computed_field
    @property
    def is_development(self) -> bool:
        """True if running in development environment."""
        return self.environment == "development" or self.debug

    @computed_field
    @property
    def is_testing(self) -> bool:
        """True if running in testing environment."""
        return self.environment == "testing"

    @computed_field
    @property
    def is_staging(self) -> bool:
        """True if running in staging environment."""
        return self.environment == "staging"

    @computed_field
    @property
    def is_docker(self) -> bool:
        """True if running in Docker container."""
        return os.path.exists("/.dockerenv")

    # Computed paths
    @computed_field
    @property
    def static_dir(self) -> Path:
        """Collected static files directory (STATIC_ROOT = BASE_DIR/staticfiles)."""
        return self.base_dir / "staticfiles"

    @computed_field
    @property
    def media_dir(self) -> Path:
        """Media files directory."""
        return self.base_dir / "media"

    @computed_field
    @property
    def templates_dir(self) -> Path:
        """Templates directory."""
        return self.base_dir / "templates"

    @computed_field
    @property
    def logs_dir(self) -> Path:
        """Logs directory."""
        return self.base_dir / "logs"

    def _validate_production(self) -> bool:
        """Validate production-specific requirements."""
        errors = []

        # Check secret key security
        if len(self.secret_key) < 50:
            errors.append("Secret key must be at least 50 characters in production")

        # Check debug is disabled
        if self.debug:
            errors.append("Debug mode must be disabled in production")

        # Check allowed hosts
        if "*" in self.allowed_hosts:
            errors.append("Wildcard '*' in ALLOWED_HOSTS is not secure for production")

        if errors:
            print("❌ Production validation errors:")
            for error in errors:
                print(f"   - {error}")
            return False

        return True

