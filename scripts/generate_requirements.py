#!/usr/bin/env python3
"""
Generate requirements.txt from pyproject.toml

This script generates requirements.txt files from PEP 621 pyproject.toml format.
"""

import sys
from pathlib import Path
from rich.console import Console
import tomlkit

console = Console()


def extract_dependencies_from_toml(pyproject_path: Path):
    """Extract dependencies from pyproject.toml (PEP 621 format)."""
    try:
        with open(pyproject_path, "r") as f:
            pyproject = tomlkit.parse(f.read())
        
        # Extract main dependencies
        main_deps = pyproject.get("project", {}).get("dependencies", [])
        
        # Extract optional dependencies
        optional_deps = pyproject.get("project", {}).get("optional-dependencies", {})
        dev_deps = optional_deps.get("dev", [])
        test_deps = optional_deps.get("test", [])
        
        return main_deps, dev_deps, test_deps
        
    except Exception as e:
        console.print(f"❌ Failed to parse pyproject.toml: {e}")
        return [], [], []


def write_requirements_file(requirements, output_path: Path, header: str):
    """Write requirements to file with header."""
    with open(output_path, "w") as f:
        f.write(f"# {header}\n")
        f.write("# Generated automatically from pyproject.toml\n")
        f.write("# Do not edit manually!\n\n")
        
        for req in sorted(requirements):
            f.write(f"{req}\n")


def generate_requirements_files():
    """Generate all requirements files from pyproject.toml."""
    base_path = Path(__file__).parent.parent
    pyproject_path = base_path / "pyproject.toml"

    if not pyproject_path.exists():
        console.print(f"❌ pyproject.toml not found at {pyproject_path}")
        sys.exit(1)

    try:
        console.print("[yellow]Generating requirements files from pyproject.toml...[/yellow]")

        # Extract dependencies
        main_deps, dev_deps, test_deps = extract_dependencies_from_toml(pyproject_path)
        
        if not main_deps:
            console.print("⚠️ No main dependencies found in pyproject.toml")
            return False

        # Generate requirements.txt (main dependencies only)
        req_path = base_path / "requirements.txt"
        write_requirements_file(
            main_deps, 
            req_path, 
            "Main dependencies for django-cfg"
        )
        console.print(f"✅ Generated requirements.txt ({len(main_deps)} dependencies)")

        # Generate requirements-dev.txt (main + dev dependencies)
        if dev_deps:
            all_dev_deps = main_deps + dev_deps
            req_dev_path = base_path / "requirements-dev.txt"
            write_requirements_file(
                all_dev_deps,
                req_dev_path,
                "Development dependencies for django-cfg (includes main deps)"
            )
            console.print(f"✅ Generated requirements-dev.txt ({len(all_dev_deps)} dependencies)")
        else:
            console.print("⚠️ No dev dependencies found")

        # Generate requirements-test.txt (main + test dependencies)
        if test_deps:
            all_test_deps = main_deps + test_deps
            req_test_path = base_path / "requirements-test.txt"
            write_requirements_file(
                all_test_deps,
                req_test_path,
                "Test dependencies for django-cfg (includes main deps)"
            )
            console.print(f"✅ Generated requirements-test.txt ({len(all_test_deps)} dependencies)")

        # Print summary
        console.print(f"\n📊 Summary:")
        console.print(f"  Main dependencies: {len(main_deps)}")
        console.print(f"  Dev dependencies: {len(dev_deps)}")
        console.print(f"  Test dependencies: {len(test_deps)}")

        return True

    except Exception as e:
        console.print(f"❌ Failed to generate requirements: {e}")
        return False


if __name__ == "__main__":
    success = generate_requirements_files()
    sys.exit(0 if success else 1)