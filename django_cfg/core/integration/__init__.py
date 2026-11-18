"""
Django CFG Integration Package.

Provides URL integration and startup information display.
"""

import os

from .display.startup import StartupDisplayManager
from .url_integration import add_django_cfg_urls, get_django_cfg_urls_info

# Module-level flag that persists across hot reloads
_startup_info_shown = False

#: Opt-in switch that restores the verbose startup block (``1``/``true``/``yes``/``on``).
ENV_BANNER = "DJANGO_CFG_BANNER"

from django_cfg.core.utils.runtime_paths import (  # noqa: E402
    DEV_SERVER_COMMANDS,
    is_dev_server_command,
)


def _truthy(value) -> bool:
    return str(value or "").strip().lower() in ("1", "true", "yes", "on")


def banner_requested(config=None) -> bool:
    """True when the verbose startup block was asked for (env ``DJANGO_CFG_BANNER`` or ``config.startup_banner``)."""
    if _truthy(os.environ.get(ENV_BANNER)):
        return True
    return bool(getattr(config, "startup_banner", False))


def print_startup_info():
    """
    Print startup information.

    Default: nothing, except ONE short line (``django-cfg <ver> . <project> . <env>``) for a
    development server on a terminal. Tests, ``shell``, ``migrate``, gunicorn/daphne workers and
    containers (no TTY) stay silent. ``DJANGO_CFG_BANNER=1`` (or ``DjangoConfig.startup_banner``)
    restores the verbose block selected by ``config.startup_info_mode``.
    """
    global _startup_info_shown

    # Skip if already shown (prevents spam on hot reload)
    if _startup_info_shown:
        return

    # Only show in the actual worker process (not in autoreload parent process)
    # RUN_MAIN is set by Django's autoreloader in the worker process (absent with --noreload)
    import sys

    if os.environ.get('RUN_MAIN') != 'true' and '--noreload' not in sys.argv:
        return

    manager = StartupDisplayManager()
    config = manager.config
    verbose = banner_requested(config)

    if not verbose:
        if not is_dev_server_command():
            return
        try:
            if not sys.stdout.isatty():
                return
        except Exception:
            return

    # Mark as shown to prevent duplicate display on subsequent hot reloads
    _startup_info_shown = True

    if verbose:
        manager.display_startup_info()
    else:
        manager.display_one_line()

def reset_startup_info_flag():
    """Reset the startup info display flag. Useful for testing or manual reset."""
    global _startup_info_shown
    _startup_info_shown = False

from .commands_collector import get_all_commands, get_command_count, get_commands_with_descriptions
from .timing import (
    ServerStartupTimer,
    get_django_startup_time,
    get_django_timer,
    start_django_timer,
)
from .version_checker import get_current_version, get_latest_version, get_version_info

__all__ = [
    "add_django_cfg_urls",
    "get_django_cfg_urls_info",
    "print_startup_info",
    "banner_requested",
    "is_dev_server_command",
    "reset_startup_info_flag",
    "get_version_info",
    "get_latest_version",
    "get_current_version",
    "get_all_commands",
    "get_command_count",
    "get_commands_with_descriptions",
    # Timing utilities
    "ServerStartupTimer",
    "start_django_timer",
    "get_django_timer",
    "get_django_startup_time",
]
