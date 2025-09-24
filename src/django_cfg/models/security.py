"""
Security Configuration Model

Django security settings with Pydantic 2.
"""

from typing import List, Dict, Any
from pydantic import Field, field_validator
from .base import BaseConfig


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
    
    # Production domains for auto-configuration
    production_domains: List[str] = Field(
        default_factory=lambda: [
            "https://carapis.com",
            "https://api2.carapis.com",
            "https://djangocfg.com",
        ],
        description="Production domains for security configuration"
    )
    
    @field_validator('hsts_max_age')
    @classmethod
    def validate_hsts_max_age(cls, v: int) -> int:
        """Validate HSTS max age."""
        if v < 0:
            raise ValueError("HSTS max age must be non-negative")
        return v
    
    def configure_for_production(self) -> None:
        """Configure security settings for production."""
        self.cors_allow_all_origins = False
        self.cors_allowed_origins = self.production_domains
        self.csrf_cookie_secure = True
        self.csrf_trusted_origins = self.production_domains
        self.ssl_redirect = True
        self.hsts_enabled = True
        self.session_cookie_secure = True
    
    def configure_for_development(self) -> None:
        """Configure security settings for development."""
        self.cors_allow_all_origins = True
        self.cors_allowed_origins = []
        self.csrf_cookie_secure = False
        self.csrf_trusted_origins = []
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
            })
            
            # Add corsheaders to middleware if not present
            # This will be handled by the main ConfigToolkit
        
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
