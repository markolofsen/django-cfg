from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ChartData(BaseModel):
    """
    Chart.js data structure serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    labels: list[str] = ...
    datasets: list[Any] = ...



