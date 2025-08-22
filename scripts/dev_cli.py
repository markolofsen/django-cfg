#!/usr/bin/env python3
"""
Django-CFG Development CLI

Main CLI for managing development tasks and publishing.
"""

import sys
import shutil
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import questionary
import tomlkit

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.version_manager import VersionManager

console = Console()


def show_main_menu():
    """Show the main development menu."""
    console.print(
        Panel(
            "[bold blue]Django-CFG Development Tools[/bold blue]\n"
            "Choose an action to perform:",
            title="🛠️  Dev CLI",
            border_style="blue",
        )
    )

    choice = questionary.select(
        "What would you like to do?",
        choices=[
            questionary.Choice("📦 Version Management", value="version"),
            questionary.Choice("🚀 Publish Package", value="publish"),
            questionary.Choice("🔧 Build Package", value="build"),
            questionary.Choice("📄 Generate Requirements", value="requirements"),
            questionary.Choice("🧪 Run Tests", value="test"),
            questionary.Choice("❌ Exit", value="exit"),
        ],
    ).ask()

    return choice


def handle_version_management():
    """Handle version management tasks."""
    console.print(Panel("Version Management", title="📦 Version", border_style="green"))

    action = questionary.select(
        "Version action:",
        choices=[
            questionary.Choice("Get current version", value="get"),
            questionary.Choice("Bump version", value="bump"),
            questionary.Choice("Validate versions", value="validate"),
            questionary.Choice("Sync versions", value="sync"),
            questionary.Choice("Back to main menu", value="back"),
        ],
    ).ask()

    if action == "back":
        return

    if action == "bump":
        bump_type = questionary.select(
            "Bump type:",
            choices=[
                questionary.Choice("Patch (1.0.1 → 1.0.2)", value="patch"),
                questionary.Choice("Minor (1.0.1 → 1.1.0)", value="minor"),
                questionary.Choice("Major (1.0.1 → 2.0.0)", value="major"),
            ],
        ).ask()

        cmd = [
            sys.executable,
            "scripts/version_manager.py",
            "bump",
            "--bump-type",
            bump_type,
        ]
    elif action == "sync":
        cmd = [sys.executable, "scripts/sync_versions.py"]
    else:
        cmd = [sys.executable, "scripts/version_manager.py", action]

    try:
        result = subprocess.run(cmd, check=True)
        console.print(f"✅ Version management completed")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Version management failed: {e}")


def handle_publishing():
    """Handle package publishing."""
    console.print(
        Panel("Package Publishing", title="🚀 Publish", border_style="yellow")
    )

    confirm = questionary.confirm(
        "Start interactive publishing process?", default=True
    ).ask()

    if confirm:
        try:
            subprocess.run([sys.executable, "scripts/publisher.py"], check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Publishing failed: {e}")


def handle_build():
    """Handle package building."""
    console.print(Panel("Package Building", title="🔧 Build", border_style="red"))

    confirm = questionary.confirm(
        "Build the package for distribution?", default=True
    ).ask()

    if confirm:
        try:
            # Clean old builds
            for pattern in ["build", "dist", "*.egg-info"]:
                for path in Path().glob(pattern):
                    if path.exists():
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                        console.print(f"🧹 Cleaned {path}")

            # Generate requirements from pyproject.toml using our script
            console.print("[yellow]Generating requirements files...[/yellow]")
            
            try:
                subprocess.run([
                    sys.executable, "scripts/generate_requirements.py"
                ], check=True)
                
                console.print("✅ Requirements files generated from pyproject.toml")
                
            except subprocess.CalledProcessError as e:
                console.print(f"❌ Requirements generation failed: {e}")
                raise

            # Build package
            console.print("[yellow]Building the package...[/yellow]")
            subprocess.run([sys.executable, "-m", "build"], check=True)
            console.print("✅ Package built successfully")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Build failed: {e}")


def handle_requirements():
    """Handle requirements generation."""
    console.print(Panel("Generate Requirements Files", title="📄 Requirements", border_style="magenta"))

    confirm = questionary.confirm(
        "Generate requirements.txt files from pyproject.toml?", default=True
    ).ask()

    if confirm:
        try:
            subprocess.run([sys.executable, "scripts/generate_requirements.py"], check=True)
            console.print("✅ Requirements files generated successfully")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Requirements generation failed: {e}")


def handle_tests():
    """Handle running tests."""
    console.print(Panel("Running Tests", title="🧪 Tests", border_style="cyan"))

    test_type = questionary.select(
        "What tests to run?",
        choices=[
            questionary.Choice("All tests", value="all"),
            questionary.Choice("Unit tests only", value="unit"),
            questionary.Choice("Integration tests only", value="integration"),
            questionary.Choice("With coverage", value="coverage"),
            questionary.Choice("Back to main menu", value="back"),
        ],
    ).ask()

    if test_type == "back":
        return

    try:
        if test_type == "all":
            cmd = ["poetry", "run", "pytest", "tests/", "-v"]
        elif test_type == "unit":
            cmd = ["poetry", "run", "pytest", "tests/", "-m", "unit", "-v"]
        elif test_type == "integration":
            cmd = ["poetry", "run", "pytest", "tests/", "-m", "integration", "-v"]
        elif test_type == "coverage":
            cmd = ["poetry", "run", "pytest", "tests/", "--cov=django_cfg", "--cov-report=term-missing", "-v"]

        subprocess.run(cmd, check=True)
        console.print("✅ Tests completed successfully")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Tests failed: {e}")


def main():
    """Main CLI loop."""
    while True:
        try:
            choice = show_main_menu()

            if choice == "exit":
                console.print("👋 Goodbye!")
                break
            elif choice == "version":
                handle_version_management()
            elif choice == "publish":
                handle_publishing()
            elif choice == "build":
                handle_build()
            elif choice == "requirements":
                handle_requirements()
            elif choice == "test":
                handle_tests()

            # Ask if user wants to continue
            if choice != "exit":
                continue_choice = questionary.confirm(
                    "Continue with another task?", default=True
                ).ask()

                if not continue_choice:
                    console.print("👋 Goodbye!")
                    break

        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!")
            break
        except Exception as e:
            console.print(f"❌ Unexpected error: {e}")
            break


if __name__ == "__main__":
    main()