"""MCP Module - Model Context Protocol integration."""

import logging
from django.apps import AppConfig
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class DjangoMCPConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_cfg.modules.django_mcp"
    label = "django_cfg_mcp"
    verbose_name = "Model Context Protocol (MCP)"

    def ready(self) -> None:
        """Initialize MCP module and auto-discover project config + tools."""
        from . import is_enabled
        if not is_enabled():
            return

        # Step 0: Register default tools (introspection, query, raw_sql, etc.)
        self._register_default_tools()

        # Step 1: Auto-discover and load project-level mcp/ folder config
        from .auto_loader import load_project_mcp_config
        project_config = load_project_mcp_config()
        if project_config is not None:
            try:
                from django_cfg.core.state import get_current_config
                config = get_current_config()
                if config.mcp is not None:
                    config.mcp = project_config
                    logger.info("✅ MCP project configuration applied successfully")
            except Exception as e:
                logger.warning(f"Failed to apply MCP project config: {e}")

        # Step 2: Auto-discover and register project tools
        self._discover_project_tools()

        # Step 3: Register connection signal for resource limits
        self._register_connection_signal()

    def _register_default_tools(self):
        """Register default MCP tools (introspection, query, raw_sql, etc.)."""
        try:
            from .handlers.tools import tool_registry  # This imports and registers all default tools
            from django_cfg.modules.django_mcp.tools.base import tool_registry as global_registry
            logger.info(f"✅ {len(global_registry._tools)} default MCP tools registered")
        except Exception as e:
            logger.warning(f"⚠️ Failed to register default MCP tools: {e}")

    def _discover_project_tools(self) -> int:
        """
        Auto-discover and register tools from project's mcp/tools/ directory.

        Scans all Python files in <project_root>/mcp/tools/*.py
        and imports them. Each file is expected to register its tools
        via tool_registry.register(YourTool()).

        Returns the number of tool modules discovered.
        """
        from .auto_loader import mcp_config_exists
        from .tools.base import tool_registry

        if not mcp_config_exists():
            return 0

        from django_cfg.core.state import get_current_config
        config = get_current_config()
        if not config:
            return 0

        import importlib
        import importlib.util
        from pathlib import Path

        project_root = config.base_dir
        tools_dir = project_root / "mcp" / "tools"

        if not tools_dir.exists():
            return 0

        count = 0
        for py_file in tools_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            module_name = f"project_mcp_tools.{py_file.stem}"
            try:
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    count += 1
                    logger.info(f"✅ MCP tool module registered: {py_file.name}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to load MCP tool module {py_file.name}: {e}")

        return count

    def _register_connection_signal(self):
        """Register connection signal to enforce resource limits."""
        from django.db.backends.signals import connection_created
        from django.dispatch import receiver

        @receiver(connection_created)
        def limit_mcp_resources(sender, connection, **kwargs):
            """Apply resource limits to MCP database connections."""
            try:
                from django_cfg.core.state import get_current_config
                config = get_current_config()
                if config and config.mcp and config.mcp.enabled:
                    with connection.cursor() as cursor:
                        cursor.execute("SET LOCAL statement_timeout = 5000")
                        cursor.execute("SET LOCAL work_mem = '16MB'")
                        cursor.execute("SET LOCAL lock_timeout = 2000")
            except Exception:
                pass
