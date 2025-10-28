from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DashboardOverview(BaseModel):
    """
    Main serializer for dashboard overview endpoint. Uses DictField to avoid
    allOf generation in OpenAPI.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    stat_cards: list[Any] = Field(description='Dashboard statistics cards')
    system_health: list[Any] = Field(description='System health status')
    quick_actions: list[Any] = Field(description='Quick action buttons')
    recent_activity: list[Any] = Field(description='Recent activity entries')
    system_metrics: Any = Field(description='System performance metrics')
    user_statistics: Any = Field(description='User statistics')
    timestamp: str = Field(description='Data timestamp (ISO format)')



