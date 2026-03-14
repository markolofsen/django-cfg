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

        # 🔥 AUTO-CREATE monitor database if monitor app is enabled
        self._ensure_monitor_database()

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

    def _ensure_monitor_database(self) -> None:
        """
        Auto-create monitor database alias if monitor app is enabled.

        The monitor app (django_cfg.apps.system.monitor) requires a separate
        database alias to prevent ATOMIC_REQUESTS rollback from losing error records.

        This method automatically creates the monitor database alias by copying
        the 'default' database configuration with conn_max_age=0 (no pooling).

        Why no pooling?
        - ServerEvent.record() uses get_or_create with F() expressions
        - Connection pooling can cause stale connection state
        - Fresh connections ensure transaction isolation
        """
        # Check if monitor app is enabled
        if not (self.config.frontend_monitor and self.config.frontend_monitor.enabled):
            return

        monitor_alias = getattr(self.config.frontend_monitor, 'monitor_db_alias', 'monitor')

        # Skip if monitor database already exists
        if monitor_alias in self.config.databases:
            return

        # Skip if 'default' database doesn't exist (nothing to copy from)
        if 'default' not in self.config.databases:
            logger.warning(
                f"Monitor app is enabled but cannot auto-create '{monitor_alias}' database: "
                f"'default' database not found. Please configure databases manually."
            )
            return

        # Create monitor database by copying default with conn_max_age=0
        from django_cfg.models import DatabaseConfig

        default_db = self.config.databases['default']

        # Clone default database config with no connection pooling
        monitor_db = DatabaseConfig(
            engine=default_db.engine,
            name=default_db.name,
            user=default_db.user,
            password=default_db.password,
            host=default_db.host,
            port=default_db.port,
            conn_max_age=0,  # CRITICAL: no pooling for monitor DB
            options=default_db.options.copy() if default_db.options else {},
            # Add routing rule for monitor app
            apps=['django_cfg_monitor'],
        )

        # Add to config.databases (mutate in place - safe in settings generation)
        self.config.databases[monitor_alias] = monitor_db

        logger.info(
            f"Auto-created '{monitor_alias}' database alias for monitor app "
            f"(same as 'default' but with conn_max_age=0)"
        )


__all__ = ["DatabaseSettingsGenerator"]
