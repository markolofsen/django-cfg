"""
Database configuration model for django_cfg.

Type-safe database connection configuration with validation.
"""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, PrivateAttr, field_validator, model_validator

from . import converters, routing, validators


class DatabaseConfig(BaseModel):
    """
    Type-safe database connection configuration.

    Supports both individual connection parameters and connection strings.
    Automatically validates connection parameters and provides helpful error messages.
    """

    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",  # Prevent typos in field names
    }

    # Core connection parameters
    engine: Optional[str] = Field(
        default=None,
        description="Django database engine (e.g., 'django.db.backends.postgresql'). If not provided, will be auto-detected from database URL scheme.",
        min_length=1,
    )

    name: str = Field(
        ...,
        description="Database name or connection string",
        min_length=1,
    )

    user: Optional[str] = Field(
        default=None,
        description="Database username",
    )

    password: Optional[str] = Field(
        default=None,
        description="Database password",
        repr=False,  # Don't show in repr for security
    )

    host: str = Field(
        default="localhost",
        description="Database host",
        min_length=1,
    )

    port: int = Field(
        default=5432,
        description="Database port",
        ge=1,
        le=65535,
    )

    # Connection options
    connect_timeout: int = Field(
        default=10,
        description="Connection timeout in seconds",
        ge=1,
        le=300,  # Max 5 minutes
    )

    sslmode: str = Field(
        default="prefer",
        description="SSL mode for connection",
    )

    # Additional database options
    options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional database-specific options",
    )

    # Connection pooling options (CRITICAL for preventing connection exhaustion)
    conn_max_age: int = Field(
        default=0,  # 0 disables persistent connections when using connection pooling
        description="Maximum age of database connections in seconds. Must be 0 when using connection pooling.",
        ge=0,
    )

    conn_health_checks: bool = Field(
        default=True,
        description="Enable database connection health checks",
    )

    # Database routing configuration
    apps: List[str] = Field(
        default_factory=list,
        description="Django app labels that should use this database",
    )

    operations: List[Literal["read", "write", "migrate"]] = Field(
        default_factory=lambda: ["read", "write", "migrate"],
        description="Allowed operations for this database",
        min_length=1,
    )

    migrate_to: Optional[str] = Field(
        default=None,
        description="Override database alias for migrations (if different from this database)",
    )

    routing_description: str = Field(
        default="",
        description="Human-readable description of the routing rule",
    )

    # Internal fields for parsed connection strings
    _is_connection_string: bool = PrivateAttr(default=False)
    _parsed_components: Optional[Dict[str, Any]] = PrivateAttr(default=None)

    # Validators
    @field_validator("engine")
    @classmethod
    def validate_engine(cls, v: Optional[str]) -> Optional[str]:
        """Validate Django database engine format."""
        return validators.validate_engine(v)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate database name or parse connection string."""
        return validators.validate_name(v)

    @field_validator("sslmode")
    @classmethod
    def validate_sslmode(cls, v: str) -> str:
        """Validate SSL mode values."""
        return validators.validate_sslmode(v)

    @field_validator("apps")
    @classmethod
    def validate_apps(cls, v: List[str]) -> List[str]:
        """Validate app labels format."""
        return validators.validate_apps(v)

    @field_validator("operations")
    @classmethod
    def validate_operations(cls, v: List[str]) -> List[str]:
        """Validate operations list."""
        return validators.validate_operations(v)

    @model_validator(mode="before")
    @classmethod
    def validate_connection_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate connection parameter consistency and auto-detect engine."""
        return validators.validate_connection_consistency(values)

    @model_validator(mode="after")
    def validate_connection_after(self) -> "DatabaseConfig":
        """Validate connection after model creation."""
        return validators.validate_connection_after(self)

    # Converters
    def to_django_config(self) -> Dict[str, Any]:
        """
        Convert to Django database configuration format.

        Returns:
            Django-compatible database configuration dictionary

        Raises:
            DatabaseError: If configuration cannot be converted
        """
        return converters.to_django_config(self)

    # Routing methods
    def matches_app(self, app_label: str) -> bool:
        """
        Check if this database should be used for the given app.

        Args:
            app_label: Django app label to check

        Returns:
            True if this database should be used for the app
        """
        return routing.matches_app(self, app_label)

    def allows_operation(self, operation: str) -> bool:
        """
        Check if this database allows the given operation.

        Args:
            operation: Operation to check ('read', 'write', 'migrate')

        Returns:
            True if operation is allowed
        """
        return routing.allows_operation(self, operation)

    def get_migration_database(self) -> Optional[str]:
        """
        Get the database alias to use for migrations.

        Returns:
            Database alias for migrations, or None to use this database
        """
        return routing.get_migration_database(self)

    def has_routing_rules(self) -> bool:
        """
        Check if this database has any routing rules configured.

        Returns:
            True if apps list is not empty
        """
        return routing.has_routing_rules(self)

    def test_connection(self) -> bool:
        """
        Test database connection (placeholder for future implementation).

        Returns:
            True if connection successful, False otherwise
        """
        return routing.test_connection(self)

    # Factory methods
    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        apps: Optional[List[str]] = None,
        operations: Optional[List[Literal["read", "write", "migrate"]]] = None,
        routing_description: str = "",
        conn_max_age: int = 0,  # 0 disables persistent connections when using connection pooling
        conn_health_checks: bool = True,
        **kwargs
    ) -> "DatabaseConfig":
        """
        Create DatabaseConfig from URL with automatic engine detection.

        Args:
            url: Database URL (e.g., 'postgresql://user:pass@host:port/db')
            apps: Django app labels that should use this database
            operations: Allowed operations for this database
            routing_description: Human-readable description of the routing rule
            **kwargs: Additional parameters to override defaults

        Returns:
            DatabaseConfig instance with auto-detected engine

        Example:
            # Simple SQLite database
            db = DatabaseConfig.from_url("sqlite:///db.sqlite3")

            # PostgreSQL with routing
            blog_db = DatabaseConfig.from_url(
                "postgresql://user:pass@localhost:5432/blog",
                apps=["apps.blog"],
                routing_description="Blog posts and comments"
            )
        """
        return cls(
            name=url,
            apps=apps or [],
            operations=operations or ["read", "write", "migrate"],
            routing_description=routing_description,
            conn_max_age=conn_max_age,
            conn_health_checks=conn_health_checks,
            **kwargs
        )


__all__ = [
    "DatabaseConfig",
]
