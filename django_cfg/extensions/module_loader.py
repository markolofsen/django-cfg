"""
Module Loader for extension modules.

Discovers and loads utility modules from extensions/modules/.
"""

import importlib
import logging
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar

from .configs.modules.base import BaseModuleSettings
from .scanner import ExtensionScanner

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Global module loader instance
_module_loader: Optional["ModuleLoader"] = None


def get_module_loader(base_path: Optional[Path] = None) -> "ModuleLoader":
    """
    Get or create the global module loader instance.

    Args:
        base_path: Project root path. If None, uses current working directory.

    Returns:
        ModuleLoader instance
    """
    global _module_loader
    if _module_loader is None:
        _module_loader = ModuleLoader(base_path)
    return _module_loader


def requires_module(
    module_name: str,
    fallback: Optional[Callable[..., T]] = None,
) -> Callable[[Callable[..., T]], Callable[..., Optional[T]]]:
    """
    Decorator that checks if a module is enabled before executing.

    Args:
        module_name: Name of the module to check
        fallback: Optional fallback function to call if module is disabled

    Returns:
        Decorated function

    Example:
        @requires_module("telegram")
        def send_notification(message):
            from django_cfg.modules.django_telegram import send_message
            send_message(message)

        @requires_module("currency", fallback=lambda amount, *args: amount)
        def convert_to_usd(amount, from_currency):
            from extensions.modules.currency import convert
            return convert(amount, from_currency, "USD")
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Optional[T]:
            loader = get_module_loader()
            if not loader.is_module_enabled(module_name):
                if fallback:
                    return fallback(*args, **kwargs)
                logger.debug(f"Module '{module_name}' not enabled, skipping {func.__name__}")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


class ModuleLoader:
    """
    Loads and manages extension modules.

    Extension modules are utility libraries without Django models
    that can be optionally enabled per project via extensions/modules/.
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize module loader.

        Args:
            base_path: Project root path. If None, uses current working directory.
        """
        self.scanner = ExtensionScanner(base_path)
        self._modules_cache: Dict[str, Any] = {}
        self._settings_cache: Dict[str, BaseModuleSettings] = {}

    def get_enabled_modules(self) -> Dict[str, BaseModuleSettings]:
        """
        Get all enabled extension modules.

        Returns:
            Dictionary of module name to settings
        """
        modules = {}
        for ext in self.scanner.discover_modules():
            if ext.is_valid:
                settings = self.get_module_settings(ext.name)
                if settings and settings.enabled:
                    modules[ext.name] = settings
        return modules

    def is_module_enabled(self, name: str) -> bool:
        """
        Check if a module is enabled.

        Args:
            name: Module name

        Returns:
            True if module is enabled
        """
        settings = self.get_module_settings(name)
        return settings is not None and settings.enabled

    def get_module_settings(self, name: str) -> Optional[BaseModuleSettings]:
        """
        Get settings for a specific module.

        Args:
            name: Module name

        Returns:
            Module settings or None
        """
        if name in self._settings_cache:
            return self._settings_cache[name]

        # Try to load from extensions/modules/{name}/__cfg__.py
        ext = self.scanner.get_extension(name)
        if ext is None or ext.type != "module":
            return None

        try:
            config_path = ext.path / "__cfg__.py"
            if config_path.exists():
                module = self._import_module_file(config_path, f"_cfg_{name}")
                settings = getattr(module, "settings", None)
                if settings and isinstance(settings, BaseModuleSettings):
                    self._settings_cache[name] = settings
                    return settings
        except Exception as e:
            logger.error(f"Failed to load settings for module '{name}': {e}")

        return None

    def get_module(self, name: str) -> Optional[Any]:
        """
        Get module instance.

        First checks extensions/modules/{name}/ for local override,
        then falls back to django_cfg.modules.django_{name}.

        Args:
            name: Module name

        Returns:
            Module object or None
        """
        if name in self._modules_cache:
            return self._modules_cache[name]

        # Check if module is enabled
        if not self.is_module_enabled(name):
            logger.debug(f"Module '{name}' is not enabled")
            return None

        # Try local module first
        ext = self.scanner.get_extension(name)
        if ext and ext.type == "module":
            try:
                # Import from extensions.modules.{name}
                local_path = f"extensions.modules.{name}"
                module = importlib.import_module(local_path)
                self._modules_cache[name] = module
                return module
            except ImportError as e:
                logger.debug(f"Local module '{name}' not found: {e}")

        # Fall back to core module
        try:
            core_path = f"django_cfg.modules.django_{name}"
            module = importlib.import_module(core_path)
            self._modules_cache[name] = module
            return module
        except ImportError as e:
            logger.debug(f"Core module 'django_{name}' not found: {e}")

        return None

    def check_dependencies(self, name: str) -> Dict[str, list]:
        """
        Check if all dependencies for a module are installed.

        Args:
            name: Module name

        Returns:
            Dictionary with 'missing' list of uninstalled packages
        """
        settings = self.get_module_settings(name)
        if not settings:
            return {"missing": [], "error": f"Module '{name}' not found"}

        missing = settings.check_dependencies()
        return {"missing": missing}

    def clear_cache(self) -> None:
        """Clear all caches."""
        self._modules_cache.clear()
        self._settings_cache.clear()
        self.scanner.clear_cache()

    def _import_module_file(self, path: Path, module_name: str) -> Any:
        """Import a Python file as a module."""
        import importlib.util
        import sys

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec for {path}")

        module = importlib.util.module_from_spec(spec)

        # Add parent paths for imports
        parent_path = str(path.parent.parent.parent)
        project_root = str(path.parent.parent.parent.parent)

        for p in [parent_path, project_root]:
            if p not in sys.path:
                sys.path.insert(0, p)

        try:
            spec.loader.exec_module(module)
        finally:
            for p in [parent_path, project_root]:
                if p in sys.path:
                    sys.path.remove(p)

        return module
