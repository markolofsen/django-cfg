"""
Geo configuration model.
"""

from typing import TYPE_CHECKING, List

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from django_cfg.models.django.django_rq import RQScheduleConfig


class GeoConfig(BaseModel):
    """
    Geo app configuration for geographic data (countries, states, cities).

    Uses PostgreSQL with Django ORM. Data from dr5hn dataset
    (250+ countries, 5000+ states, 150,000+ cities).

    Example:
        ```python
        from django_cfg import DjangoConfig, GeoConfig

        class MyConfig(DjangoConfig):
            geo = GeoConfig()
        ```
    """

    enabled: bool = Field(
        default=True,
        description="Enable geo app (auto-adds to INSTALLED_APPS)"
    )

    auto_populate: bool = Field(
        default=True,
        description="Auto-populate geo data on startup if empty"
    )

    update_interval: int = Field(
        default=86400 * 30,  # 30 days
        description="Data update interval in seconds (default: 30 days)"
    )

    auto_update_enabled: bool = Field(
        default=False,
        description="Enable automatic data updates via RQ scheduler"
    )

    use_postgis: bool = Field(
        default=False,
        description="Use PostGIS for spatial queries (requires PostGIS extension)"
    )

    def get_rq_schedules(self) -> List["RQScheduleConfig"]:
        """Get RQ schedules for geo data updates."""
        if not self.enabled or not self.auto_update_enabled:
            return []

        from django_cfg.models.django.django_rq import RQScheduleConfig

        return [
            RQScheduleConfig(
                func="django_cfg.apps.tools.geo.tasks.update_geo_data",
                interval=self.update_interval,
                queue="default",
                description=f"Update geo data (every {self.update_interval}s)",
            )
        ]


__all__ = ["GeoConfig"]
