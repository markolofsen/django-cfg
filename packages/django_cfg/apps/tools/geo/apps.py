"""
Django app configuration for geo app.

Handles auto-population of geo data on startup if configured.
"""

import logging
import sys
import threading

from django.apps import AppConfig

logger = logging.getLogger(__name__)


class GeoAppConfig(AppConfig):
    """
    Geographic data app.

    Provides:
    - Country, State, City models (PostgreSQL)
    - CountryField, CityField for models
    - AJAX search endpoints for Select2 widgets
    - Proximity search via geopy
    """

    name = "django_cfg.apps.tools.geo"
    label = "cfg_geo"
    verbose_name = "Geographic Data"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        """Initialize app on Django startup."""
        # Skip during migrations and other management commands
        skip_commands = ["migrate", "makemigrations", "collectstatic", "createsuperuser"]
        if any(cmd in sys.argv for cmd in skip_commands):
            return

        # Check if auto_populate is enabled via DjangoConfig
        try:
            from django_cfg.core import get_config

            config = get_config()

            if config.geo and config.geo.enabled and config.geo.auto_populate:
                # Run population in background thread to not block startup
                thread = threading.Thread(
                    target=self._populate_if_empty,
                    daemon=True,
                    name="geo-populate"
                )
                thread.start()
        except Exception as e:
            logger.debug(f"Could not check geo config: {e}")

    def _populate_if_empty(self) -> None:
        """Populate database if empty (runs in background)."""
        try:
            from .models import Country
            from .services.loader import GeoDataLoader

            # Check if data already exists
            if Country.objects.exists():
                logger.debug("Geo data already populated")
                return

            logger.info("Populating geo database on startup...")
            try:
                loader = GeoDataLoader()
                stats = loader.populate_database()
                logger.info(
                    f"Geo database populated: "
                    f"{stats['countries']} countries, "
                    f"{stats['states']} states, "
                    f"{stats['cities']} cities"
                )
            except Exception as e:
                logger.warning(f"Failed to populate geo database: {e}")
        except Exception as e:
            logger.debug(f"Could not initialize geo data: {e}")
