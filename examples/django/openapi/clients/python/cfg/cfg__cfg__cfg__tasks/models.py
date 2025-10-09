from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..enums import QueueActionRequestaction, QueueActionaction, WorkerActionRequestaction, WorkerActionaction


class APIResponse(BaseModel):
    """
    Standard API response serializer.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = Field(description='Operation success status')
    message: str = Field(None, description='Success message')
    error: str = Field(None, description='Error message')
    data: dict[str, Any] = Field(None, description='Response data')



class QueueAction(BaseModel):
    """
    Serializer for queue management actions.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    action: QueueActionAction = Field(description='Action to perform on queues\n\n* `clear` - clear\n* `clear_all` - clear_all\n* `purge` - purge\n* `purge_failed` - purge_failed\n* `flush` - flush')
    queue_names: list[str] = Field(None, description='Specific queues to target (empty = all queues)')



class QueueStatus(BaseModel):
    """
    Serializer for queue status data.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    queues: dict[str, Any] = Field(description='Queue information with pending/failed counts')
    workers: int = Field(description='Number of active workers')
    redis_connected: bool = Field(description='Redis connection status')
    timestamp: str = Field(description='Current timestamp')
    error: str = Field(None, description='Error message if any')



class TaskStatistics(BaseModel):
    """
    Serializer for task statistics data.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    statistics: dict[str, Any] = Field(description='Task count statistics')
    recent_tasks: list[dict[str, Any]] = Field(description='List of recent tasks')
    timestamp: str = Field(description='Current timestamp')
    error: str = Field(None, description='Error message if any')



class WorkerAction(BaseModel):
    """
    Serializer for worker management actions.

    Response model (includes read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    action: WorkerActionAction = Field(description='Action to perform on workers\n\n* `start` - start\n* `stop` - stop\n* `restart` - restart')
    processes: int = Field(None, description='Number of worker processes', ge=1.0, le=10.0)
    threads: int = Field(None, description='Number of threads per process', ge=1.0, le=20.0)



class APIResponseRequest(BaseModel):
    """
    Standard API response serializer.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    success: bool = Field(description='Operation success status')
    message: str = Field(None, description='Success message', min_length=1)
    error: str = Field(None, description='Error message', min_length=1)
    data: dict[str, Any] = Field(None, description='Response data')



class QueueActionRequest(BaseModel):
    """
    Serializer for queue management actions.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    action: QueueActionRequestAction = Field(description='Action to perform on queues\n\n* `clear` - clear\n* `clear_all` - clear_all\n* `purge` - purge\n* `purge_failed` - purge_failed\n* `flush` - flush')
    queue_names: list[str] = Field(None, description='Specific queues to target (empty = all queues)')



class WorkerActionRequest(BaseModel):
    """
    Serializer for worker management actions.

    Request model (no read-only fields).
    """

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        frozen=False,
    )

    action: WorkerActionRequestAction = Field(description='Action to perform on workers\n\n* `start` - start\n* `stop` - stop\n* `restart` - restart')
    processes: int = Field(None, description='Number of worker processes', ge=1.0, le=10.0)
    threads: int = Field(None, description='Number of threads per process', ge=1.0, le=20.0)



