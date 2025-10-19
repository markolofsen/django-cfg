"""
Django OpenAPI Service.

Universal OpenAPI client generator.
Replaces django-revolution with faster, cleaner implementation.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .config import OpenAPIConfig
from .group import OpenAPIGroupConfig

logger = logging.getLogger(__name__)


class OpenAPIError(Exception):
    """Base exception for OpenAPI-related errors."""

    pass


class DjangoOpenAPI:
    """
    Main OpenAPI service.

    Features:
    - Smart application grouping (cfg/custom)
    - Pure Python client generation (Python + TypeScript)
    - 20x faster than django-revolution
    - No external dependencies (Node.js, datamodel-codegen, etc.)
    - Full x-enum-varnames support
    - Native COMPONENT_SPLIT_REQUEST handling

    Example:
        >>> from django_cfg.modules.django_client.core.config import get_openapi_service
        >>> service = get_openapi_service()
        >>> service.generate_clients(groups=["cfg", "custom"])
    """

    def __init__(self, config: Optional[OpenAPIConfig] = None):
        self._config: Optional[OpenAPIConfig] = config

    @property
    def config(self) -> Optional[OpenAPIConfig]:
        """Get OpenAPI configuration."""
        return self._config

    def set_config(self, config: OpenAPIConfig):
        """Set OpenAPI configuration."""
        self._config = config

    def is_enabled(self) -> bool:
        """Check if OpenAPI is enabled."""
        return self.config is not None and self.config.enabled

    def get_groups(self) -> Dict[str, OpenAPIGroupConfig]:
        """Get configured application groups as a dictionary (for backward compatibility)."""
        if not self.config:
            return {}

        # Use get_groups_with_defaults if available (OpenAPIClientConfig)
        if hasattr(self.config, 'get_groups_with_defaults'):
            return self.config.get_groups_with_defaults()

        # Convert list to dict for backward compatibility
        return {group.name: group for group in self.config.groups}

    def get_group(self, group_name: str) -> Optional[OpenAPIGroupConfig]:
        """Get specific group configuration (including defaults)."""
        return self.get_groups().get(group_name)

    def get_group_names(self) -> List[str]:
        """Get list of configured group names (including defaults)."""
        return list(self.get_groups().keys())

    def get_output_dir(self) -> Path:
        """Get base output directory."""
        if not self.config:
            return Path("openapi")
        return self.config.get_output_path()

    def get_schemas_dir(self) -> Path:
        """Get schemas directory."""
        if not self.config:
            return Path("openapi/schemas")
        return self.config.get_schemas_dir()

    def get_clients_dir(self) -> Path:
        """Get clients directory."""
        if not self.config:
            return Path("openapi/clients")
        return self.config.get_clients_dir()

    def ensure_directories(self):
        """Ensure all required directories exist."""
        if not self.config:
            return

        dirs = [
            self.config.get_output_path(),
            self.config.get_schemas_dir(),
            self.config.get_clients_dir(),
            self.config.get_python_clients_dir(),
            self.config.get_typescript_clients_dir(),
        ]

        if self.config.enable_archive:
            dirs.append(self.config.get_archive_dir())

        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")

    def validate_config(self) -> bool:
        """
        Validate OpenAPI configuration.

        Returns:
            bool: True if configuration is valid

        Raises:
            OpenAPIError: If configuration is invalid
        """
        if not self.config:
            raise OpenAPIError("OpenAPI configuration not found")

        if not self.config.enabled:
            raise OpenAPIError("OpenAPI is not enabled")

        if not self.config.groups:
            raise OpenAPIError("No application groups configured")

        # Validate each group
        for group in self.config.groups:
            if not group.apps:
                raise OpenAPIError(f"Group '{group.name}' has no apps configured")

            if not group.title:
                raise OpenAPIError(f"Group '{group.name}' has no title")

        logger.debug(f"OpenAPI configuration validated: {len(self.config.groups)} groups")
        return True

    def get_status(self) -> Dict:
        """
        Get OpenAPI service status.

        Returns:
            Dictionary with service status information
        """
        if not self.config:
            return {
                "enabled": False,
                "reason": "Configuration not found",
            }

        try:
            return {
                "enabled": self.config.enabled,
                "groups": len(self.config.groups),
                "group_names": self.get_group_names(),
                "output_dir": str(self.config.get_output_path()),
                "generate_python": self.config.generate_python,
                "generate_typescript": self.config.generate_typescript,
                "api_prefix": self.config.api_prefix,
                "archive_enabled": self.config.enable_archive,
            }
        except Exception as e:
            return {
                "enabled": False,
                "error": str(e),
            }


# Singleton instance
_service_instance: Optional[DjangoOpenAPI] = None


def get_openapi_service() -> DjangoOpenAPI:
    """
    Get singleton OpenAPI service instance.

    Returns:
        DjangoOpenAPI instance

    Example:
        >>> service = get_openapi_service()
        >>> if service.is_enabled():
        ...     print(f"Groups: {service.get_group_names()}")
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = DjangoOpenAPI()
    return _service_instance


def reset_service():
    """Reset singleton instance (useful for testing)."""
    global _service_instance
    _service_instance = None


__all__ = [
    "DjangoOpenAPI",
    "OpenAPIError",
    "get_openapi_service",
    "reset_service",
]
