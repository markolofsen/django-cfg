#!/usr/bin/env python3
"""
Version Synchronizer for Django-CFG

Ensures all version references are synchronized across the project.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.version_manager import VersionManager
from rich.console import Console

console = Console()


def main():
    """Synchronize versions across all files."""
    console.print("[blue]🔄 Synchronizing versions...[/blue]")
    
    version_manager = VersionManager()
    
    try:
        # Get current version from pyproject.toml
        current_version = version_manager.get_current_version()
        console.print(f"[blue]Reference version: {current_version}[/blue]")
        
        # Update all files with the current version
        version_manager.update_init_version(current_version)
        
        # Generate requirements files
        version_manager.generate_requirements()
        
        # Validate consistency
        if version_manager.validate_version_consistency():
            console.print("[green]✅ All versions synchronized successfully![/green]")
            return 0
        else:
            console.print("[red]❌ Version synchronization failed![/red]")
            return 1
            
    except Exception as e:
        console.print(f"[red]❌ Error during synchronization: {e}[/red]")
        return 1


if __name__ == "__main__":
    sys.exit(main())
