"""
Email Configuration Model

Django email settings with Pydantic 2.
"""

from typing import Any, Dict, Optional

from pydantic import Field, field_validator, model_validator

from ..base import BaseConfig


class EmailConfig(BaseConfig):
    """
    📧 Email Configuration - Django email settings

    Supports SMTP, console, file, and other email backends
    with environment-aware defaults.
    """

    # Email backend
    backend: str = Field(
        default="console",
        description="Email backend (smtp/console/file/memory/gateway)"
    )

    # SMTP settings
    host: str = Field(
        default="localhost",
        description="SMTP server host"
    )

    port: int = Field(
        default=587,
        ge=1,
        le=65535,
        description="SMTP server port"
    )

    username: Optional[str] = Field(
        default=None,
        description="SMTP username"
    )

    password: Optional[str] = Field(
        default=None,
        description="SMTP password"
    )

    use_tls: bool = Field(
        default=True,
        description="Use TLS for SMTP"
    )

    use_ssl: bool = Field(
        default=False,
        description="Use SSL for SMTP"
    )

    ssl_verify: bool = Field(
        default=True,
        description="Verify SSL certificates (set False for self-signed certs in dev)"
    )

    timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="SMTP timeout in seconds"
    )

    # Email addresses
    default_from: str = Field(
        default="noreply@example.com",
        description="Default 'from' email address"
    )

    # File backend settings
    file_path: str = Field(
        default="emails/",
        description="Path for file-based email backend"
    )

    # HTTP email-gateway settings (backend="gateway").
    # The gateway owns the provider integration (ESP choice, sender identity
    # pinning, rate limits); Django holds no provider credentials.
    gateway_url: Optional[str] = Field(
        default=None,
        description="Email gateway send endpoint (e.g. https://email-api.example.com/send)"
    )

    gateway_secret: Optional[str] = Field(
        default=None,
        repr=False,
        description="Shared secret presented to the gateway as a Bearer token"
    )

    # Optional one-click subscribe link rendered as a P.S. footer in system
    # emails (templates get it as `subscribe_url`). None/empty = no footer.
    subscribe_url: Optional[str] = Field(
        default=None,
        description="Newsletter subscribe URL for the system-email P.S. footer"
    )

    @field_validator('backend')
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate email backend."""
        valid_backends = ['smtp', 'console', 'file', 'memory', 'dummy', 'gateway']
        if v not in valid_backends:
            raise ValueError(f"Email backend must be one of: {valid_backends}")
        return v

    @model_validator(mode='after')
    def validate_gateway_credentials(self):
        """The gateway backend is unusable without both settings."""
        if self.backend == 'gateway' and not (
            self.gateway_url and self.gateway_secret
        ):
            raise ValueError(
                "backend='gateway' requires gateway_url and gateway_secret"
            )
        return self

    @field_validator('default_from')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email address format."""
        if v and '@' not in v:
            raise ValueError("Invalid email address format")
        return v

    @field_validator('use_tls', 'use_ssl', mode='after')
    @classmethod
    def validate_tls_ssl(cls, v, info):
        """Ensure TLS and SSL are not both enabled."""
        data = info.data
        if data.get('use_tls') and data.get('use_ssl'):
            raise ValueError("Cannot use both TLS and SSL simultaneously")
        return v

    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django email settings."""
        if self.backend == 'smtp':
            # Choose backend based on SSL verification setting
            if self.ssl_verify:
                backend_class = 'django.core.mail.backends.smtp.EmailBackend'
            else:
                # Use custom backend that accepts self-signed SSL certs
                backend_class = 'django_cfg.core.backends.smtp.UnverifiedSSLEmailBackend'

            settings = {
                'EMAIL_BACKEND': backend_class,
                'EMAIL_HOST': self.host,
                'EMAIL_PORT': self.port,
                'EMAIL_USE_TLS': self.use_tls,
                'EMAIL_USE_SSL': self.use_ssl,
                'EMAIL_TIMEOUT': self.timeout,
                'DEFAULT_FROM_EMAIL': self.default_from,
            }

            if self.username:
                settings['EMAIL_HOST_USER'] = self.username

            if self.password:
                settings['EMAIL_HOST_PASSWORD'] = self.password

        elif self.backend == 'console':
            settings = {
                'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
                'DEFAULT_FROM_EMAIL': self.default_from,
            }

        elif self.backend == 'file':
            settings = {
                'EMAIL_BACKEND': 'django.core.mail.backends.filebased.EmailBackend',
                'EMAIL_FILE_PATH': self.file_path,
                'DEFAULT_FROM_EMAIL': self.default_from,
            }

        elif self.backend == 'memory':
            settings = {
                'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
                'DEFAULT_FROM_EMAIL': self.default_from,
            }

        elif self.backend == 'dummy':
            settings = {
                'EMAIL_BACKEND': 'django.core.mail.backends.dummy.EmailBackend',
                'DEFAULT_FROM_EMAIL': self.default_from,
            }

        elif self.backend == 'gateway':
            settings = {
                'EMAIL_BACKEND': 'django_cfg.core.backends.gateway.GatewayEmailBackend',
                'EMAIL_GATEWAY_URL': self.gateway_url,
                'EMAIL_GATEWAY_SECRET': self.gateway_secret,
                'EMAIL_TIMEOUT': self.timeout,
                'DEFAULT_FROM_EMAIL': self.default_from,
            }

        else:
            raise ValueError(f"Unsupported email backend: {self.backend}")

        if self.subscribe_url:
            settings['EMAIL_SUBSCRIBE_URL'] = self.subscribe_url

        return settings
