"""
URL module discovery for Django apps.

Discovers urls.py and urls_*.py files for any Django app using
find_spec() (safe, no imports triggered).

Convention:
- urls.py        -> main API (no suffix)
- urls_public.py -> /public/ suffix
- urls_admin.py  -> /admin/ suffix
- urls_<name>.py -> /<name>/ suffix
"""

import glob
import importlib.util
import os
from typing import List, Tuple


def discover_app_url_modules(app_name: str) -> List[Tuple[str, str]]:
    """
    Discover urls.py and urls_*.py for a Django app.

    Uses find_spec() + filesystem glob — safe, does not trigger imports.

    Args:
        app_name: Dotted app name, e.g. "apps.business.payments"

    Returns:
        List of (module_name, url_suffix) tuples, e.g.:
            [("apps.business.payments.urls", ""),
             ("apps.business.payments.urls_public", "public")]
        Empty list if no urls.py found.
    """
    modules: List[Tuple[str, str]] = []

    # Check if urls.py exists
    main_mod = f"{app_name}.urls"
    try:
        main_spec = importlib.util.find_spec(main_mod)
    except (ModuleNotFoundError, ValueError):
        main_spec = None

    if main_spec is None:
        return modules

    modules.append((main_mod, ""))

    # Look for urls_*.py siblings via filesystem
    if main_spec.origin:
        app_dir = os.path.dirname(main_spec.origin)
        for filepath in glob.glob(os.path.join(app_dir, "urls_*.py")):
            filename = os.path.basename(filepath)
            if filename.startswith("__"):
                continue

            # urls_public.py -> module "urls_public", suffix "public"
            module_stem = filename[:-3]  # Remove .py
            suffix = module_stem[5:]  # Remove "urls_"
            full_module = f"{app_name}.{module_stem}"

            # Verify importable
            try:
                spec = importlib.util.find_spec(full_module)
            except (ModuleNotFoundError, ValueError):
                spec = None

            if spec is not None:
                modules.append((full_module, suffix))

    return modules
