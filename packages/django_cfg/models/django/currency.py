"""
Currency configuration model.
"""

from typing import TYPE_CHECKING, List

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from django_cfg.models.django.django_rq import RQScheduleConfig


class CurrencyConfig(BaseModel):
    """
    Currency app configuration.

    Example:
        ```python
        from django_cfg import DjangoConfig, CurrencyConfig

        class MyConfig(DjangoConfig):
            currency = CurrencyConfig(target_currency="USD")
        ```
    """

    enabled: bool = Field(default=True, description="Enable currency app")

    target_currency: str = Field(
        default="USD",
        description="Target currency for all conversions (e.g., USD)"
    )

    update_interval: int = Field(
        default=3600,
        description="Rate update interval in seconds (default: 1 hour)"
    )

    update_on_startup: bool = Field(
        default=True,
        description="Update rates on app startup if stale"
    )

    auto_update_enabled: bool = Field(
        default=True,
        description="Enable automatic rate updates via RQ scheduler"
    )

    def get_rq_schedules(self) -> List["RQScheduleConfig"]:
        """
        Get RQ schedules for currency rate updates.

        Returns schedule for update_all_rates task based on update_interval.
        """
        if not self.enabled or not self.auto_update_enabled:
            return []

        from django_cfg.models.django.django_rq import RQScheduleConfig

        return [
            RQScheduleConfig(
                func="django_cfg.apps.tools.currency.tasks.update_all_rates",
                interval=self.update_interval,
                queue="default",
                description=f"Update currency rates (every {self.update_interval}s)",
            )
        ]


__all__ = ["CurrencyConfig"]
