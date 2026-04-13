"""
Auto-discovery and loading of project-level MCP configuration.

Automatically finds mcp/__init__.py in the project root directory
and imports its mcp_config variable.
"""

import importlib.util
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def mcp_config_exists() -> bool:
    """
    Check if project-level mcp/__init__.py exists.

    Returns True if mcp/__init__.py is found in the project root.
    """
    from django_cfg.core.utils.paths import get_base_path
    mcp_file = get_base_path("mcp", "__init__.py")
    return mcp_file.exists()


def load_project_mcp_config() -> Optional[Any]:
    """
    Automatically discover and load mcp/ folder from project root.

    Searches for mcp/__init__.py in the project directory (where manage.py lives)
    and imports its mcp_config variable if found.

    Returns:
        The mcp_config object from project's mcp/__init__.py, or None if not found.
    """
    if not mcp_config_exists():
        return None

    from django_cfg.core.utils.paths import get_base_path
    mcp_file = get_base_path("mcp", "__init__.py")

    # Import the module dynamically
    try:
        spec = importlib.util.spec_from_file_location("project_mcp", mcp_file)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load spec for {mcp_file}")
            return None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get mcp_config from the module
        mcp_config = getattr(module, "mcp_config", None)
        if mcp_config is None:
            logger.warning(f"mcp_config not found in {mcp_file}")
            return None

        logger.info(f"✅ MCP configuration loaded from {mcp_file}")
        return mcp_config

    except Exception as e:
        logger.error(f"Failed to load MCP config from {mcp_file}: {e}")
        return None
