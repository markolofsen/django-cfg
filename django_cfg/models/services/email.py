"""
Email Configuration Model

Django email settings with Pydantic 2.
"""

import django
from typing import Any, Dict, Optional

from pydantic import Field, field_validator, model_validator

from ...core.utils.display_name import normalize_display_name
from ..base import BaseConfig



# Django 6.1 added MAILERS and deprecated the EMAIL_* connection settings.
# Lives here (models layer) so core can import it without a layer inversion.
HAS_MAILERS = django.VERSION >= (6, 1)

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
    default_from: Optional[str] = Field(
        default=None,
        description=(
            "Default 'from' email address. Required in production with a "
            "sending backend (smtp/gateway)."
        ),
    )

    default_from_name: Optional[str] = Field(
        default=None,
        description=(
            "Display name shown in the recipient's inbox. Defaults to the "
            "project name. Set it to a person ('Mark from Acme') for letters "
            "written in the first person — the name is what a reader sees "
            "before deciding to open, and 'noreply' argues against replying."
        ),
    )

    reply_to: Optional[str] = Field(
        default=None,
        description=(
            "Address that receives replies, when it differs from 'from'. "
            "Needed when mail is sent from an unattended sender but the content "
            "invites a response: without it, a reply is silently discarded."
        ),
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

    @field_validator('default_from_name')
    @classmethod
    def validate_from_name(cls, v: Optional[str]) -> Optional[str]:
        """Same rules as the project name: it becomes the `From` display name."""
        return normalize_display_name(v) if v else v

    @field_validator('default_from', 'reply_to')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        """Validate email address format.

        ``reply_to`` is checked too: a typo there does not fail a send, it just
        routes every reply into nowhere, which is invisible until someone
        complains that nobody answered them.
        """
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

    def backend_path(self) -> str:
        """Dotted path of the Django email backend class for ``backend``."""
        if self.backend == 'smtp':
            if self.ssl_verify:
                return 'django.core.mail.backends.smtp.EmailBackend'
            # Accepts self-signed certificates (development only).
            return 'django_cfg.core.backends.smtp.UnverifiedSSLEmailBackend'
        paths = {
            'console': 'django.core.mail.backends.console.EmailBackend',
            'file': 'django.core.mail.backends.filebased.EmailBackend',
            'memory': 'django.core.mail.backends.locmem.EmailBackend',
            'dummy': 'django.core.mail.backends.dummy.EmailBackend',
            'gateway': 'django_cfg.core.backends.gateway.GatewayEmailBackend',
        }
        try:
            return paths[self.backend]
        except KeyError:
            raise ValueError(f"Unsupported email backend: {self.backend}") from None

    def backend_options(self) -> Dict[str, Any]:
        """Constructor options for the backend, as Django 6.1 ``MAILERS`` OPTIONS.

        Names follow Django's mapping of the deprecated settings
        (``EMAIL_HOST`` -> ``host``, ``EMAIL_HOST_USER`` -> ``username``, ...).
        """
        if self.backend == 'smtp':
            options: Dict[str, Any] = {
                'host': self.host,
                'port': self.port,
                'use_tls': self.use_tls,
                'use_ssl': self.use_ssl,
                'timeout': self.timeout,
            }
            if self.username:
                options['username'] = self.username
            if self.password:
                options['password'] = self.password
            return options
        if self.backend == 'file':
            return {'file_path': self.file_path}
        if self.backend == 'gateway':
            return {
                'gateway_url': self.gateway_url,
                'gateway_secret': self.gateway_secret,
                'timeout': self.timeout,
            }
        return {}

    def to_mailer(self) -> Dict[str, Any]:
        """One ``MAILERS`` entry: ``{"BACKEND": ..., "OPTIONS": {...}}``.

        Public so a project can compose its own ``MAILERS`` (a second alias, a
        backend that wraps this one) from the same ``EmailConfig``.
        """
        mailer: Dict[str, Any] = {'BACKEND': self.backend_path()}
        options = self.backend_options()
        if options:
            mailer['OPTIONS'] = options
        return mailer

    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django email settings.

        Django 6.1+ gets ``MAILERS`` (the ``EMAIL_*`` connection settings are
        deprecated there and removed in Django 2028; Django refuses both at
        once). Django 5.2 has no ``MAILERS`` and gets ``EMAIL_*``.
        """
        if HAS_MAILERS:
            settings: Dict[str, Any] = {'MAILERS': {'default': self.to_mailer()}}
        else:
            settings = self._legacy_email_settings()

        if self.default_from:
            settings['DEFAULT_FROM_EMAIL'] = self.default_from

        if self.subscribe_url:
            settings['EMAIL_SUBSCRIBE_URL'] = self.subscribe_url

        return settings

    def _legacy_email_settings(self) -> Dict[str, Any]:
        """``EMAIL_*`` settings for Django 5.2, which has no ``MAILERS``."""
        settings: Dict[str, Any] = {'EMAIL_BACKEND': self.backend_path()}

        if self.backend == 'smtp':
            settings.update({
                'EMAIL_HOST': self.host,
                'EMAIL_PORT': self.port,
                'EMAIL_USE_TLS': self.use_tls,
                'EMAIL_USE_SSL': self.use_ssl,
                'EMAIL_TIMEOUT': self.timeout,
            })
            if self.username:
                settings['EMAIL_HOST_USER'] = self.username
            if self.password:
                settings['EMAIL_HOST_PASSWORD'] = self.password

        elif self.backend == 'file':
            settings['EMAIL_FILE_PATH'] = self.file_path

        elif self.backend == 'gateway':
            settings.update({
                'EMAIL_GATEWAY_URL': self.gateway_url,
                'EMAIL_GATEWAY_SECRET': self.gateway_secret,
                'EMAIL_TIMEOUT': self.timeout,
            })

        return settings
