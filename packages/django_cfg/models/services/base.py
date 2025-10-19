"""
Base service configuration for django_cfg.

Generic service configuration for custom services.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator


class ServiceConfig(BaseModel):
    """
    Generic service configuration for custom services.

    This is a fallback for services that don't have specialized models.
    Prefer specific models like EmailConfig, TelegramConfig when available.
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "allow",  # Allow additional fields for flexibility
    }

    name: str = Field(
        ...,
        description="Service name",
        min_length=1,
        max_length=50,
    )

    enabled: bool = Field(
        default=True,
        description="Whether service is enabled",
    )

    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Service-specific configuration",
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate service name format."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError(
                "Service name must contain only alphanumeric characters, "
                "underscores, and hyphens"
            )

        return v

    def to_config_dict(self) -> Dict[str, Any]:
        """Convert to configuration dictionary."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            **self.config,
        }


__all__ = [
    "ServiceConfig",
]
