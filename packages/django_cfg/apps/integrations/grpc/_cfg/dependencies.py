"""
gRPC Dependencies Checker.

Validates that all required gRPC libraries are installed before running the gRPC server.
"""

from __future__ import annotations

import sys
from typing import Dict, List, Tuple


class GRPCDependencyError(Exception):
    """Raised when required gRPC dependencies are missing."""
    pass


class DependencyChecker:
    """
    Checks if all required gRPC dependencies are installed.

    Usage:
        >>> from django_cfg.apps.integrations.grpc.utils.dependencies import check_grpc_dependencies
        >>> check_grpc_dependencies()  # Raises GRPCDependencyError if missing
    """

    # Required dependencies with their import names and package names
    REQUIRED_DEPENDENCIES: List[Tuple[str, str, str]] = [
        ("grpc", "grpcio", "Core gRPC framework"),
        ("grpc_tools", "grpcio-tools", "Protocol Buffer compiler and tools"),
        ("google.protobuf", "protobuf", "Protocol Buffers runtime"),
    ]

    # Optional but recommended dependencies
    OPTIONAL_DEPENDENCIES: List[Tuple[str, str, str]] = [
        ("grpc_reflection", "grpcio-reflection", "Server reflection API (for grpcurl/grpcui)"),
        ("grpc_health", "grpcio-health-checking", "Health check service"),
    ]

    @classmethod
    def check_all(cls, raise_on_missing: bool = True) -> Dict[str, bool]:
        """
        Check all gRPC dependencies.

        Args:
            raise_on_missing: If True, raises GRPCDependencyError when required deps are missing

        Returns:
            Dictionary with dependency status

        Raises:
            GRPCDependencyError: If required dependencies are missing and raise_on_missing=True

        Example:
            >>> status = DependencyChecker.check_all(raise_on_missing=False)
            >>> if not status['grpc']:
            ...     print("gRPC not installed")
        """
        status = {}
        missing_required = []
        missing_optional = []

        # Check required dependencies
        for import_name, package_name, description in cls.REQUIRED_DEPENDENCIES:
            is_available = cls._check_import(import_name)
            status[package_name] = is_available

            if not is_available:
                missing_required.append((package_name, description))

        # Check optional dependencies
        for import_name, package_name, description in cls.OPTIONAL_DEPENDENCIES:
            is_available = cls._check_import(import_name)
            status[package_name] = is_available

            if not is_available:
                missing_optional.append((package_name, description))

        # Raise error if required dependencies are missing
        if missing_required and raise_on_missing:
            cls._raise_missing_error(missing_required, missing_optional)

        return status

    @classmethod
    def _check_import(cls, module_name: str) -> bool:
        """
        Check if a module can be imported.

        Args:
            module_name: Module to import (e.g., "grpc", "google.protobuf")

        Returns:
            True if module can be imported
        """
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False

    @classmethod
    def _detect_package_manager(cls) -> str:
        """
        Detect which package manager is being used.

        Returns:
            'poetry' if poetry.lock exists, 'pip' otherwise
        """
        import os
        # Check for poetry.lock in current dir and parent dirs
        current = os.getcwd()
        for _ in range(5):  # Check up to 5 levels up
            if os.path.exists(os.path.join(current, 'poetry.lock')):
                return 'poetry'
            parent = os.path.dirname(current)
            if parent == current:  # Reached root
                break
            current = parent
        return 'pip'

    @classmethod
    def _raise_missing_error(
        cls,
        missing_required: List[Tuple[str, str]],
        missing_optional: List[Tuple[str, str]]
    ) -> None:
        """
        Raise a detailed error message about missing dependencies using Rich formatting.

        Args:
            missing_required: List of (package_name, description) tuples for required deps
            missing_optional: List of (package_name, description) tuples for optional deps
        """
        # Detect package manager
        pkg_manager = cls._detect_package_manager()

        try:
            # Try to use Rich for beautiful output
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.text import Text

            console = Console()
            console.print()  # Blank line

            # Header
            header = Text("MISSING gRPC DEPENDENCIES", style="bold red")
            console.print(Panel(header, style="red"))

            console.print(
                "\n[yellow]Django-CFG's gRPC integration requires additional dependencies[/yellow]\n"
            )

            # Required dependencies table
            if missing_required:
                table = Table(title="📦 REQUIRED Dependencies (Missing)", style="red")
                table.add_column("Package", style="cyan", no_wrap=True)
                table.add_column("Description", style="white")

                for package_name, description in missing_required:
                    table.add_row(f"❌ {package_name}", description)

                console.print(table)
                console.print()

            # Optional dependencies table
            if missing_optional:
                table = Table(title="📦 OPTIONAL Dependencies (Recommended)", style="yellow")
                table.add_column("Package", style="cyan", no_wrap=True)
                table.add_column("Description", style="white")

                for package_name, description in missing_optional:
                    table.add_row(f"⚠️  {package_name}", description)

                console.print(table)
                console.print()

            # Installation instructions based on detected package manager
            if pkg_manager == 'poetry':
                quick_install = (
                    "[bold green]Install all dependencies (RECOMMENDED)[/bold green]\n\n"
                    "[cyan]poetry add django-cfg[grpc][/cyan]"
                )
            else:
                quick_install = (
                    "[bold green]Install all dependencies (RECOMMENDED)[/bold green]\n\n"
                    "[cyan]pip install django-cfg[grpc][/cyan]"
                )

            console.print(Panel.fit(
                quick_install,
                title=f"🔧 HOW TO FIX ({pkg_manager.upper()})",
                border_style="green"
            ))

            # Manual installation option
            if missing_required or missing_optional:
                console.print()
                manual_install = "[bold]Or install manually:[/bold]\n\n"
                if missing_required:
                    packages = " ".join(pkg for pkg, _ in missing_required)
                    if pkg_manager == 'poetry':
                        manual_install += f"[cyan]poetry add {packages}[/cyan]\n"
                    else:
                        manual_install += f"[cyan]pip install {packages}[/cyan]\n"
                if missing_optional:
                    packages = " ".join(pkg for pkg, _ in missing_optional)
                    manual_install += f"\n# Optional:\n"
                    if pkg_manager == 'poetry':
                        manual_install += f"[dim cyan]poetry add {packages}[/dim cyan]"
                    else:
                        manual_install += f"[dim cyan]pip install {packages}[/dim cyan]"

                console.print(Panel.fit(manual_install, border_style="blue"))

            # Footer
            console.print()
            console.print(Panel.fit(
                "[link=https://djangocfg.com/docs/integrations/grpc]Documentation[/link]\n"
                "[link=https://github.com/markolofsen/django-cfg/issues]Report Issues[/link]",
                title="📚 MORE INFORMATION",
                border_style="blue"
            ))
            console.print()

            # Raise without the message (Rich already printed it)
            raise GRPCDependencyError("gRPC dependencies are missing. See details above.")

        except ImportError:
            # Fallback to plain text if Rich is not available
            error_lines = [
                "",
                "=" * 80,
                "❌ MISSING gRPC DEPENDENCIES",
                "=" * 80,
                "",
                "Django-CFG's gRPC integration requires additional dependencies that are not installed.",
                "",
            ]

            # Required dependencies
            if missing_required:
                error_lines.append("📦 REQUIRED (missing):")
                error_lines.append("")
                for package_name, description in missing_required:
                    error_lines.append(f"  ❌ {package_name:<30} - {description}")
                error_lines.append("")

            # Optional dependencies
            if missing_optional:
                error_lines.append("📦 OPTIONAL (recommended, but missing):")
                error_lines.append("")
                for package_name, description in missing_optional:
                    error_lines.append(f"  ⚠️  {package_name:<30} - {description}")
                error_lines.append("")

            # Installation instructions based on detected package manager
            error_lines.extend([
                "=" * 80,
                f"🔧 HOW TO FIX ({pkg_manager.upper()})",
                "=" * 80,
                "",
                "Install all gRPC dependencies at once (RECOMMENDED):",
                "",
            ])

            if pkg_manager == 'poetry':
                error_lines.append("  poetry add django-cfg[grpc]")
            else:
                error_lines.append("  pip install django-cfg[grpc]")

            error_lines.extend([
                "",
                "Or install manually:",
                "",
            ])

            # Build install command for required
            if missing_required:
                packages = " ".join(pkg for pkg, _ in missing_required)
                if pkg_manager == 'poetry':
                    error_lines.append(f"  poetry add {packages}")
                else:
                    error_lines.append(f"  pip install {packages}")
                error_lines.append("")

            # Build install command for optional
            if missing_optional:
                packages = " ".join(pkg for pkg, _ in missing_optional)
                error_lines.append(f"  # Optional (recommended):")
                if pkg_manager == 'poetry':
                    error_lines.append(f"  poetry add {packages}")
                else:
                    error_lines.append(f"  pip install {packages}")
                error_lines.append("")

            error_lines.extend([
                "=" * 80,
                "📚 MORE INFORMATION",
                "=" * 80,
                "",
                "Documentation: https://djangocfg.com/docs/integrations/grpc",
                "Issues: https://github.com/markolofsen/django-cfg/issues",
                "",
                "=" * 80,
                "",
            ])

            error_message = "\n".join(error_lines)
            raise GRPCDependencyError(error_message)

    @classmethod
    def get_version_info(cls) -> Dict[str, str]:
        """
        Get version information for installed gRPC dependencies.

        Returns:
            Dictionary with package versions

        Example:
            >>> versions = DependencyChecker.get_version_info()
            >>> print(f"gRPC version: {versions.get('grpcio', 'not installed')}")
        """
        versions = {}

        all_deps = cls.REQUIRED_DEPENDENCIES + cls.OPTIONAL_DEPENDENCIES

        for import_name, package_name, _ in all_deps:
            try:
                module = __import__(import_name)
                version = getattr(module, "__version__", "unknown")
                versions[package_name] = version
            except (ImportError, AttributeError):
                versions[package_name] = "not installed"

        return versions


