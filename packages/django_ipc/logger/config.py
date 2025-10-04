"""
Logger Configuration Models

Pydantic models for structured logging configuration.
"""

from typing import Optional, Literal
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LogRotationConfig(BaseModel):
    """
    Log rotation configuration.

    Supports size-based and time-based rotation.

    Example:
        >>> config = LogRotationConfig(
        ...     max_bytes=10 * 1024 * 1024,  # 10 MB
        ...     backup_count=5,
        ...     rotation_time="midnight",
        ... )
    """

    max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Maximum size of log file before rotation (bytes)",
        ge=1024,  # Min 1 KB
    )

    backup_count: int = Field(
        default=5,
        description="Number of backup files to keep",
        ge=0,
        le=100,
    )

    rotation_time: Optional[str] = Field(
        default=None,
        description="Time-based rotation (midnight, H, D, W0-W6)",
    )


class LoggerConfig(BaseModel):
    """
    Complete logger configuration.

    Configures structured logging with rotation, separate error logs,
    and RPC request/response tracking.

    Example:
        >>> config = LoggerConfig(
        ...     log_dir="./logs",
        ...     level="INFO",
        ...     log_rpc_calls=True,
        ...     log_errors=True,
        ... )
    """

    # Directory settings
    log_dir: str = Field(
        default="./logs",
        description="Directory for log files",
    )

    # Logging levels
    level: LogLevel = Field(
        default="INFO",
        description="Global log level",
    )

    # What to log
    log_rpc_calls: bool = Field(
        default=True,
        description="Log all RPC calls (request/response)",
    )

    log_errors: bool = Field(
        default=True,
        description="Log errors to separate error.log file",
    )

    log_performance: bool = Field(
        default=True,
        description="Log performance metrics (RPC timing)",
    )

    log_connections: bool = Field(
        default=True,
        description="Log WebSocket connection events",
    )

    # Format settings
    use_json: bool = Field(
        default=True,
        description="Use JSON structured logging format",
    )

    include_timestamp: bool = Field(
        default=True,
        description="Include timestamp in logs",
    )

    include_correlation_id: bool = Field(
        default=True,
        description="Include correlation_id for request tracking",
    )

    include_caller_info: bool = Field(
        default=False,
        description="Include file/line info (performance overhead)",
    )

    # Rotation settings
    rotation: LogRotationConfig = Field(
        default_factory=LogRotationConfig,
        description="Log rotation configuration",
    )

    # Console output
    console_output: bool = Field(
        default=True,
        description="Also output logs to console",
    )

    console_level: Optional[LogLevel] = Field(
        default=None,
        description="Console log level (uses 'level' if None)",
    )

    @field_validator("log_dir")
    @classmethod
    def validate_log_dir(cls, v: str) -> str:
        """Create log directory if it doesn't exist."""
        log_path = Path(v)
        log_path.mkdir(parents=True, exist_ok=True)
        return v

    def get_log_file(self, log_type: str = "app") -> Path:
        """
        Get path to log file.

        Args:
            log_type: Type of log (app, error, rpc, performance)

        Returns:
            Path to log file

        Example:
            >>> config = LoggerConfig(log_dir="./logs")
            >>> config.get_log_file("error")
            PosixPath('logs/error.log')
        """
        return Path(self.log_dir) / f"{log_type}.log"


__all__ = [
    "LogLevel",
    "LogRotationConfig",
    "LoggerConfig",
]
