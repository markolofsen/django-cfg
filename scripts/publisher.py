#!/usr/bin/env python3
"""
Django-CFG Publisher

Interactive CLI for publishing the package to PyPI or TestPyPI.
"""

import os
import sys
import subprocess
import questionary
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.version_manager import VersionManager

console = Console()


def main():
    console.print(
        Panel(
            "[bold blue]Django-CFG Publisher[/bold blue]\nInteractive package publishing to PyPI",
            title="🚀 PyPI Publisher",
            border_style="blue",
        )
    )

    # Initialize version manager
    version_manager = VersionManager()

    # Show current version
    current_version = version_manager.get_current_version()
    console.print(f"[blue]Current version: {current_version}[/blue]")

    # Version bump selection
    bump_version = questionary.confirm(
        "Do you want to bump the version before publishing?", default=True
    ).ask()

    if bump_version:
        bump_type = questionary.select(
            "What type of version bump?",
            choices=[
                questionary.Choice("Patch (1.0.1 → 1.0.2)", value="patch"),
                questionary.Choice("Minor (1.0.1 → 1.1.0)", value="minor"),
                questionary.Choice("Major (1.0.1 → 2.0.0)", value="major"),
                questionary.Choice("Cancel", value=None),
            ],
        ).ask()

        if bump_type:
            try:
                new_version = version_manager.bump_version(bump_type)
                console.print(f"[green]✅ Version bumped to: {new_version}[/green]")

                # Validate version consistency
                if not version_manager.validate_version_consistency():
                    console.print(
                        "[red]❌ Version inconsistencies found! Please fix before publishing.[/red]"
                    )
                    return 1

            except Exception as e:
                console.print(f"[red]❌ Failed to bump version: {e}[/red]")
                return 1
        else:
            console.print("❌ Publishing cancelled.")
            return 0

    # Repository selection
    repo = questionary.select(
        "Where do you want to publish the package?",
        choices=[
            questionary.Choice("PyPI (production)", value="pypi"),
            questionary.Choice("TestPyPI (test)", value="testpypi"),
            questionary.Choice("Cancel", value=None),
        ],
    ).ask()
    if not repo:
        console.print("❌ Publishing cancelled.")
        return 0

    # Confirmation
    confirm = questionary.confirm(
        f"Publish to {'PyPI' if repo == 'pypi' else 'TestPyPI'}?", default=True
    ).ask()
    if not confirm:
        console.print("❌ Publishing cancelled.")
        return 0

    # Cleanup old build artifacts
    for pattern in ["build", "dist", "*.egg-info"]:
        for path in Path().glob(pattern):
            if path.exists():
                console.print(f"[blue]Removing old {path}...[/blue]")
                if path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                else:
                    path.unlink()

    # Generate requirements files before building
    console.print("[yellow]Generating requirements files...[/yellow]")
    try:
        requirements_result = subprocess.run([
            sys.executable, "scripts/generate_requirements.py"
        ], check=True, capture_output=True, text=True)
        console.print("✅ Requirements files generated from pyproject.toml")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Requirements generation failed: {e}[/red]")
        if e.stdout:
            console.print(f"[red]stdout: {e.stdout}[/red]")
        if e.stderr:
            console.print(f"[red]stderr: {e.stderr}[/red]")
        return 1

    # Build step
    console.print("[yellow]Building the package...[/yellow]")
    build_result = subprocess.run(
        [sys.executable, "-m", "build"], capture_output=True, text=True
    )
    console.print(build_result.stdout)
    if build_result.returncode != 0:
        console.print(f"[red]❌ Build failed![/red]\n{build_result.stderr}")
        return build_result.returncode

    # Check dist/ folder
    if not Path("dist").is_dir():
        console.print("[red]dist/ folder not found! Please build the package first.[/red]")
        return 1

    # Run publishing with twine
    console.print("[yellow]Publishing with twine...[/yellow]")
    try:
        twine_cmd = (
            ["twine", "upload", "--repository", repo, "dist/*"]
            if repo == "testpypi"
            else ["twine", "upload", "dist/*"]
        )
        result = subprocess.run(twine_cmd, check=False)
        if result.returncode == 0:
            console.print("[green]✅ Package published successfully![/green]")
        else:
            console.print(f"[red]❌ Publishing failed. Return code: {result.returncode}[/red]")
        return result.returncode
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())