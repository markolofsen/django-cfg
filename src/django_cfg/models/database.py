"""
Database configuration models for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper type annotations for all fields
- No mutable default arguments
- Comprehensive validation with helpful error messages
"""

from typing import Dict, List, Optional, Any, Literal, Union
from pathlib import Path
from pydantic import BaseModel, Field, field_validator, model_validator, PrivateAttr
from urllib.parse import urlparse

from django_cfg.core.exceptions import DatabaseError, ValidationError


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

    @field_validator("engine")
    @classmethod
    def validate_engine(cls, v: Optional[str]) -> Optional[str]:
        """Validate Django database engine format."""
        if v is None:
            return v
            
        if not v.startswith("django.db.backends."):
            raise ValueError(f"Invalid database engine '{v}'. " "Must start with 'django.db.backends.'")

        # Common engines validation
        valid_engines = {
            "django.db.backends.postgresql",
            "django.db.backends.mysql",
            "django.db.backends.sqlite3",
            "django.db.backends.oracle",
        }

        if v not in valid_engines and not v.startswith("django.db.backends."):
            # Allow custom backends but warn about common typos
            common_typos = {
                "postgresql": "django.db.backends.postgresql",
                "postgres": "django.db.backends.postgresql",
                "mysql": "django.db.backends.mysql",
                "sqlite": "django.db.backends.sqlite3",
                "sqlite3": "django.db.backends.sqlite3",
            }

            if v in common_typos:
                raise ValueError(f"Invalid engine '{v}'. Did you mean '{common_typos[v]}'?")

        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate database name or parse connection string."""
        # Check if it's a connection string
        if "://" in v:
            try:
                parsed = urlparse(v)
                if not parsed.scheme:
                    raise ValueError("Invalid connection string format")
                return v
            except Exception as e:
                raise ValueError(f"Invalid connection string: {e}") from e

        # Regular database name validation
        if v in [":memory:", ""]:
            return v  # Special cases for SQLite

        # Check for path-like names (SQLite files)
        if "/" in v or "\\" in v or v.endswith(".db") or v.endswith(".sqlite3"):
            path = Path(v)
            if path.is_absolute() or v.startswith("./") or v.startswith("../"):
                return v  # Valid file path

        return v

    @field_validator("sslmode")
    @classmethod
    def validate_sslmode(cls, v: str) -> str:
        """Validate SSL mode values."""
        valid_modes = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}

        if v not in valid_modes:
            raise ValueError(f"Invalid SSL mode '{v}'. " f"Valid options: {', '.join(sorted(valid_modes))}")

        return v

    @model_validator(mode="before")
    @classmethod
    def validate_connection_consistency(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate connection parameter consistency and auto-detect engine."""
        # Auto-detect engine if not provided
        if values.get("engine") is None and values.get("name"):
            values["engine"] = cls._detect_engine_from_url(values["name"])
        
        return values

    @model_validator(mode="after")
    def validate_connection_after(self) -> "DatabaseConfig":
        """Validate connection after model creation."""
        # Parse connection string if present
        if "://" in self.name:
            self._is_connection_string = True
            self._parsed_components = self._parse_connection_string(self.name)

            # Override individual parameters with parsed values if not explicitly set
            parsed = self._parsed_components
            if parsed and not self.user and parsed.get("user"):
                object.__setattr__(self, 'user', parsed["user"])
            if parsed and not self.password and parsed.get("password"):
                object.__setattr__(self, 'password', parsed["password"])
            if parsed and self.host == "localhost" and parsed.get("host"):
                object.__setattr__(self, 'host', parsed["host"])
            if parsed and self.port == 5432 and parsed.get("port"):
                object.__setattr__(self, 'port', parsed["port"])

        # Validate SQLite-specific constraints
        if self.engine == "django.db.backends.sqlite3":
            if self.name not in [":memory:", ""] and not (self.name.endswith((".db", ".sqlite", ".sqlite3")) or "/" in self.name or "\\" in self.name):
                raise ValueError("SQLite database name must be ':memory:', a file path, " "or end with .db, .sqlite, or .sqlite3")

        # Validate PostgreSQL-specific constraints
        elif self.engine == "django.db.backends.postgresql":
            if not self._is_connection_string and not self.name:
                raise ValueError("PostgreSQL database name is required")

        return self

    @staticmethod
    def _detect_engine_from_url(url: str) -> str:
        """
        Automatically detect Django database engine from URL scheme.
        
        Args:
            url: Database URL (e.g., 'postgresql://...', 'sqlite:///...')
            
        Returns:
            Django database engine string
            
        Raises:
            ValueError: If URL scheme is not supported
        """
        if "://" not in url:
            # Assume SQLite for file paths without scheme
            return "django.db.backends.sqlite3"
            
        scheme = url.split("://")[0].lower()
        
        # Map URL schemes to Django engines
        scheme_to_engine = {
            "postgresql": "django.db.backends.postgresql",
            "postgres": "django.db.backends.postgresql",
            "mysql": "django.db.backends.mysql",
            "sqlite": "django.db.backends.sqlite3",
            "sqlite3": "django.db.backends.sqlite3",
            "oracle": "django.db.backends.oracle",
        }
        
        if scheme in scheme_to_engine:
            return scheme_to_engine[scheme]
            
        raise ValueError(
            f"Unsupported database scheme '{scheme}'. "
            f"Supported schemes: {', '.join(scheme_to_engine.keys())}"
        )

    @staticmethod
    def _parse_connection_string(connection_string: str) -> Dict[str, Any]:
        """Parse database connection string into components."""
        try:
            parsed = urlparse(connection_string)

            components = {
                "scheme": parsed.scheme,
                "user": parsed.username,
                "password": parsed.password,
                "host": parsed.hostname,
                "port": parsed.port,
                "database": parsed.path.lstrip("/") if parsed.path else None,
            }

            # Parse query parameters as options
            if parsed.query:
                from urllib.parse import parse_qs

                query_params = parse_qs(parsed.query)
                components["options"] = {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}

            return components

        except Exception as e:
            raise DatabaseError(f"Failed to parse connection string: {e}", context={"connection_string": connection_string}) from e

    def to_django_config(self) -> Dict[str, Any]:
        """
        Convert to Django database configuration format.

        Returns:
            Django-compatible database configuration dictionary

        Raises:
            DatabaseError: If configuration cannot be converted
        """
        try:
            # Base configuration
            config = {
                "ENGINE": self.engine,
                "OPTIONS": {**self.options},
            }
            
            # Add database-specific options
            if self.engine == "django.db.backends.postgresql":
                # PostgreSQL supports connect_timeout and sslmode
                config["OPTIONS"]["connect_timeout"] = self.connect_timeout
                config["OPTIONS"]["sslmode"] = self.sslmode
            elif self.engine == "django.db.backends.mysql":
                # MySQL supports connect_timeout but not sslmode
                config["OPTIONS"]["connect_timeout"] = self.connect_timeout
            # SQLite doesn't support connect_timeout or sslmode, so we skip them

            # Handle connection string vs individual parameters
            if self._is_connection_string:
                # For connection strings, use the full string as NAME
                config["NAME"] = self.name

                # Add parsed components if available
                if self._parsed_components:
                    parsed = self._parsed_components
                    if parsed.get("database"):
                        config["NAME"] = parsed["database"]
                    if parsed.get("user"):
                        config["USER"] = parsed["user"]
                    if parsed.get("password"):
                        config["PASSWORD"] = parsed["password"]
                    if parsed.get("host"):
                        config["HOST"] = parsed["host"]
                    if parsed.get("port"):
                        config["PORT"] = parsed["port"]
                    if parsed.get("options"):
                        config["OPTIONS"].update(parsed["options"])
            else:
                # Individual parameters
                config["NAME"] = self.name

                if self.user:
                    config["USER"] = self.user

                if self.password:
                    config["PASSWORD"] = self.password

                if self.host:
                    config["HOST"] = self.host

                if self.port:
                    config["PORT"] = self.port

            return config

        except Exception as e:
            raise DatabaseError(f"Failed to convert database configuration: {e}", database_alias=getattr(self, "_alias", "unknown"), context={"config": self.model_dump()}) from e

    @field_validator("apps")
    @classmethod
    def validate_apps(cls, v: List[str]) -> List[str]:
        """Validate app labels format."""
        for app in v:
            if not app or not app.replace("_", "").replace(".", "").isalnum():
                raise ValueError(f"Invalid app label '{app}'. " "App labels must contain only letters, numbers, dots, and underscores")
        return v

    @field_validator("operations")
    @classmethod
    def validate_operations(cls, v: List[str]) -> List[str]:
        """Validate operations list."""
        if not v:
            raise ValueError("At least one operation must be specified")

        valid_ops = {"read", "write", "migrate"}
        for op in v:
            if op not in valid_ops:
                raise ValueError(f"Invalid operation '{op}'. " f"Valid operations: {', '.join(sorted(valid_ops))}")
        return v

    def matches_app(self, app_label: str) -> bool:
        """
        Check if this database should be used for the given app.

        Args:
            app_label: Django app label to check

        Returns:
            True if this database should be used for the app
        """
        return app_label in self.apps

    def allows_operation(self, operation: str) -> bool:
        """
        Check if this database allows the given operation.

        Args:
            operation: Operation to check ('read', 'write', 'migrate')

        Returns:
            True if operation is allowed
        """
        return operation in self.operations

    def get_migration_database(self) -> Optional[str]:
        """
        Get the database alias to use for migrations.

        Returns:
            Database alias for migrations, or None to use this database
        """
        return self.migrate_to

    def has_routing_rules(self) -> bool:
        """
        Check if this database has any routing rules configured.

        Returns:
            True if apps list is not empty
        """
        return bool(self.apps)

    def test_connection(self) -> bool:
        """
        Test database connection (placeholder for future implementation).

        Returns:
            True if connection successful, False otherwise
        """
        # TODO: Implement actual connection testing
        # This would require Django to be available and configured
        return True

    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        apps: Optional[List[str]] = None,
        operations: Optional[List[Literal["read", "write", "migrate"]]] = None,
        routing_description: str = "",
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
            **kwargs
        )


# Export all models
__all__ = [
    "DatabaseConfig",
]
