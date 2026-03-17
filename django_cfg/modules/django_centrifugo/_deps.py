"""
django_centrifugo dependency checker.

Validates that all required dependencies for Centrifugo are installed.
Provides Rich-formatted error messages with installation instructions.
"""

from __future__ import annotations

import importlib.util
import os
from typing import Dict


class CentrifugoDependencyError(ImportError):
    """Raised when required Centrifugo dependencies are missing."""
    pass


class DependencyChecker:
    """Check and validate Centrifugo dependencies."""

    REQUIRED_DEPS = {
        "httpx": "httpx>=0.28.0",
    }

    OPTIONAL_DEPS = {
        "cent":       "cent>=5.0.0",
        "redis":      "redis>=6.4.0",
        "websockets": "websockets>=13.0",
    }

    DESCRIPTIONS = {
        "httpx":      "HTTP client for async requests (included in django-cfg)",
        "cent":       "Python client for Centrifugo",
        "redis":      "Redis backend for real-time messaging",
        "websockets": "WebSocket protocol implementation",
    }

    @classmethod
    def check_package(cls, package_name: str) -> bool:
        return importlib.util.find_spec(package_name) is not None

    @classmethod
    def check_all(cls, raise_on_missing: bool = True) -> Dict[str, bool]:
        status = {}
        for pkg in cls.REQUIRED_DEPS:
            status[pkg] = cls.check_package(pkg)
        for pkg in cls.OPTIONAL_DEPS:
            status[pkg] = cls.check_package(pkg)

        missing_required = [p for p in cls.REQUIRED_DEPS if not status.get(p, False)]
        missing_optional = [p for p in cls.OPTIONAL_DEPS if not status.get(p, False)]

        if missing_required and raise_on_missing:
            cls._raise_missing_error(missing_required, missing_optional)

        return status

    @classmethod
    def _raise_missing_error(
        cls,
        missing_required: list[str],
        missing_optional: list[str],
    ) -> None:
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table

            console = Console()
            console.print()
            console.print(Panel("[bold red]MISSING Centrifugo DEPENDENCIES[/bold red]", expand=True))
            console.print()

            if missing_required:
                table = Table(title="Required Dependencies (Missing)", show_header=True)
                table.add_column("Package", style="cyan")
                table.add_column("Description", style="white")
                for pkg in missing_required:
                    pip_name = cls.REQUIRED_DEPS[pkg].split(">=")[0]
                    table.add_row(f"[red]{pip_name}[/red]", cls.DESCRIPTIONS.get(pkg, ""))
                console.print(table)
                console.print()

            pkg_manager = _detect_package_manager()
            install_cmd = "poetry add" if pkg_manager == "poetry" else "pip install"
            console.print(Panel(
                f"[bold green]HOW TO FIX[/bold green]\n\n"
                f"[cyan]{install_cmd} django-cfg[centrifugo][/cyan]\n\n"
                f"Or manually:\n[cyan]{install_cmd} httpx cent[/cyan]",
                expand=False,
            ))
            console.print()
        except ImportError:
            pass  # Rich not available — plain error below

        raise CentrifugoDependencyError(
            "Centrifugo dependencies are missing. Install: pip install django-cfg[centrifugo]"
        )

    @classmethod
    def print_status(cls) -> None:
        try:
            from rich.console import Console
            from rich.table import Table

            console = Console()
            status = cls.check_all(raise_on_missing=False)
            table = Table(title="Centrifugo Dependency Status", show_header=True)
            table.add_column("Package", style="cyan")
            table.add_column("Status")
            table.add_column("Type")
            for pkg, spec in cls.REQUIRED_DEPS.items():
                pip_name = spec.split(">=")[0]
                s = "✅ Installed" if status.get(pkg) else "❌ Missing"
                table.add_row(pip_name, s, "Required")
            for pkg, spec in cls.OPTIONAL_DEPS.items():
                pip_name = spec.split(">=")[0]
                s = "✅ Installed" if status.get(pkg) else "⚠️  Missing"
                table.add_row(pip_name, s, "Optional")
            console.print(table)
        except ImportError:
            status = cls.check_all(raise_on_missing=False)
            for pkg, ok in status.items():
                print(f"{'OK' if ok else 'MISSING'}: {pkg}")


def _detect_package_manager() -> str:
    current = os.getcwd()
    for _ in range(5):
        if os.path.exists(os.path.join(current, "poetry.lock")):
            return "poetry"
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return "pip"


def check_centrifugo_available() -> bool:
    """Lightweight check — returns True if all required Centrifugo deps are installed."""
    try:
        status = DependencyChecker.check_all(raise_on_missing=False)
        return all(status.get(dep, False) for dep in DependencyChecker.REQUIRED_DEPS)
    except Exception:
        try:
            import httpx  # noqa: F401
            return True
        except ImportError:
            return False


def require_centrifugo_feature() -> None:
    """Raise ImportError with detailed instructions if Centrifugo deps are missing."""
    try:
        if not check_centrifugo_available():
            DependencyChecker.check_all(raise_on_missing=True)
    except CentrifugoDependencyError as exc:
        raise ImportError(str(exc)) from exc


__all__ = [
    "CentrifugoDependencyError",
    "DependencyChecker",
    "check_centrifugo_available",
    "require_centrifugo_feature",
]
