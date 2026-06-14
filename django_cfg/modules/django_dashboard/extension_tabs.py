"""
Extension-provided admin dashboard tabs.

Mirrors ``django_unfold.navigation.manager._get_extension_navigation``: each
discovered ``type == "app"`` extension may declare ``dashboard_tabs`` in its
``__cfg__.py`` ``settings`` object, and those tabs are merged into the
project's ``DashboardConfig.tabs`` at render time. This keeps the consumer
project's ``api/config.py`` free of extension-specific dashboard wiring.
"""

import importlib
import traceback
from typing import Any, List

from django_cfg.utils import get_logger
from django_cfg.modules.base import BaseCfgModule

from .models import DashboardTab

logger = get_logger(__name__)


def _coerce_tab(item: Any) -> DashboardTab | None:
    """Coerce an extension-declared tab into a DashboardTab."""
    if isinstance(item, DashboardTab):
        return item
    if isinstance(item, dict):
        return DashboardTab(**item)
    # Already a compatible model (e.g. subclass) — accept as-is.
    if hasattr(item, "slug") and hasattr(item, "title"):
        return item
    raise TypeError(f"Unsupported dashboard tab entry: {type(item)!r}")


def get_extension_dashboard_tabs() -> List[DashboardTab]:
    """Collect dashboard tabs declared by auto-discovered extensions.

    Robust to misconfigured extensions — a failure in one extension is logged
    and skipped, never propagated to the dashboard render.
    """
    tabs: List[DashboardTab] = []
    try:
        extensions = BaseCfgModule()._get_discovered_extensions()
        for ext in extensions:
            try:
                if ext.type != "app" or not ext.manifest:
                    continue
                config_mod = importlib.import_module(f"extensions.apps.{ext.name}.__cfg__")
                settings_obj = getattr(config_mod, "settings", None)
                if not settings_obj or not getattr(settings_obj, "enabled", True):
                    continue
                ext_tabs = getattr(settings_obj, "dashboard_tabs", None)
                if not ext_tabs:
                    continue
                for raw in ext_tabs:
                    try:
                        coerced = _coerce_tab(raw)
                        if coerced is not None:
                            tabs.append(coerced)
                    except Exception:
                        logger.warning(
                            f"Failed dashboard tab in extension '{ext.name}':\n{traceback.format_exc()}"
                        )
            except Exception:
                logger.error(f"Extension '{ext.name}' dashboard tabs failed:\n{traceback.format_exc()}")
    except Exception:
        logger.error(f"Extension dashboard tab discovery failed:\n{traceback.format_exc()}")

    return tabs
