"""
Email Configuration Model

Django email settings with Pydantic 2.
"""

from typing import Dict, Any, Optional
from pydantic import Field, field_validator
from .base import BaseConfig


class EmailConfig(BaseConfig):
    """
    📧 Email Configuration - Django email settings
    
    Supports SMTP, console, file, and other email backends
    with environment-aware defaults.
    """
    
    # Email backend
    backend: str = Field(
        default="console",
        description="Email backend (smtp/console/file/memory)"
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
    
    admin_email: Optional[str] = Field(
        default=None,
        description="Admin email for error notifications"
    )
    
    # File backend settings
    file_path: str = Field(
        default="emails/",
        description="Path for file-based email backend"
    )
    
    @field_validator('backend')
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate email backend."""
        valid_backends = ['smtp', 'console', 'file', 'memory', 'dummy']
        if v not in valid_backends:
            raise ValueError(f"Email backend must be one of: {valid_backends}")
        return v
    
    @field_validator('default_from', 'admin_email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
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
            backend_class = 'django.core.mail.backends.smtp.EmailBackend'
            
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
        
        else:
            raise ValueError(f"Unsupported email backend: {self.backend}")
        
        # Add admin email if provided
        if self.admin_email:
            settings['ADMINS'] = [('Admin', self.admin_email)]
            settings['MANAGERS'] = [('Manager', self.admin_email)]
        
        return settings
