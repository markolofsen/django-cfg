"""
Environment Configuration Model

Core Django environment settings with Pydantic 2.
"""

import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic import Field, field_validator, computed_field
from .base import BaseConfig


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
                    f"Please change the secret key from default/example value"
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
        """Static files directory."""
        return self.base_dir / "static"

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

    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django settings with smart defaults."""
        return {
            # Core Django settings
            "DEBUG": self.debug,
            "SECRET_KEY": self.secret_key,
            "ALLOWED_HOSTS": self.allowed_hosts,
            # Paths
            "BASE_DIR": self.base_dir,
            # URL and WSGI/ASGI configuration
            "ROOT_URLCONF": "api.urls",
            "WSGI_APPLICATION": "api.wsgi.application",
            "ASGI_APPLICATION": "api.asgi.application",
            # Static files configuration
            "STATIC_URL": "/static/",
            "STATIC_ROOT": self.static_dir,
            "STATICFILES_STORAGE": "whitenoise.storage.CompressedManifestStaticFilesStorage",
            "WHITENOISE_USE_FINDERS": True,
            "WHITENOISE_AUTOREFRESH": self.debug,
            "WHITENOISE_MAX_AGE": 31536000,  # 1 year
            # Media files configuration
            "MEDIA_URL": "/media/",
            "MEDIA_ROOT": self.media_dir,
            # Basic Django apps (can be extended by other configs)
            "INSTALLED_APPS": [
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
                "django.contrib.staticfiles",
                "django.contrib.humanize",
                "django.contrib.sites",
                "django.contrib.sitemaps",
            ],
            # User model
            "AUTH_USER_MODEL": self.auth_user_model,
            # Basic middleware (can be extended by other configs)
            "MIDDLEWARE": [
                "django.middleware.security.SecurityMiddleware",
                "whitenoise.middleware.WhiteNoiseMiddleware",
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
            ],
            # Templates configuration
            "TEMPLATES": [
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [self.templates_dir],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.debug",
                            "django.template.context_processors.request",
                            "django.contrib.auth.context_processors.auth",
                            "django.contrib.messages.context_processors.messages",
                        ],
                    },
                },
            ],
            # Auth configuration
            "AUTH_PASSWORD_VALIDATORS": (
                []
                if self.debug
                else [
                    {
                        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
                    },
                    {
                        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
                        "OPTIONS": {"min_length": 8},
                    },
                    {
                        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
                    },
                    {
                        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
                    },
                ]
            ),
            # Internationalization
            "LANGUAGE_CODE": "en-us",
            "TIME_ZONE": "UTC",
            "USE_I18N": True,
            "USE_L10N": True,
            "USE_TZ": True,
            # Miscellaneous
            "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
            "DATA_UPLOAD_MAX_NUMBER_FIELDS": 10000,
            "SITE_ID": 1,
        }
