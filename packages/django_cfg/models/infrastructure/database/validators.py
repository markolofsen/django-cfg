"""
Database configuration validators.

Field validators for DatabaseConfig model.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .parsers import detect_engine_from_url, parse_connection_string


def validate_engine(v: Optional[str]) -> Optional[str]:
    """Validate Django database engine format."""
    if v is None:
        return v

    # Allow both django.db.backends.* and django.contrib.gis.db.backends.*
    valid_prefixes = (
        "django.db.backends.",
        "django.contrib.gis.db.backends.",
    )

    if not v.startswith(valid_prefixes):
        raise ValueError(
            f"Invalid database engine '{v}'. "
            "Must start with 'django.db.backends.' or 'django.contrib.gis.db.backends.'"
        )

    # Common engines validation
    valid_engines = {
        # Standard backends
        "django.db.backends.postgresql",
        "django.db.backends.mysql",
        "django.db.backends.sqlite3",
        "django.db.backends.oracle",
        # PostGIS backends (for spatial queries)
        "django.contrib.gis.db.backends.postgis",
        "django.contrib.gis.db.backends.mysql",
        "django.contrib.gis.db.backends.oracle",
        "django.contrib.gis.db.backends.spatialite",
    }

    if v not in valid_engines and not v.startswith(valid_prefixes):
        # Allow custom backends but warn about common typos
        common_typos = {
            "postgresql": "django.db.backends.postgresql",
            "postgres": "django.db.backends.postgresql",
            "postgis": "django.contrib.gis.db.backends.postgis",
            "mysql": "django.db.backends.mysql",
            "sqlite": "django.db.backends.sqlite3",
            "sqlite3": "django.db.backends.sqlite3",
            "spatialite": "django.contrib.gis.db.backends.spatialite",
        }

        if v in common_typos:
            raise ValueError(
                f"Invalid engine '{v}'. Did you mean '{common_typos[v]}'?"
            )

    return v


def validate_name(v: str) -> str:
    """Validate database name or parse connection string. Allows environment variable templates like ${VAR:-default}."""
    # Skip validation for environment variable templates
    if v.startswith("${") and "}" in v:
        return v

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


def validate_sslmode(v: str) -> str:
    """Validate SSL mode values."""
    valid_modes = {"disable", "allow", "prefer", "require", "verify-ca", "verify-full"}

    if v not in valid_modes:
        raise ValueError(
            f"Invalid SSL mode '{v}'. "
            f"Valid options: {', '.join(sorted(valid_modes))}"
        )

    return v


def validate_connection_consistency(values: Dict[str, Any]) -> Dict[str, Any]:
    """Validate connection parameter consistency and auto-detect engine."""
    # Auto-detect engine if not provided
    if values.get("engine") is None and values.get("name"):
        values["engine"] = detect_engine_from_url(values["name"])

    return values


def validate_connection_after(config: "DatabaseConfig") -> "DatabaseConfig":  # type: ignore
    """Validate connection after model creation."""
    # Parse connection string if present
    if "://" in config.name:
        object.__setattr__(config, '_is_connection_string', True)
        parsed = parse_connection_string(config.name)
        object.__setattr__(config, '_parsed_components', parsed)

        # Override individual parameters with parsed values if not explicitly set
        if parsed and not config.user and parsed.get("user"):
            object.__setattr__(config, 'user', parsed["user"])
        if parsed and not config.password and parsed.get("password"):
            object.__setattr__(config, 'password', parsed["password"])
        if parsed and config.host == "localhost" and parsed.get("host"):
            object.__setattr__(config, 'host', parsed["host"])
        if parsed and config.port == 5432 and parsed.get("port"):
            object.__setattr__(config, 'port', parsed["port"])

    # Validate SQLite-specific constraints
    if config.engine == "django.db.backends.sqlite3":
        if config.name not in [":memory:", ""] and not (
            config.name.endswith((".db", ".sqlite", ".sqlite3"))
            or "/" in config.name
            or "\\" in config.name
        ):
            raise ValueError(
                "SQLite database name must be ':memory:', a file path, "
                "or end with .db, .sqlite, or .sqlite3"
            )

    # Validate PostgreSQL-specific constraints
    elif config.engine == "django.db.backends.postgresql":
        if not config._is_connection_string and not config.name:
            raise ValueError("PostgreSQL database name is required")

    # Validate PostGIS-specific constraints (same as PostgreSQL)
    elif config.engine == "django.contrib.gis.db.backends.postgis":
        if not config._is_connection_string and not config.name:
            raise ValueError("PostGIS database name is required")

    return config


def validate_apps(v: List[str]) -> List[str]:
    """Validate app labels format."""
    for app in v:
        if not app or not app.replace("_", "").replace(".", "").isalnum():
            raise ValueError(
                f"Invalid app label '{app}'. "
                "App labels must contain only letters, numbers, dots, and underscores"
            )
    return v


def validate_operations(v: List[str]) -> List[str]:
    """Validate operations list."""
    if not v:
        raise ValueError("At least one operation must be specified")

    valid_ops = {"read", "write", "migrate"}
    for op in v:
        if op not in valid_ops:
            raise ValueError(
                f"Invalid operation '{op}'. "
                f"Valid operations: {', '.join(sorted(valid_ops))}"
            )
    return v


__all__ = [
    "validate_engine",
    "validate_name",
    "validate_sslmode",
    "validate_connection_consistency",
    "validate_connection_after",
    "validate_apps",
    "validate_operations",
]
