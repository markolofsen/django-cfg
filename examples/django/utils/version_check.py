"""
Python version checking utilities for django-cfg.

This module provides beautiful version checking with rich formatting
and helpful upgrade instructions for users.
"""

import sys
from typing import NoReturn


def check_python_version(context: str = "django-cfg") -> None:
    """
    Check if Python version meets requirements with beautiful output.
    
    Args:
        context: Context string for error messages (e.g., "django-cfg", "CLI")
    
    Raises:
        SystemExit: If Python version is < 3.12
    """
    if sys.version_info >= (3, 12):
        return  # Version is OK
    
    _show_version_error(context)


def _show_version_error(context: str) -> NoReturn:
    """Show beautiful version error message and exit."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.text import Text
        from rich.table import Table
        
        console = Console()
        
        # Create main error message
        error_text = Text()
        error_text.append("🐍 Python Version Incompatible\n\n", style="bold red")
        error_text.append(f"{context} requires ", style="white")
        error_text.append("Python 3.12+", style="bold green")
        error_text.append(" but you're using ", style="white")
        error_text.append(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", style="bold red")
        
        # Create upgrade instructions table
        upgrade_table = Table(show_header=True, header_style="bold cyan", show_lines=True)
        upgrade_table.add_column("Platform", style="bold blue", width=12)
        upgrade_table.add_column("Command", style="green", width=35)
        upgrade_table.add_column("Notes", style="dim", width=20)
        
        upgrade_table.add_row("macOS", "brew install python@3.12", "Homebrew")
        upgrade_table.add_row("Ubuntu", "sudo apt install python3.12", "22.04+")
        upgrade_table.add_row("Windows", "Download from python.org", "Official")
        upgrade_table.add_row("pyenv", "pyenv install 3.12.0", "Recommended")
        upgrade_table.add_row("conda", "conda install python=3.12", "Anaconda/Miniconda")
        
        # Create benefits text
        benefits_text = Text()
        benefits_text.append("✨ Python 3.12 Benefits:\n", style="bold yellow")
        benefits_text.append("• 40% faster performance\n", style="green")
        benefits_text.append("• Better error messages\n", style="green")
        benefits_text.append("• Modern syntax features\n", style="green")
        benefits_text.append("• Enhanced type checking", style="green")
        
        console.print()
        console.print(Panel(
            error_text,
            title=f"🚫 {context} Import Error",
            title_align="center",
            border_style="bright_red",
            padding=(1, 2)
        ))
        
        console.print()
        console.print(Panel(
            upgrade_table,
            title="🔧 Upgrade Instructions",
            title_align="center", 
            border_style="bright_blue",
            padding=(1, 2)
        ))
        
        console.print()
        console.print(Panel(
            benefits_text,
            title="💡 Why Upgrade?",
            title_align="center",
            border_style="bright_yellow",
            padding=(1, 2)
        ))
        
        # Footer
        footer_text = Text()
        footer_text.append("📚 Learn more: ", style="dim")
        footer_text.append("https://docs.python.org/3.12/whatsnew/", style="blue underline")
        console.print(footer_text)
        console.print()
        
    except ImportError:
        # Fallback if rich is not available
        print(f"❌ Error: {context} requires Python 3.12 or higher", file=sys.stderr)
        print(f"   Current Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", file=sys.stderr)
        print(f"   Please upgrade Python to use {context}", file=sys.stderr)
        print("", file=sys.stderr)
        print("💡 How to upgrade Python:", file=sys.stderr)
        print("   • macOS: brew install python@3.12", file=sys.stderr)
        print("   • Ubuntu: sudo apt install python3.12", file=sys.stderr)
        print("   • Windows: Download from python.org", file=sys.stderr)
        print("   • pyenv: pyenv install 3.12.0 && pyenv global 3.12.0", file=sys.stderr)
        print("", file=sys.stderr)
    
    sys.exit(1)


def get_python_version_string() -> str:
    """Get formatted Python version string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def is_python_compatible() -> bool:
    """Check if current Python version is compatible."""
    return sys.version_info >= (3, 12)
