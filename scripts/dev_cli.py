#!/usr/bin/env python3
"""
Django Revolution Development CLI

Main CLI for managing development tasks, testing, and publishing.
"""

import sys
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import questionary

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


def show_main_menu():
    """Show the main development menu."""
    console.print(
        Panel(
            "[bold blue]Django Revolution Development Tools[/bold blue]\n"
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
            questionary.Choice("🧪 Test Generation", value="test"),
            questionary.Choice("📋 Generate Requirements", value="requirements"),
            questionary.Choice("🔧 Build Package", value="build"),
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


def handle_test_generation():
    """Handle test generation."""
    console.print(Panel("Test Generation", title="🧪 Test", border_style="cyan"))

    confirm = questionary.confirm(
        "Run test generation in django_sample?", default=True
    ).ask()

    if confirm:
        try:
            subprocess.run(["./scripts/test_generation.sh"], check=True)
            console.print("✅ Test generation completed")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Test generation failed: {e}")


def handle_requirements_generation():
    """Handle requirements generation."""
    console.print(
        Panel(
            "Requirements Generation", title="📋 Requirements", border_style="magenta"
        )
    )

    try:
        subprocess.run([sys.executable, "scripts/generate_requirements.py"], check=True)
        console.print("✅ Requirements files generated")
    except subprocess.CalledProcessError as e:
        console.print(f"❌ Requirements generation failed: {e}")


def handle_build():
    """Handle package building."""
    console.print(Panel("Package Building", title="🔧 Build", border_style="red"))

    confirm = questionary.confirm(
        "Build the package for distribution?", default=True
    ).ask()

    if confirm:
        try:
            # Clean old builds
            import shutil

            for folder in ["build", "dist", "django_revolution.egg-info"]:
                if Path(folder).exists():
                    shutil.rmtree(folder)
                    console.print(f"🧹 Cleaned {folder}/")

            # Build package
            subprocess.run([sys.executable, "-m", "build"], check=True)
            console.print("✅ Package built successfully")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Build failed: {e}")


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
            elif choice == "test":
                handle_test_generation()
            elif choice == "requirements":
                handle_requirements_generation()
            elif choice == "build":
                handle_build()

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
