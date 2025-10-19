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


__all__ = ["DatabaseSettingsGenerator"]
