from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CommandsSummary(BaseModel):
    """
    Commands summary serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    total_commands: int = ...
    core_commands: int = ...
    custom_commands: int = ...
    categories: list[str] = ...
    commands: list[Any] = ...
    categorized: Any = ...



