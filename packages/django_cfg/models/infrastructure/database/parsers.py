"""
Database connection string parsers.

Utilities for parsing and detecting database engines from URLs.
"""

from typing import Any, Dict
from urllib.parse import urlparse


def detect_engine_from_url(url: str) -> str:
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
        # Standard backends
        "postgresql": "django.db.backends.postgresql",
        "postgres": "django.db.backends.postgresql",
        "mysql": "django.db.backends.mysql",
        "sqlite": "django.db.backends.sqlite3",
        "sqlite3": "django.db.backends.sqlite3",
        "oracle": "django.db.backends.oracle",
        # PostGIS backends (for spatial queries)
        "postgis": "django.contrib.gis.db.backends.postgis",
        "spatialite": "django.contrib.gis.db.backends.spatialite",
    }

    if scheme in scheme_to_engine:
        return scheme_to_engine[scheme]

    raise ValueError(
        f"Unsupported database scheme '{scheme}'. "
        f"Supported schemes: {', '.join(scheme_to_engine.keys())}"
    )


def parse_connection_string(connection_string: str) -> Dict[str, Any]:
    """
    Parse database connection string into components.

    Args:
        connection_string: Database URL to parse

    Returns:
        Dictionary with parsed components (scheme, user, password, host, port, database, options)

    Raises:
        DatabaseError: If connection string cannot be parsed
    """
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
        # Import here to avoid circular dependency
        from django_cfg.core.exceptions import DatabaseError

        raise DatabaseError(
            f"Failed to parse connection string: {e}",
            context={"connection_string": connection_string}
        ) from e


__all__ = [
    "detect_engine_from_url",
    "parse_connection_string",
]
