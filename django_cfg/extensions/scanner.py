"""
Extension Scanner

Scans the extensions/ folder in user's project and discovers extensions.
"""

import importlib.util
import sys
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field

from django_cfg.utils import get_logger

from .manifest import ExtensionManifest

logger = get_logger(__name__)


class DiscoveredExtension(BaseModel):
    """Represents a discovered extension with its metadata."""

    name: str = Field(..., description="Extension name (folder name)")
    type: str = Field(..., description="'app' or 'module'")
    path: Path = Field(..., description="Absolute path to extension folder")
    manifest: Optional[ExtensionManifest] = Field(
        default=None, description="Parsed manifest if valid"
    )
    is_valid: bool = Field(default=True, description="Whether extension is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")

    model_config = {"arbitrary_types_allowed": True}


class ExtensionScanner:
    """
    Scans extensions/ folder in user's project and discovers extensions.

    Reads extension configuration from config.py (preferred) or __manifest__.py (fallback).

    Usage:
        scanner = ExtensionScanner(base_path=Path("/path/to/project"))
        extensions = scanner.discover_all()
        for ext in extensions:
            print(f"{ext.name}: {ext.type}, valid={ext.is_valid}")
    """

    EXTENSIONS_DIR = "extensions"
    APPS_SUBDIR = "apps"
    MODULES_SUBDIR = "modules"
    CONFIG_FILE = "__cfg__.py"
    MANIFEST_FILE = "__manifest__.py"  # legacy fallback

    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize scanner.

        Args:
            base_path: Project root path. If None, uses current working directory.
        """
        self.base_path = base_path or Path.cwd()
        self.extensions_path = self.base_path / self.EXTENSIONS_DIR
        self._cache: Optional[List[DiscoveredExtension]] = None

    def discover_all(self, use_cache: bool = True) -> List[DiscoveredExtension]:
        """
        Discover all extensions in the project.

        Args:
            use_cache: If True, returns cached results if available.

        Returns:
            List of discovered extensions.
        """
        if use_cache and self._cache is not None:
            return self._cache

        extensions: List[DiscoveredExtension] = []

        if not self.extensions_path.exists():
            logger.debug(f"Extensions directory not found: {self.extensions_path}")
            self._cache = extensions
            return extensions

        # Scan apps/
        apps_path = self.extensions_path / self.APPS_SUBDIR
        if apps_path.exists() and apps_path.is_dir():
            for item in apps_path.iterdir():
                if self._is_valid_extension_dir(item):
                    ext = self._scan_extension(item, "app")
                    extensions.append(ext)

        # Scan modules/
        modules_path = self.extensions_path / self.MODULES_SUBDIR
        if modules_path.exists() and modules_path.is_dir():
            for item in modules_path.iterdir():
                if self._is_valid_extension_dir(item):
                    ext = self._scan_extension(item, "module")
                    extensions.append(ext)

        # Sort by dependencies (topological sort)
        extensions = self._sort_by_dependencies(extensions)

        self._cache = extensions
        return extensions

    def discover_apps(self) -> List[DiscoveredExtension]:
        """Discover only app extensions."""
        return [ext for ext in self.discover_all() if ext.type == "app"]

    def discover_modules(self) -> List[DiscoveredExtension]:
        """Discover only module extensions."""
        return [ext for ext in self.discover_all() if ext.type == "module"]

    def get_extension(self, name: str) -> Optional[DiscoveredExtension]:
        """Get a specific extension by name."""
        for ext in self.discover_all():
            if ext.name == name:
                return ext
        return None

    def clear_cache(self) -> None:
        """Clear the discovery cache."""
        self._cache = None

    def _is_valid_extension_dir(self, path: Path) -> bool:
        """Check if a directory is a valid extension directory."""
        if not path.is_dir():
            return False
        if path.name.startswith("_") or path.name.startswith("."):
            return False
        if path.name == "__pycache__":
            return False
        return True

    def _scan_extension(self, path: Path, ext_type: str) -> DiscoveredExtension:
        """Scan a single extension directory."""
        errors: List[str] = []
        manifest: Optional[ExtensionManifest] = None

        # Try to load from config.py first (preferred)
        config_path = path / self.CONFIG_FILE
        manifest_path = path / self.MANIFEST_FILE

        if config_path.exists():
            try:
                manifest = self._load_from_config(config_path)
            except Exception as e:
                logger.debug(f"Failed to load config.py for {path.name}: {e}")
                # Fallback to __manifest__.py
                if manifest_path.exists():
                    try:
                        manifest = self._load_manifest(manifest_path)
                    except Exception as e2:
                        errors.append(f"Failed to load config: {e}, manifest: {e2}")
                else:
                    errors.append(f"Failed to load config.py: {e}")
        elif manifest_path.exists():
            # Fallback: load from __manifest__.py
            try:
                manifest = self._load_manifest(manifest_path)
            except Exception as e:
                errors.append(f"Failed to load manifest: {e}")
        else:
            errors.append(f"Missing {self.CONFIG_FILE} or {self.MANIFEST_FILE}")

        # Validate manifest matches folder
        if manifest:
            if manifest.name != path.name:
                errors.append(
                    f"Extension name '{manifest.name}' doesn't match folder '{path.name}'"
                )
            if manifest.type != ext_type:
                errors.append(
                    f"Extension type '{manifest.type}' doesn't match location '{ext_type}'"
                )

        # Check for required files based on type
        if ext_type == "app":
            if not (path / "apps.py").exists() and not (path / "__init__.py").exists():
                errors.append("App extension should have apps.py or __init__.py")

        return DiscoveredExtension(
            name=path.name,
            type=ext_type,
            path=path,
            manifest=manifest,
            is_valid=len(errors) == 0 and manifest is not None,
            errors=errors,
        )

    def _load_from_config(self, config_path: Path) -> ExtensionManifest:
        """
        Load manifest from config.py via settings.to_manifest().

        Args:
            config_path: Path to config.py

        Returns:
            ExtensionManifest instance
        """
        spec = importlib.util.spec_from_file_location(
            f"_config_{config_path.parent.name}",
            config_path,
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec for {config_path}")

        module = importlib.util.module_from_spec(spec)

        # Add paths for imports
        parent_path = str(config_path.parent.parent.parent)
        if parent_path not in sys.path:
            sys.path.insert(0, parent_path)

        try:
            spec.loader.exec_module(module)
        finally:
            if parent_path in sys.path:
                sys.path.remove(parent_path)

        # Get settings object and convert to manifest
        settings = getattr(module, "settings", None)
        if settings is None:
            raise ValueError("config.py must export 'settings' variable")

        # Check for to_manifest method
        if hasattr(settings, "to_manifest"):
            return settings.to_manifest()
        else:
            raise TypeError("settings must have to_manifest() method")

    def _load_manifest(self, manifest_path: Path) -> ExtensionManifest:
        """
        Dynamically load and parse a manifest file (fallback).

        Args:
            manifest_path: Path to __manifest__.py

        Returns:
            ExtensionManifest instance
        """
        spec = importlib.util.spec_from_file_location(
            f"_manifest_{manifest_path.parent.name}",
            manifest_path,
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load spec for {manifest_path}")

        module = importlib.util.module_from_spec(spec)

        # Temporarily add parent to path for relative imports
        parent_path = str(manifest_path.parent.parent.parent)
        if parent_path not in sys.path:
            sys.path.insert(0, parent_path)

        try:
            spec.loader.exec_module(module)
        finally:
            # Clean up sys.path
            if parent_path in sys.path:
                sys.path.remove(parent_path)

        # Get the manifest object
        manifest = getattr(module, "manifest", None)
        if manifest is None:
            raise ValueError("Manifest file must export 'manifest' variable")

        if isinstance(manifest, ExtensionManifest):
            return manifest
        elif isinstance(manifest, dict):
            return ExtensionManifest(**manifest)
        else:
            raise TypeError(
                f"manifest must be ExtensionManifest or dict, got {type(manifest)}"
            )

    def _sort_by_dependencies(
        self, extensions: List[DiscoveredExtension]
    ) -> List[DiscoveredExtension]:
        """
        Sort extensions by dependencies using topological sort.

        Extensions with dependencies will be loaded after their dependencies.
        """
        if not extensions:
            return extensions

        # Build dependency graph
        name_to_ext = {ext.name: ext for ext in extensions}
        sorted_list: List[DiscoveredExtension] = []
        visited: set = set()
        temp_visited: set = set()

        def visit(ext: DiscoveredExtension) -> None:
            if ext.name in temp_visited:
                logger.warning(f"Circular dependency detected for {ext.name}")
                return
            if ext.name in visited:
                return

            temp_visited.add(ext.name)

            # Visit dependencies first
            if ext.manifest and ext.manifest.requires:
                for dep_name in ext.manifest.requires:
                    if dep_name in name_to_ext:
                        visit(name_to_ext[dep_name])
                    else:
                        logger.warning(
                            f"Extension {ext.name} requires {dep_name}, but it's not installed"
                        )

            temp_visited.remove(ext.name)
            visited.add(ext.name)
            sorted_list.append(ext)

        for ext in extensions:
            if ext.name not in visited:
                visit(ext)

        return sorted_list
