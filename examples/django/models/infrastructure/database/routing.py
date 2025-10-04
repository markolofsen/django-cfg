"""
Database routing utilities.

Methods for database routing and operation checks.
"""

from typing import Optional


def matches_app(config: "DatabaseConfig", app_label: str) -> bool:  # type: ignore
    """
    Check if this database should be used for the given app.

    Args:
        config: DatabaseConfig instance
        app_label: Django app label to check

    Returns:
        True if this database should be used for the app
    """
    return app_label in config.apps


def allows_operation(config: "DatabaseConfig", operation: str) -> bool:  # type: ignore
    """
    Check if this database allows the given operation.

    Args:
        config: DatabaseConfig instance
        operation: Operation to check ('read', 'write', 'migrate')

    Returns:
        True if operation is allowed
    """
    return operation in config.operations


def get_migration_database(config: "DatabaseConfig") -> Optional[str]:  # type: ignore
    """
    Get the database alias to use for migrations.

    Args:
        config: DatabaseConfig instance

    Returns:
        Database alias for migrations, or None to use this database
    """
    return config.migrate_to


def has_routing_rules(config: "DatabaseConfig") -> bool:  # type: ignore
    """
    Check if this database has any routing rules configured.

    Args:
        config: DatabaseConfig instance

    Returns:
        True if apps list is not empty
    """
    return bool(config.apps)


def test_connection(config: "DatabaseConfig") -> bool:  # type: ignore
    """
    Test database connection (placeholder for future implementation).

    Args:
        config: DatabaseConfig instance

    Returns:
        True if connection successful, False otherwise
    """
    # TODO: Implement actual connection testing
    # This would require Django to be available and configured
    return True


__all__ = [
    "matches_app",
    "allows_operation",
    "get_migration_database",
    "has_routing_rules",
    "test_connection",
]
