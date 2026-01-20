"""
Database settings generator.

Handles DATABASES configuration and routing.
Size: ~100 lines (focused on database settings)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class DatabaseSettingsGenerator:
    """
    Generates Django DATABASES settings.

    Responsibilities:
    - Convert DatabaseConfig models to Django format
    - Apply smart defaults per database engine
    - Configure database routing

    Example:
        ```python
        generator = DatabaseSettingsGenerator(config)
        settings = generator.generate()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate database settings.

        Returns:
            Dictionary with DATABASES and routing configuration

        Example:
            >>> generator = DatabaseSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> "DATABASES" in settings
            True
        """
        settings = {}

        if not self.config.databases:
            return settings

        # Convert database configurations
        django_databases = {}
        for alias, db_config in self.config.databases.items():
            django_databases[alias] = db_config.to_django_config()

            # 🔥 AUTOMATICALLY add TEST settings for each database
            django_databases[alias]['TEST'] = self._generate_test_settings(alias, db_config)

        settings["DATABASES"] = django_databases

        # Apply database defaults for each database based on its engine
        from ....utils.smart_defaults import SmartDefaults

        for alias, db_config in self.config.databases.items():
            db_defaults = SmartDefaults.get_database_defaults(
                self.config.env_mode,
                self.config.debug,
                db_config.engine
            )
            if db_defaults:
                # Merge defaults with existing configuration
                for key, value in db_defaults.items():
                    if key == "OPTIONS":
                        # Merge OPTIONS dictionaries
                        existing_options = django_databases[alias].get("OPTIONS", {})
                        merged_options = {**value, **existing_options}
                        django_databases[alias]["OPTIONS"] = merged_options
                    elif key not in django_databases[alias]:
                        django_databases[alias][key] = value

        # Configure database routing if needed
        routing_settings = self._generate_routing_settings()
        settings.update(routing_settings)

        return settings

    def _generate_routing_settings(self) -> Dict[str, Any]:
        """
        Generate database routing configuration.

        Returns:
            Dictionary with routing settings
        """
        routing_rules = {}

        # Check if any database has routing rules
        for alias, db_config in self.config.databases.items():
            if db_config.has_routing_rules():
                for app in db_config.apps:
                    routing_rules[app] = alias

        if not routing_rules:
            return {}

        return {
            "DATABASE_ROUTERS": ["django_cfg.routing.routers.DatabaseRouter"],
            "DATABASE_ROUTING_RULES": routing_rules,
        }

    def _generate_test_settings(self, alias: str, db_config: "DatabaseConfig") -> Dict[str, Any]:
        """
        Automatic test database configuration.

        Args:
            alias: Database alias
            db_config: DatabaseConfig instance

        Returns:
            Dictionary with TEST settings

        Solves problems:
        - EOFError when trying input() in CI (auto-cleanup old databases)
        - Missing extensions in test database
        - Inconsistent migration history
        """
        test_settings: Dict[str, Any] = {}

        # Determine engine
        engine = db_config.engine or ""

        # Special settings for PostgreSQL / PostGIS
        if 'postgresql' in engine.lower() or 'postgis' in engine.lower():
            # Get main database name
            db_name = db_config.name

            # If connection string - extract database name
            if any(db_name.startswith(scheme) for scheme in ['postgresql://', 'postgres://', 'postgis://']):
                # Extract database name from URL (last part after /)
                try:
                    db_name = db_name.split('/')[-1].split('?')[0]
                except Exception:
                    db_name = 'test_db'

            test_settings.update({
                # Custom name for test database
                'NAME': f'test_{db_name}',

                # Use clean template without old data
                'TEMPLATE': 'template0',

                # Charset
                'CHARSET': 'UTF8',

                # Automatic database creation
                'CREATE_DB': True,

                # Automatic migration application
                'MIGRATE': True,
            })

        # Special settings for SQLite
        elif 'sqlite' in engine.lower():
            test_settings.update({
                # In-memory database for speed
                'NAME': ':memory:',
            })

        # Special settings for MySQL
        elif 'mysql' in engine.lower():
            test_settings.update({
                'CHARSET': 'utf8mb4',
                'COLLATION': 'utf8mb4_unicode_ci',
            })

        return test_settings


__all__ = ["DatabaseSettingsGenerator"]
