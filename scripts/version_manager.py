#!/usr/bin/env python3
"""
Version Manager for Django-CFG
Manages versions in pyproject.toml and other files using tomlkit
"""

import re
import sys
from pathlib import Path
from typing import Tuple
import tomlkit


class VersionManager:
    """Manages version across package files."""

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()

    def get_current_version(self) -> str:
        """Get current version from pyproject.toml."""
        pyproject_path = self.base_path / "pyproject.toml"

        if not pyproject_path.exists():
            raise FileNotFoundError(f"pyproject.toml not found at {pyproject_path}")

        with open(pyproject_path, "r") as f:
            pyproject = tomlkit.parse(f.read())

        # Try PEP 621 format first
        if "project" in pyproject:
            version = pyproject["project"]["version"]
        # Fallback to Poetry format
        elif "tool" in pyproject and "poetry" in pyproject["tool"]:
            version = pyproject["tool"]["poetry"]["version"]
        else:
            raise ValueError("Version not found in pyproject.toml")

        if not version:
            raise ValueError("Version not found in pyproject.toml")

        return str(version)

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into components."""
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version}")

        return tuple(int(part) for part in parts)

    def bump_version(self, bump_type: str = "patch") -> str:
        """Bump version and update all files."""
        current_version = self.get_current_version()
        major, minor, patch = self.parse_version(current_version)

        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        new_version = f"{major}.{minor}.{patch}"

        # Update pyproject.toml
        self.update_pyproject_version(new_version)

        # Update __init__.py
        self.update_init_version(new_version)

        # Generate requirements files
        self.generate_requirements()

        return new_version

    def update_pyproject_version(self, version: str):
        """Update version in pyproject.toml using tomlkit."""
        file_path = self.base_path / "pyproject.toml"
        try:
            with open(file_path, "r") as f:
                pyproject = tomlkit.parse(f.read())
            
            # Update in PEP 621 format
            if "project" in pyproject:
                pyproject["project"]["version"] = version
            # Fallback to Poetry format
            elif "tool" in pyproject and "poetry" in pyproject["tool"]:
                pyproject["tool"]["poetry"]["version"] = version
            else:
                raise ValueError("Neither PEP 621 nor Poetry format found in pyproject.toml")
            
            with open(file_path, "w") as f:
                tomlkit.dump(pyproject, f)
            
            print(f"✅ Updated version in pyproject.toml to {version}")
        except Exception as e:
            print(f"❌ Failed to update pyproject.toml: {e}")

    def update_init_version(self, version: str):
        """Update __version__ in src/django_cfg/__init__.py."""
        file_path = self.base_path / "src" / "django_cfg" / "__init__.py"
        try:
            if not file_path.exists():
                print(f"⚠️ {file_path} not found, skipping...")
                return

            content = file_path.read_text(encoding="utf-8")
            
            # Update __version__ constant
            content = re.sub(
                r'__version__\s*=\s*["\']([^"\']+)["\']',
                f'__version__ = "{version}"',
                content,
                count=1
            )

            file_path.write_text(content, encoding="utf-8")
            print(f"✅ Updated __version__ in src/django_cfg/__init__.py to {version}")
        except Exception as e:
            print(f"❌ Failed to update src/django_cfg/__init__.py: {e}")

    def generate_requirements(self):
        """Generate requirements.txt files from pyproject.toml."""
        try:
            import subprocess
            
            # Use our custom requirements generator
            result = subprocess.run([
                sys.executable, "scripts/generate_requirements.py"
            ], cwd=self.base_path, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Generated requirements files from pyproject.toml")
                print(result.stdout)
            else:
                print(f"⚠️ Failed to generate requirements: {result.stderr}")

        except Exception as e:
            print(f"⚠️ Failed to generate requirements: {e}")

    def validate_version_consistency(self) -> bool:
        """Validate that all files have the same version."""
        reference_version = self.get_current_version()
        inconsistent = []

        # Check __init__.py version
        try:
            init_path = self.base_path / "src" / "django_cfg" / "__init__.py"
            if init_path.exists():
                content = init_path.read_text(encoding="utf-8")
                match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                if not match:
                    inconsistent.append("src/django_cfg/__init__.py: __version__ not found")
                elif match.group(1) != reference_version:
                    inconsistent.append(
                        f"src/django_cfg/__init__.py: __version__ = {match.group(1)} != {reference_version}"
                    )
        except Exception as e:
            inconsistent.append(f"Error reading src/django_cfg/__init__.py: {e}")

        if inconsistent:
            print("❌ Version inconsistencies found:")
            for error in inconsistent:
                print(f"  - {error}")
            return False

        print(f"✅ All versions are consistent: {reference_version}")
        return True


def main():
    """CLI for version management."""
    import argparse

    parser = argparse.ArgumentParser(description="Django-CFG Version Manager")
    parser.add_argument(
        "action",
        choices=["get", "bump", "validate"],
        help="Action to perform",
    )
    parser.add_argument(
        "--bump-type",
        choices=["major", "minor", "patch"],
        default="patch",
        help="Type of version bump (default: patch)",
    )

    args = parser.parse_args()
    config = VersionManager()

    if args.action == "get":
        version = config.get_current_version()
        print(f"Current version: {version}")

    elif args.action == "bump":
        new_version = config.bump_version(args.bump_type)
        print(f"Version bumped to: {new_version}")

    elif args.action == "validate":
        config.validate_version_consistency()


if __name__ == "__main__":
    main()