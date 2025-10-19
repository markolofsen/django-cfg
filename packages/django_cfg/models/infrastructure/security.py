"""
Security Configuration Model

Django security settings with Pydantic 2.
"""

from typing import Any, Dict, List

from pydantic import Field, field_validator

from ..base import BaseConfig


class SecurityConfig(BaseConfig):
    """
    🔒 Security Configuration - Django security settings
    
    Handles CORS, CSRF, SSL, sessions, and other security configurations
    with environment-aware defaults.
    """

    # CORS settings
    cors_enabled: bool = Field(default=True, description="Enable CORS support")
    cors_allow_all_origins: bool = Field(default=False, description="Allow all origins (dev only)")
    cors_allowed_origins: List[str] = Field(default_factory=list, description="Allowed CORS origins")
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_allow_headers: List[str] = Field(
        default_factory=lambda: [
            "accept",
            "accept-encoding",
            "authorization",
            "content-type",
            "dnt",
            "origin",
            "user-agent",
            "x-csrftoken",
            "x-requested-with",
        ],
        description="CORS allowed headers with common defaults for API usage",
    )

    # CSRF settings
    csrf_enabled: bool = Field(default=True, description="Enable CSRF protection")
    csrf_trusted_origins: List[str] = Field(default_factory=list, description="CSRF trusted origins")
    csrf_cookie_secure: bool = Field(default=False, description="Secure CSRF cookies")

    # SSL/HTTPS settings
    ssl_redirect: bool = Field(default=False, description="Redirect HTTP to HTTPS")
    hsts_enabled: bool = Field(default=False, description="Enable HTTP Strict Transport Security")
    hsts_max_age: int = Field(default=31536000, description="HSTS max age in seconds")

    # Session settings
    session_cookie_secure: bool = Field(default=False, description="Secure session cookies")
    session_cookie_age: int = Field(default=86400, description="Session cookie age in seconds")

    # Production domains for auto-configuration (deprecated - use DjangoConfig.security_domains instead)
    production_domains: List[str] = Field(
        default_factory=list,
        description="DEPRECATED: Use DjangoConfig.security_domains instead. Will be removed in future versions."
    )

    @field_validator('hsts_max_age')
    @classmethod
    def validate_hsts_max_age(cls, v: int) -> int:
        """Validate HSTS max age."""
        if v < 0:
            raise ValueError("HSTS max age must be non-negative")
        return v

    def configure_for_production(self, domains: List[str] = None) -> None:
        """
        Configure security settings for production.

        Args:
            domains: Optional list of production domains. If not provided, uses production_domains field.
        """
        prod_domains = domains or self.production_domains

        self.cors_allow_all_origins = False
        self.cors_allowed_origins = prod_domains
        self.csrf_cookie_secure = True
        self.csrf_trusted_origins = prod_domains
        self.ssl_redirect = True
        self.hsts_enabled = True
        self.session_cookie_secure = True

    def configure_for_development(self) -> None:
        """
        Configure security settings for development.
        
        In development:
        - CORS allows all origins for convenience
        - CSRF requires explicit trusted origins (CORS setting doesn't affect CSRF)
        - Adds common dev ports + existing csrf_trusted_origins
        """
        self.cors_allow_all_origins = True
        self.cors_allowed_origins = []
        self.csrf_cookie_secure = False

        # Common development origins for CSRF
        # Note: CORS_ALLOW_ALL_ORIGINS doesn't affect CSRF - it needs explicit origins

        # function smart diapason for dev ports
        def smart_diapason(start: int, end: int) -> List[str]:
            """Generate localhost origins for port range."""
            origins = []
            for i in range(start, end):
                origins.append(f'http://localhost:{i}')
                origins.append(f'http://127.0.0.1:{i}')
            return origins

        # Wide coverage of common dev ports
        # 3000-5000: Frontend frameworks (React, Vue, Next.js, etc)
        # 8000-9000: Backend frameworks (Django, Flask, FastAPI, etc)
        dev_local_origins = smart_diapason(3000, 5000) + smart_diapason(8000, 9000)

        # Combine dev defaults with existing trusted origins (from security_domains)
        # Remove duplicates while preserving order
        combined = dev_local_origins + self.csrf_trusted_origins

        # unique and sorted
        combined_unique = list(dict.fromkeys(combined))
        combined_unique.sort()

        self.csrf_trusted_origins = combined_unique

        self.ssl_redirect = False
        self.hsts_enabled = False
        self.session_cookie_secure = False

    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django security settings."""
        settings = {}

        # CORS settings
        if self.cors_enabled:
            settings.update({
                'CORS_ALLOW_ALL_ORIGINS': self.cors_allow_all_origins,
                'CORS_ALLOWED_ORIGINS': self.cors_allowed_origins,
                'CORS_ALLOW_CREDENTIALS': self.cors_allow_credentials,
                'CORS_ALLOW_HEADERS': self.cors_allow_headers,
            })

            # Add corsheaders to middleware if not present
            # This will be handled by the main DjangoConfig

        # CSRF settings
        settings.update({
            'CSRF_TRUSTED_ORIGINS': self.csrf_trusted_origins,
            'CSRF_COOKIE_SECURE': self.csrf_cookie_secure,
        })

        # SSL/HTTPS settings
        if self.ssl_redirect:
            settings['SECURE_SSL_REDIRECT'] = True

        if self.hsts_enabled:
            settings.update({
                'SECURE_HSTS_SECONDS': self.hsts_max_age,
                'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
                'SECURE_HSTS_PRELOAD': True,
            })

        # Session settings
        settings.update({
            'SESSION_COOKIE_SECURE': self.session_cookie_secure,
            'SESSION_COOKIE_AGE': self.session_cookie_age,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
        })

        # Additional security headers
        settings.update({
            'SECURE_CONTENT_TYPE_NOSNIFF': True,
            'SECURE_BROWSER_XSS_FILTER': True,
            'X_FRAME_OPTIONS': 'DENY',
        })

        return settings