def check_grpc_dependencies(raise_on_missing: bool = True) -> Dict[str, bool]:
    """
    Convenience function to check gRPC dependencies.

    Args:
        raise_on_missing: If True, raises GRPCDependencyError when required deps are missing

    Returns:
        Dictionary with dependency status

    Raises:
        GRPCDependencyError: If required dependencies are missing and raise_on_missing=True

    Example:
        >>> from django_cfg.apps.integrations.grpc.utils.dependencies import check_grpc_dependencies
        >>>
        >>> # Check and raise error if missing
        >>> check_grpc_dependencies()
        >>>
        >>> # Check without raising error
        >>> status = check_grpc_dependencies(raise_on_missing=False)
        >>> if not all(status.values()):
        ...     print("Some dependencies are missing")
    """
    return DependencyChecker.check_all(raise_on_missing=raise_on_missing)


def print_dependency_status() -> None:
    """
    Print a formatted status report of all gRPC dependencies.

    Useful for debugging and verification.

    Example:
        >>> from django_cfg.apps.integrations.grpc.utils.dependencies import print_dependency_status
        >>> print_dependency_status()

        gRPC Dependencies Status:
        ========================
        ✅ grpcio              1.60.0
        ✅ grpcio-tools        1.60.0
        ✅ protobuf            5.27.0
        ✅ grpcio-reflection   1.60.0
        ✅ grpcio-health-checking 1.60.0
    """
    print("\ngRPC Dependencies Status:")
    print("=" * 60)

    versions = DependencyChecker.get_version_info()
    status = DependencyChecker.check_all(raise_on_missing=False)

    # Print required
    print("\nRequired:")
    for _, package_name, description in DependencyChecker.REQUIRED_DEPENDENCIES:
        version = versions.get(package_name, "not installed")
        is_installed = status.get(package_name, False)
        icon = "✅" if is_installed else "❌"
        print(f"  {icon} {package_name:<25} {version:<15} - {description}")

    # Print optional
    print("\nOptional (recommended):")
    for _, package_name, description in DependencyChecker.OPTIONAL_DEPENDENCIES:
        version = versions.get(package_name, "not installed")
        is_installed = status.get(package_name, False)
        icon = "✅" if is_installed else "⚠️ "
        print(f"  {icon} {package_name:<25} {version:<15} - {description}")

    print("\n" + "=" * 60)
    print()


