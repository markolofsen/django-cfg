"""
Extension URL Discovery and Registration

Auto-discovers all urls*.py files in extension apps and provides
URL patterns for integration with Django's URL routing.

Convention:
- urls.py -> /cfg/{prefix}/ (main API)
- urls_admin.py -> /cfg/{prefix}/admin/ (admin API)
- urls_system.py -> /cfg/{prefix}/system/ (system API)
- urls_<name>.py -> /cfg/{prefix}/<name>/ (custom suffix)
"""

import glob
import importlib
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

from django_cfg.utils import get_logger

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver

logger = get_logger(__name__)


def discover_url_modules(
    extension_name: str,
    extension_type: str,
    base_dir: Optional[Path] = None,
) -> List[Tuple[str, str, str]]:
    """
    Discover all urls*.py files in an extension directory.

    Convention:
    - urls.py -> main prefix (no suffix)
    - urls_admin.py -> /admin/ suffix
    - urls_system.py -> /system/ suffix
    - urls_<name>.py -> /<name>/ suffix

    Args:
        extension_name: Extension name (e.g., "knowbase")
        extension_type: Extension type ("app" or "module")
        base_dir: Project root path. If None, uses current config.

    Returns:
        List of (url_module, url_suffix, namespace_suffix) tuples
        e.g., [
            ("extensions.apps.knowbase.urls", "", ""),
            ("extensions.apps.knowbase.urls_admin", "admin", "_admin"),
            ("extensions.apps.knowbase.urls_system", "system", "_system"),
        ]
    """
    if base_dir is None:
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        if not config:
            return []
        base_dir = Path(config.base_dir)

    # Build filesystem path
    if extension_type == "app":
        fs_path = base_dir / "extensions" / "apps" / extension_name
        module_base = f"extensions.apps.{extension_name}"
    else:
        fs_path = base_dir / "extensions" / "modules" / extension_name
        module_base = f"extensions.modules.{extension_name}"

    modules = []

    # Find all urls*.py files
    pattern = str(fs_path / "urls*.py")
    for filepath in glob.glob(pattern):
        filename = os.path.basename(filepath)

        # Skip __pycache__ and other special files
        if filename.startswith("__"):
            continue

        # Parse filename: urls.py or urls_<suffix>.py
        if filename == "urls.py":
            suffix = ""
            namespace_suffix = ""
        else:
            # urls_admin.py -> admin
            name_part = filename[5:-3]  # Remove "urls_" and ".py"
            suffix = name_part
            namespace_suffix = f"_{name_part}"

        module_name = filename[:-3]  # Remove .py
        url_module = f"{module_base}.{module_name}"

        modules.append((url_module, suffix, namespace_suffix))

    return modules


def get_extension_url_patterns(
    url_prefix: str = "cfg",
    base_dir: Optional[Path] = None,
    filter_extension: Optional[str] = None,
) -> List["URLPattern | URLResolver"]:
    """
    Get URL patterns for all discovered extensions.

    Auto-discovers all urls*.py files in each extension and registers them:
    - urls.py -> /{prefix}/{ext.url_prefix}/
    - urls_admin.py -> /{prefix}/{ext.url_prefix}/admin/
    - urls_system.py -> /{prefix}/{ext.url_prefix}/system/

    Args:
        url_prefix: URL prefix for all extensions (default: "cfg")
        base_dir: Project root path. If None, uses current config.

    Returns:
        List of URL patterns ready for urlpatterns.extend()
    """
    from django.urls import include, path

    from django_cfg.extensions import get_extension_loader

    if base_dir is None:
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        if not config:
            return []
        base_dir = Path(config.base_dir)

    patterns: List = []
    loader = get_extension_loader(base_path=base_dir)
    extensions = loader.scanner.discover_all()

    for ext in extensions:
        if not ext.manifest or not ext.manifest.url_prefix:
            continue

        ext_url_prefix = ext.manifest.url_prefix.strip('/')
        base_namespace = ext.manifest.url_namespace or ext.name

        # Discover all urls*.py files for this extension
        url_modules = discover_url_modules(ext.name, ext.type, base_dir)

        if not url_modules:
            logger.debug(f"Extension '{ext.name}' has no urls*.py files")
            continue

        # Register each URL module
        for url_module, suffix, namespace_suffix in url_modules:
            try:
                importlib.import_module(url_module)

                # Build URL path and namespace
                if suffix:
                    url_path = f"{url_prefix}/{ext_url_prefix}/{suffix}/"
                    namespace = f"{base_namespace}{namespace_suffix}"
                else:
                    url_path = f"{url_prefix}/{ext_url_prefix}/"
                    namespace = base_namespace

                patterns.append(
                    path(url_path, include(url_module, namespace=namespace))
                )

                # Log successful registration
                sys.stderr.write(f"✅ Auto-registered Extension URL: /{url_path} -> {url_module}\n")
                sys.stderr.flush()

            except ImportError as e:
                sys.stderr.write(f"⚠️  Failed to import {url_module}: {e}\n")
                sys.stderr.flush()
            except Exception as e:
                sys.stderr.write(f"❌ Error registering {url_module}: {e}\n")
                sys.stderr.flush()

    return patterns


def print_extension_urls() -> None:
    """Print all discovered extension URLs to console (for debugging)."""
    from django_cfg.core.state import get_current_config
    from django_cfg.extensions import get_extension_loader

    config = get_current_config()
    if not config:
        print("No Django-CFG config found")
        return

    base_dir = Path(config.base_dir)
    loader = get_extension_loader(base_path=base_dir)
    extensions = loader.scanner.discover_all()

    print("\n=== Extension URLs ===\n")

    for ext in extensions:
        if not ext.manifest or not ext.manifest.url_prefix:
            print(f"  {ext.name}: (no url_prefix)")
            continue

        print(f"  {ext.name}:")
        url_modules = discover_url_modules(ext.name, ext.type, base_dir)

        if not url_modules:
            print(f"    └── (no urls*.py files)")
        else:
            for url_module, suffix, _ in url_modules:
                if suffix:
                    url_path = f"/cfg/{ext.manifest.url_prefix}/{suffix}/"
                else:
                    url_path = f"/cfg/{ext.manifest.url_prefix}/"
                print(f"    └── {url_path} -> {url_module}")

    print()
