"""
Extension Manifest Model

Internal model used by scanner/loader.
Users should use BaseExtensionSettings from configs/apps/base.py instead.
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ExtensionManifest(BaseModel):
    """
    Internal manifest model for scanner/loader.

    Users don't create this directly - it's generated from
    BaseExtensionSettings.to_manifest().
    """

    # Identification
    name: str = Field(..., description="Extension name")
    version: str = Field(default="1.0.0")
    description: str = Field(default="")
    author: str = Field(default="")

    # Type
    type: Literal["app", "module"] = Field(default="app")

    # Compatibility
    min_djangocfg_version: Optional[str] = Field(default=None)

    # Django integration
    django_app_label: Optional[str] = Field(default=None)

    # URL routing
    url_prefix: Optional[str] = Field(default=None)
    url_namespace: Optional[str] = Field(default=None)

    # Dependencies
    requires: List[str] = Field(default_factory=list)
    pip_requires: List[str] = Field(default_factory=list)

    # Features
    admin_enabled: bool = Field(default=True)
    has_migrations: bool = Field(default=True)

    # Hooks
    on_ready: Optional[str] = Field(default=None)

    def get_django_app_label(self) -> str:
        """Get the Django app label, defaulting to extension name."""
        return self.django_app_label or self.name

    def get_url_namespace(self) -> str:
        """Get the URL namespace, defaulting to extension name."""
        return self.url_namespace or self.name