def check_grpc_available() -> bool:
    """
    Check if all required gRPC dependencies are available.

    This is a lightweight check suitable for feature detection.
    Use `check_grpc_dependencies()` for detailed validation with error messages.

    This function is designed to be used by django_cfg.config.register_feature().

    Returns:
        True if all required gRPC dependencies are installed

    Example:
        >>> from django_cfg.apps.integrations.grpc.utils import check_grpc_available
        >>> if check_grpc_available():
        ...     print("gRPC is ready!")
        >>> else:
        ...     print("Install: pip install django-cfg[grpc]")

    Note:
        This is a pure dependency check. To check if gRPC is enabled in config,
        use `is_grpc_enabled()` from config_helper instead.
    """
    try:
        status = DependencyChecker.check_all(raise_on_missing=False)

        # Check only required dependencies (not optional)
        required_deps = ['grpcio', 'grpcio-tools', 'protobuf']
        return all(status.get(dep, False) for dep in required_deps)

    except Exception:
        # Fallback to simple import check
        try:
            import grpc as _grpc  # noqa: F401
            import grpc_tools as _grpc_tools  # noqa: F401
            import google.protobuf as _protobuf  # noqa: F401
            return True
        except ImportError:
            return False


def require_grpc_feature() -> None:
    """
    Require gRPC feature to be available or raise detailed ImportError.

    This function is used by django_cfg.config.require_feature() for gRPC.
    It provides detailed error messages with installation instructions.

    Raises:
        ImportError: If gRPC dependencies are missing (with detailed message)

    Example:
        >>> from django_cfg.apps.integrations.grpc.utils import require_grpc_feature
        >>> require_grpc_feature()  # Raises if not installed
        >>> # Safe to use gRPC after this point
    """
    if not check_grpc_available():
        try:
            # This will raise GRPCDependencyError with detailed Rich output
            DependencyChecker.check_all(raise_on_missing=True)
        except GRPCDependencyError as e:
            # Re-raise as ImportError for compatibility with django_cfg.config
            raise ImportError(str(e)) from e


__all__ = [
    "DependencyChecker",
    "GRPCDependencyError",
    "check_grpc_dependencies",
    "check_grpc_available",
    "require_grpc_feature",
    "print_dependency_status",
]
