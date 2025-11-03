#!/usr/bin/env python
"""
Centrifugo dependency checker.

Validates that all required dependencies for Centrifugo are installed.
Provides beautiful Rich-formatted error messages with installation instructions.
"""

from __future__ import annotations

import importlib.util
import os
from typing import Dict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table


class CentrifugoDependencyError(ImportError):
    """Raised when required Centrifugo dependencies are missing."""
    pass


class DependencyChecker:
    """
    Check and validate Centrifugo dependencies.

    Required dependencies:
    - cent: Python client for Centrifugo
    - httpx: HTTP client for async requests (included in django-cfg core)

    Optional dependencies:
    - redis: Redis backend for real-time messaging
    - websockets: WebSocket protocol implementation
    """

    # Required dependencies (httpx is already in django-cfg core dependencies)
    REQUIRED_DEPS = {
        "cent": "cent>=5.0.0",
        "httpx": "httpx>=0.28.0",  # Already in core, but verify it's available
    }

    # Optional dependencies
    OPTIONAL_DEPS = {
        "redis": "redis>=6.4.0",
        "websockets": "websockets>=13.0",
    }

    # Package descriptions
    DESCRIPTIONS = {
        "cent": "Python client for Centrifugo",
        "httpx": "HTTP client for async requests (included in django-cfg)",
        "redis": "Redis backend for real-time messaging",
        "websockets": "WebSocket protocol implementation",
    }

    @classmethod
    def check_package(cls, package_name: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: Python package name (import name)

        Returns:
            True if installed, False otherwise
        """
        return importlib.util.find_spec(package_name) is not None

    @classmethod
    def check_all(cls, raise_on_missing: bool = True) -> Dict[str, bool]:
        """
        Check all Centrifugo dependencies.

        Args:
            raise_on_missing: If True, raise exception when required deps missing

        Returns:
            Dictionary mapping package names to availability status

        Raises:
            CentrifugoDependencyError: If required dependencies are missing and raise_on_missing=True
        """
        status = {}

        # Check required dependencies
        for package_name in cls.REQUIRED_DEPS:
            status[package_name] = cls.check_package(package_name)

        # Check optional dependencies
        for package_name in cls.OPTIONAL_DEPS:
            status[package_name] = cls.check_package(package_name)

        # Check if any required dependencies are missing
        missing_required = [
            pkg for pkg in cls.REQUIRED_DEPS if not status.get(pkg, False)
        ]

        missing_optional = [
            pkg for pkg in cls.OPTIONAL_DEPS if not status.get(pkg, False)
        ]

        if missing_required and raise_on_missing:
            cls._raise_missing_error(missing_required, missing_optional)

        return status

    @classmethod
    def _raise_missing_error(
        cls,
        missing_required: list[str],
        missing_optional: list[str],
    ) -> None:
        """
        Raise a formatted error for missing dependencies.

        Args:
            missing_required: List of missing required packages
            missing_optional: List of missing optional packages
        """
        console = Console()

        # Header
        console.print()
        console.print(Panel(
            "[bold red]MISSING CENTRIFUGO DEPENDENCIES[/bold red]",
            expand=True,
        ))
        console.print()
        console.print("Django-CFG's Centrifugo integration requires additional dependencies")
        console.print()

        # Required dependencies table
        if missing_required:
            table = Table(title="📦 REQUIRED Dependencies (Missing)", show_header=True)
            table.add_column("Package", style="cyan")
            table.add_column("Description", style="white")

            for pkg in missing_required:
                pip_name = cls.REQUIRED_DEPS[pkg].split(">=")[0]
                desc = cls.DESCRIPTIONS.get(pkg, "")
                table.add_row(f"❌ {pip_name}", desc)

            console.print(table)
            console.print()

        # Optional dependencies table
        if missing_optional:
            table = Table(title="📦 OPTIONAL Dependencies (Recommended)", show_header=True)
            table.add_column("Package", style="cyan")
            table.add_column("Description", style="white")

            for pkg in missing_optional:
                pip_name = cls.OPTIONAL_DEPS[pkg].split(">=")[0]
                desc = cls.DESCRIPTIONS.get(pkg, "")
                table.add_row(f"⚠️  {pip_name}", desc)

            console.print(table)
            console.print()

        # Installation instructions
        pkg_manager = _detect_package_manager()

        if pkg_manager == "poetry":
            console.print(Panel(
                "[bold green]🔧 HOW TO FIX (POETRY)[/bold green]\n\n"
                "Install all dependencies (RECOMMENDED)\n\n"
                "[cyan]poetry add django-cfg[centrifugo][/cyan]",
                expand=False,
            ))
            console.print()
            console.print(Panel(
                "Or install manually:\n\n"
                "[cyan]poetry add cent httpx[/cyan]\n\n"
                "Optional:\n"
                "[dim]poetry add redis websockets[/dim]",
                expand=False,
            ))
        else:  # pip
            console.print(Panel(
                "[bold green]🔧 HOW TO FIX (PIP)[/bold green]\n\n"
                "Install all dependencies (RECOMMENDED)\n\n"
                "[cyan]pip install django-cfg[centrifugo][/cyan]",
                expand=False,
            ))
            console.print()
            console.print(Panel(
                "Or install manually:\n\n"
                "[cyan]pip install cent httpx[/cyan]\n\n"
                "Optional:\n"
                "[dim]pip install redis websockets[/dim]",
                expand=False,
            ))

        console.print()
        console.print(Panel(
            "[bold]📚 MORE INFORMATION[/bold]\n\n"
            "Documentation: https://djangocfg.com/centrifugo\n"
            "Report Issues: https://github.com/django-cfg/django-cfg/issues",
            title="📚 MORE INFORMATION",
            expand=False,
        ))
        console.print()

        raise CentrifugoDependencyError("Centrifugo dependencies are missing. See details above.")

    @classmethod
    def print_status(cls) -> None:
        """Print dependency status in a nice table."""
        console = Console()
        status = cls.check_all(raise_on_missing=False)

        table = Table(title="Centrifugo Dependency Status", show_header=True)
        table.add_column("Package", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("Type", style="white")

        # Required dependencies
        for pkg, spec in cls.REQUIRED_DEPS.items():
            pip_name = spec.split(">=")[0]
            status_str = "✅ Installed" if status.get(pkg, False) else "❌ Missing"
            table.add_row(pip_name, status_str, "Required")

        # Optional dependencies
        for pkg, spec in cls.OPTIONAL_DEPS.items():
            pip_name = spec.split(">=")[0]
            status_str = "✅ Installed" if status.get(pkg, False) else "⚠️  Missing"
            table.add_row(pip_name, status_str, "Optional")

        console.print(table)


def _detect_package_manager() -> str:
    """
    Detect which package manager is being used.

    Returns:
        'poetry' if poetry.lock exists, 'pip' otherwise
    """
    current = os.getcwd()

    # Check up to 5 parent directories for poetry.lock
    for _ in range(5):
        if os.path.exists(os.path.join(current, 'poetry.lock')):
            return 'poetry'

        parent = os.path.dirname(current)
        if parent == current:  # Reached root
            break
        current = parent

    return 'pip'


def check_centrifugo_available() -> bool:
    """
    Lightweight check if Centrifugo is available.

    Returns:
        True if all required Centrifugo dependencies are installed
    """
    try:
        status = DependencyChecker.check_all(raise_on_missing=False)
        required_deps = ['cent', 'httpx']
        return all(status.get(dep, False) for dep in required_deps)
    except Exception:
        # Fallback to simple import check
        try:
            import cent  # noqa: F401
            import httpx  # noqa: F401
            return True
        except ImportError:
            return False


def require_centrifugo_feature() -> None:
    """
    Require Centrifugo dependencies with detailed error message.

    Raises:
        ImportError: If required dependencies are missing
    """
    try:
        if not check_centrifugo_available():
            DependencyChecker.check_all(raise_on_missing=True)
    except CentrifugoDependencyError as e:
        raise ImportError(str(e)) from e


def check_centrifugo_dependencies(raise_on_missing: bool = True) -> Dict[str, bool]:
    """
    Check Centrifugo dependencies and optionally raise if missing.

    Args:
        raise_on_missing: If True, raise exception when required deps missing

    Returns:
        Dictionary mapping package names to availability status

    Raises:
        CentrifugoDependencyError: If dependencies missing and raise_on_missing=True
    """
    return DependencyChecker.check_all(raise_on_missing=raise_on_missing)


def print_dependency_status() -> None:
    """Print Centrifugo dependency status table."""
    DependencyChecker.print_status()
