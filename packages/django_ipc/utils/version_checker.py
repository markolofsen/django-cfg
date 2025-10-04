"""
Version checker for django-ipc.

Checks if the installed version is up-to-date and displays warnings using rich.
"""

import sys
from importlib.metadata import version as get_version
from typing import Optional

try:
    from packaging.version import Version
except ImportError:
    # Fallback for systems without packaging
    Version = None  # type: ignore

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


# Latest version - update this when releasing new version
LATEST_VERSION = "1.0.0"
PYPI_URL = "https://pypi.org/project/django-ipc/"


def get_current_version() -> str:
    """Get current installed version of django-ipc."""
    try:
        return get_version("django-ipc")
    except Exception:
        return "unknown"


def get_server_version() -> str:
    """
    Get server version for sending to clients.

    Alias for get_current_version() with better naming for server context.
    """
    return get_current_version()


def parse_version(version_str: str) -> Optional["Version"]:
    """Parse version string to Version object."""
    if Version is None:
        return None

    try:
        return Version(version_str)
    except Exception:
        return None


def is_outdated(current: str, latest: str) -> bool:
    """Check if current version is outdated."""
    if current == "unknown" or latest == "unknown":
        return False

    current_ver = parse_version(current)
    latest_ver = parse_version(latest)

    if current_ver is None or latest_ver is None:
        # Fallback to string comparison
        return current < latest

    return current_ver < latest_ver


def check_version(silent: bool = False) -> bool:
    """
    Check if django-ipc is up-to-date.

    Args:
        silent: If True, don't print anything

    Returns:
        True if up-to-date, False if outdated
    """
    current_version = get_current_version()

    if current_version == "unknown":
        return True  # Don't warn if we can't determine version

    outdated = is_outdated(current_version, LATEST_VERSION)

    if outdated and not silent:
        display_update_warning(current_version, LATEST_VERSION)

    return not outdated


def display_update_warning(current: str, latest: str) -> None:
    """Display update warning using rich or plain text."""
    if HAS_RICH:
        _display_rich_warning(current, latest)
    else:
        _display_plain_warning(current, latest)


def _display_rich_warning(current: str, latest: str) -> None:
    """Display rich formatted update warning."""
    console = Console()

    message = Text()
    message.append("⚠️  ", style="bold yellow")
    message.append("django-ipc is outdated!\n\n", style="bold yellow")
    message.append("Current version: ", style="dim")
    message.append(f"{current}\n", style="red bold")
    message.append("Latest version:  ", style="dim")
    message.append(f"{latest}\n\n", style="green bold")
    message.append("Update with: ", style="dim")
    message.append("pip install --upgrade django-ipc", style="cyan bold")

    panel = Panel(
        message,
        title="[bold red]Update Available[/bold red]",
        border_style="yellow",
        expand=False,
    )

    console.print()
    console.print(panel)
    console.print()


def _display_plain_warning(current: str, latest: str) -> None:
    """Display plain text update warning."""
    print()
    print("=" * 70)
    print("⚠️  django-ipc is outdated!")
    print("=" * 70)
    print(f"Current version: {current}")
    print(f"Latest version:  {latest}")
    print()
    print(f"Update with: pip install --upgrade django-ipc")
    print(f"PyPI: {PYPI_URL}")
    print("=" * 70)
    print()


def display_startup_banner() -> None:
    """Display startup banner with version info."""
    current_version = get_current_version()

    if not HAS_RICH:
        print(f"django-ipc v{current_version}")
        return

    console = Console()

    # Check if outdated
    outdated = is_outdated(current_version, LATEST_VERSION)

    if outdated:
        version_text = Text(f"v{current_version}", style="red bold")
        version_text.append(" (outdated)", style="yellow")
    else:
        version_text = Text(f"v{current_version}", style="green bold")

    banner = Text()
    banner.append("🚀 ", style="bold")
    banner.append("django-ipc ", style="bold cyan")
    banner.append(version_text)

    console.print()
    console.print(banner)

    if outdated:
        console.print(
            f"   Latest: [green bold]{LATEST_VERSION}[/green bold] "
            f"([dim]pip install --upgrade django-ipc[/dim])",
            style="dim"
        )

    console.print()


__all__ = [
    "check_version",
    "display_update_warning",
    "display_startup_banner",
    "get_current_version",
    "is_outdated",
]
