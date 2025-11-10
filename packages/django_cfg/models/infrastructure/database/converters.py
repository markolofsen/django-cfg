"""
Database configuration converters.

Convert DatabaseConfig to Django settings format.
"""

from typing import Any, Dict


def to_django_config(config: "DatabaseConfig") -> Dict[str, Any]:  # type: ignore
    """
    Convert DatabaseConfig to Django database configuration format.

    Args:
        config: DatabaseConfig instance

    Returns:
        Django-compatible database configuration dictionary

    Raises:
        DatabaseError: If configuration cannot be converted
    """
    try:
        # Base configuration
        django_config = {
            "ENGINE": config.engine,
            "OPTIONS": {**config.options},
            "CONN_MAX_AGE": config.conn_max_age,
            "CONN_HEALTH_CHECKS": config.conn_health_checks,
        }

        # Add database-specific options
        if config.engine == "django.db.backends.postgresql":
            # PostgreSQL supports connect_timeout and sslmode
            django_config["OPTIONS"]["connect_timeout"] = config.connect_timeout
            django_config["OPTIONS"]["sslmode"] = config.sslmode
        elif config.engine == "django.db.backends.mysql":
            # MySQL supports connect_timeout but not sslmode
            django_config["OPTIONS"]["connect_timeout"] = config.connect_timeout
        # SQLite doesn't support connect_timeout or sslmode, so we skip them

        # Handle connection string vs individual parameters
        if config._is_connection_string:
            # For connection strings, use the full string as NAME
            django_config["NAME"] = config.name

            # Add parsed components if available
            if config._parsed_components:
                parsed = config._parsed_components
                if parsed.get("database"):
                    django_config["NAME"] = parsed["database"]
                if parsed.get("user"):
                    django_config["USER"] = parsed["user"]
                if parsed.get("password"):
                    django_config["PASSWORD"] = parsed["password"]
                if parsed.get("host"):
                    django_config["HOST"] = parsed["host"]
                if parsed.get("port"):
                    django_config["PORT"] = parsed["port"]
                if parsed.get("options"):
                    django_config["OPTIONS"].update(parsed["options"])
        else:
            # Individual parameters
            django_config["NAME"] = config.name

            if config.user:
                django_config["USER"] = config.user

            if config.password:
                django_config["PASSWORD"] = config.password

            if config.host:
                django_config["HOST"] = config.host

            if config.port:
                django_config["PORT"] = config.port

        return django_config

    except Exception as e:
        # Import here to avoid circular dependency
        from django_cfg.core.exceptions import DatabaseError

        raise DatabaseError(
            f"Failed to convert database configuration: {e}",
            database_alias=getattr(config, "_alias", "unknown"),
            context={"config": config.model_dump()}
        ) from e


__all__ = [
    "to_django_config",
]
