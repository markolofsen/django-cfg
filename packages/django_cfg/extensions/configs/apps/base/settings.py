"""
Base extension settings class.
"""

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, computed_field

from django_cfg.extensions.manifest import ExtensionManifest

from .constants import APP_LABEL_PREFIX
from .navigation import NavigationSection
from .schedule import ExtensionScheduleConfig


class BaseExtensionSettings(BaseModel):
    """
    Base settings class for all extension apps.

    Contains both manifest fields and runtime settings.
    Subclasses define defaults, users can override in __cfg__.py.

    Example:
        class BaseLeadsSettings(BaseExtensionSettings):
            name: str = "leads"
            telegram_enabled: bool = True
            ...
    """

    # === Manifest fields ===
    name: str = Field(..., description="Extension name (required)")
    version: str = Field(default="1.0.0", description="Extension version")
    description: str = Field(default="", description="Extension description")
    author: str = Field(default="", description="Extension author")
    type: Literal["app", "module"] = Field(default="app", description="Extension type")

    # Compatibility
    min_djangocfg_version: Optional[str] = Field(default=None, description="Minimum django-cfg version")

    # Django integration (simple label without prefix)
    django_app_label: Optional[str] = Field(default=None, description="Django app label (without prefix)")

    # URL routing
    url_prefix: Optional[str] = Field(default=None, description="URL prefix for extension")
    url_namespace: Optional[str] = Field(default=None, description="URL namespace")

    @computed_field
    @property
    def full_app_label(self) -> str:
        """
        Full app label with prefix.

        User specifies: django_app_label = "support"
        Result: cfg_support

        Used for:
        - apps.py label
        - models Meta.app_label
        - migrations
        - admin URLs
        """
        label = self.django_app_label or self.name
        if label.startswith(APP_LABEL_PREFIX):
            return label
        return f"{APP_LABEL_PREFIX}{label}"

    def admin_url(self, model: str) -> str:
        """
        Generate admin URL for a model in this extension.

        Args:
            model: Model name in lowercase (e.g., "payment", "ticket")

        Returns:
            Admin changelist URL (e.g., "/admin/cfg_payments/payment/")
        """
        return f"/admin/{self.full_app_label}/{model}/"

    # Features
    admin_enabled: bool = Field(default=True, description="Enable admin interface")
    has_migrations: bool = Field(default=True, description="Extension has migrations")

    # Dependencies
    requires: list[str] = Field(default_factory=list, description="Required extensions")
    pip_requires: list[str] = Field(default_factory=list, description="Required pip packages")

    # Admin Navigation
    navigation: Optional[NavigationSection] = Field(
        default=None,
        description="Admin navigation section configuration"
    )

    # Constance Dynamic Settings
    constance_fields: list[Any] = Field(
        default_factory=list,
        description="Constance fields for this extension (list[ConstanceField])"
    )

    # RQ Scheduled Tasks
    schedules: list[Any] = Field(
        default_factory=list,
        description="RQ scheduled tasks (list[ExtensionScheduleConfig] or list[RQScheduleConfig])"
    )

    # Middleware Classes
    middleware_classes: list[str] = Field(
        default_factory=list,
        description="Middleware classes to add to MIDDLEWARE (full paths)"
    )

    class Config:
        """Pydantic config."""
        extra = "forbid"

    def to_manifest(self) -> ExtensionManifest:
        """Convert settings to ExtensionManifest."""
        return ExtensionManifest(
            name=self.name,
            version=self.version,
            description=self.description,
            author=self.author,
            type=self.type,
            min_djangocfg_version=self.min_djangocfg_version,
            django_app_label=self.django_app_label,
            url_prefix=self.url_prefix,
            url_namespace=self.url_namespace,
            admin_enabled=self.admin_enabled,
            has_migrations=self.has_migrations,
            requires=self.requires,
            pip_requires=self.pip_requires,
        )

    def get_rq_schedules(self) -> list[Any]:
        """
        Get RQ scheduled tasks for this extension.

        Converts ExtensionScheduleConfig to RQScheduleConfig.
        Override this method to dynamically generate schedules.

        Returns:
            List of RQScheduleConfig instances

        Example (declarative):
            ```python
            class MyExtSettings(BaseExtensionSettings):
                name = "myext"
                schedules = [
                    ExtensionScheduleConfig(
                        task="cleanup",  # -> extensions.apps.myext.tasks.cleanup
                        cron="0 3 * * *",
                    ),
                ]
            ```

        Example (dynamic):
            ```python
            class MyExtSettings(BaseExtensionSettings):
                cleanup_enabled: bool = True

                def get_rq_schedules(self):
                    schedules = super().get_rq_schedules()
                    if self.cleanup_enabled:
                        from django_cfg.models.django.django_rq import RQScheduleConfig
                        schedules.append(RQScheduleConfig(...))
                    return schedules
            ```
        """
        result: list[Any] = []

        for schedule in self.schedules:
            if isinstance(schedule, ExtensionScheduleConfig):
                # Convert to RQScheduleConfig
                result.append(schedule.to_rq_schedule(self.name))
            else:
                # Already RQScheduleConfig or compatible
                result.append(schedule)

        return result

    def get_middleware_classes(self) -> list[str]:
        """
        Get middleware classes for this extension.

        Override this method to dynamically generate middleware.

        Returns:
            List of middleware class paths

        Example (declarative):
            ```python
            class MyExtSettings(BaseExtensionSettings):
                name = "myext"
                middleware_classes = [
                    "extensions.apps.myext.middleware.MyMiddleware",
                ]
            ```

        Example (dynamic):
            ```python
            class PaymentsSettings(BasePaymentsSettings):
                def get_middleware_classes(self):
                    middleware = super().get_middleware_classes()
                    if self.enabled:
                        middleware.append("extensions.apps.payments.middleware.PaymentMiddleware")
                    return middleware
            ```
        """
        return list(self.middleware_classes)
