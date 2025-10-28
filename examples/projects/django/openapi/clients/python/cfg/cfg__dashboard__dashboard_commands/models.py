from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CommandHelpResponse(BaseModel):
    """
    Response serializer for command help.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    status: str = ...
    command: str = ...
    app: str = None
    help_text: str = None
    is_allowed: bool = None
    risk_level: str = None
    error: str = None



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



class CommandExecuteRequestRequest(BaseModel):
    """
    Request serializer for command execution.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="allow",
        frozen=False,
    )

    command: str = Field(description='Name of the Django management command', min_length=1)
    args: list[str] = Field(None, description='Positional arguments for the command')
    options: Any = Field(None, description="Named options for the command (e.g., {'verbosity': '2'})")



