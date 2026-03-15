"""
Extension RQ Schedules Discovery

Auto-discovers and collects RQ scheduled tasks from all enabled extensions.
"""

import importlib
from pathlib import Path
from typing import TYPE_CHECKING

from django_cfg.utils import get_logger

if TYPE_CHECKING:
    from django_cfg.models.django.django_rq import RQScheduleConfig

logger = get_logger(__name__)


def get_extension_schedules() -> list["RQScheduleConfig"]:
    """
    Collect RQ scheduled tasks from all discovered extensions.

    Calls get_rq_schedules() on each extension's settings from __cfg__.py.
    Extensions can define schedules statically or dynamically.

    Returns:
        List of RQScheduleConfig from all extensions

    Example:
        In extension's __cfg__.py:
        ```python
        from django_cfg.models.django.django_rq import RQScheduleConfig

        class MyExtSettings(BaseExtensionSettings):
            # Static schedules
            schedules = [
                RQScheduleConfig(
                    func="extensions.apps.myext.tasks.cleanup",
                    cron="0 * * * *",
                    description="Hourly cleanup",
                ),
            ]

            # Or dynamic schedules
            def get_rq_schedules(self):
                schedules = list(self.schedules)
                if self.some_feature_enabled:
                    schedules.append(RQScheduleConfig(...))
                return schedules
        ```
    """
    schedules: list["RQScheduleConfig"] = []

    try:
        from django_cfg.core.state import get_current_config
        from django_cfg.extensions import get_extension_loader

        config = get_current_config()
        if not config:
            return schedules

        loader = get_extension_loader(base_path=Path(config.base_dir))
        extensions = loader.scanner.discover_all()

        for ext in extensions:
            if ext.type != "app" or not ext.is_valid:
                continue

            # Try to load __cfg__.py and get schedules
            try:
                config_module = importlib.import_module(f"extensions.apps.{ext.name}.__cfg__")
                settings = getattr(config_module, "settings", None)

                if settings and hasattr(settings, "get_rq_schedules"):
                    ext_schedules = settings.get_rq_schedules()
                    if ext_schedules:
                        schedules.extend(ext_schedules)
                        logger.debug(f"Loaded {len(ext_schedules)} RQ schedules from {ext.name}")

            except ImportError as e:
                logger.debug(f"No __cfg__.py for extension {ext.name}: {e}")
            except Exception as e:
                logger.warning(f"Failed to load RQ schedules from {ext.name}: {e}")

    except Exception as e:
        logger.error(f"Failed to collect extension RQ schedules: {e}")

    return schedules
