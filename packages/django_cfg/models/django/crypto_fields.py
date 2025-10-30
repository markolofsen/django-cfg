"""
Django Crypto Fields configuration model.

Field-level encryption settings for sensitive data with smart defaults.
"""

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


class CryptoFieldsConfig(BaseModel):
    """
    Django Crypto Fields encryption configuration.

    Provides type-safe configuration for django-crypto-fields with environment-aware defaults.

    Features:
    - Field-level encryption for sensitive data (API keys, tokens, passwords)
    - Automatic key management
    - Custom encryption key paths
    - Auto-create keys in development mode

    Example:
        ```python
        # Auto-configuration (recommended)
        crypto = CryptoFieldsConfig(enabled=True)

        # Custom configuration
        crypto = CryptoFieldsConfig(
            enabled=True,
            key_path="/var/secrets/crypto_keys",
            key_prefix="myproject",
            auto_create=False
        )
        ```
    """

    # === Basic Settings ===
    enabled: bool = Field(
        default=True,
        description="Enable/disable django-crypto-fields encryption"
    )

    key_path: Optional[str] = Field(
        default=None,
        description="Path to encryption keys directory (None = auto: BASE_DIR/crypto_keys)"
    )

    key_prefix: str = Field(
        default="",
        description="Prefix for encryption key files (e.g., 'myproject-')"
    )

    auto_create: Optional[bool] = Field(
        default=None,
        description="Auto-create encryption keys if missing (None = auto: True in DEBUG, False in production)"
    )

    # === Django Revision Settings (for django-audit-fields dependency) ===
    ignore_git_dir: bool = Field(
        default=True,
        description=(
            "Ignore git directory for django-revision. "
            "When True, version is discovered from: package metadata → pyproject.toml → VERSION file. "
            "Prevents 'not recommended' warning from settings.REVISION fallback."
        )
    )

    def to_django_settings(self, base_dir: Path, is_production: bool, debug: bool, project_version: str = "1.0.0") -> dict:
        """
        Convert to Django settings dictionary with environment-aware defaults.

        Args:
            base_dir: Django project BASE_DIR
            is_production: Whether running in production mode
            debug: Whether debug mode is enabled
            project_version: Project version to use for REVISION (default: "1.0.0")

        Returns:
            Dictionary of django-crypto-fields settings
        """
        is_dev = debug or not is_production

        # Determine keys directory path
        if self.key_path:
            crypto_keys_dir = Path(self.key_path)
        else:
            # Default to BASE_DIR/crypto_keys
            crypto_keys_dir = base_dir / "crypto_keys"

        # Ensure the crypto keys directory exists
        if not crypto_keys_dir.exists():
            try:
                crypto_keys_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                # Log warning but don't fail - django-crypto-fields will create it if AUTO_CREATE_KEYS=True
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Could not create crypto keys directory {crypto_keys_dir}: {e}")

        # Determine auto_create setting
        auto_create_keys = self.auto_create
        if auto_create_keys is None:
            # Auto-detect: enable in DEBUG mode
            auto_create_keys = is_dev

        settings = {
            "DJANGO_CRYPTO_FIELDS_KEY_PATH": str(crypto_keys_dir),
            "KEY_PREFIX": self.key_prefix,
            "AUTO_CREATE_KEYS": auto_create_keys,
        }

        # Fix django-revision (required by django-audit-fields dependency)
        # Disable all automatic version detection and use project version directly
        # This prevents "A distribution name is required" error when package metadata is not available
        settings.update({
            "REVISION": project_version,
            "APP_NAME": "",  # Empty to prevent package metadata lookup
            "DJANGO_REVISION_IGNORE_METADATA": True,  # Don't use importlib.metadata.version()
            "DJANGO_REVISION_IGNORE_TOML_FILE": True,  # Don't read pyproject.toml
            "DJANGO_REVISION_IGNORE_VERSION_FILE": True,  # Don't read VERSION file
            "DJANGO_REVISION_IGNORE_WORKING_DIR": True,  # Don't use git
        })

        return settings

    @property
    def is_configured(self) -> bool:
        """Check if crypto fields is properly configured."""
        return self.enabled


__all__ = ["CryptoFieldsConfig"]
