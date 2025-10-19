"""
Base display manager for Django CFG startup information.
"""

from typing import List, Optional

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Panel width configuration - use fixed widths for consistent layout
CONSOLE_WIDTH = 120  # Console width that fits most terminals
MAIN_PANEL_WIDTH = CONSOLE_WIDTH  # Full width panels
HALF_PANEL_WIDTH = (CONSOLE_WIDTH - 10) // 2  # 50% width for columns (minus borders/padding)


class BaseDisplayManager:
    """Base class for all display managers."""

    def __init__(self, config=None):
        """Initialize display manager with config."""
        self.config = config or self._get_current_config()
        self.console = Console()

    def _get_current_config(self):
        """Get current Django CFG configuration."""
        try:
            from django_cfg.core.config import get_current_config
            return get_current_config()
        except Exception:
            return None

    def get_base_url(self, *paths) -> str:
        """Get base URL for API endpoints with optional path components."""
        if self.config and hasattr(self.config, 'api_url'):
            base = self.config.api_url.rstrip('/')
        else:
            base = "http://localhost:8000"

        if paths:
            # Join all path components
            path_parts = []
            for path in paths:
                if path:
                    path_parts.append(str(path).strip('/'))

            if path_parts:
                return f"{base}/{'/'.join(path_parts)}/"

        return base

    def get_environment_style(self):
        """Get environment styling (panel_style, env_emoji, env_color)."""
        if not self.config:
            return "yellow", "🧪", "yellow"

        if self.config.is_development:
            return "green", "🚧", "green"
        elif self.config.is_production:
            return "red", "🚀", "red"
        else:
            return "yellow", "🧪", "yellow"

    def get_version(self) -> str:
        """Get Django CFG version."""
        try:
            from django_cfg import __version__
            return __version__
        except ImportError:
            return "unknown"

    def create_panel(self, content, title: str, border_style: str = "blue",
                    width: Optional[int] = None, expand: bool = False) -> Panel:
        """Create a standardized panel with fixed width by default."""
        # Use MAIN_PANEL_WIDTH by default for consistent layout
        panel_width = width if width is not None else MAIN_PANEL_WIDTH

        return Panel(
            content,
            title=title,
            border_style=border_style,
            width=panel_width,
            expand=expand,
            padding=(1, 2)
        )

    def create_full_width_panel(self, content, title: str, border_style: str = "blue") -> Panel:
        """Create a panel that spans the full width (same as two columns)."""
        # Wrap in a table to match the width of two-column layout
        wrapper_table = Table(show_header=False, box=None, padding=(0, 0), width=MAIN_PANEL_WIDTH)
        wrapper_table.add_column("Content", width=MAIN_PANEL_WIDTH, justify="left")

        panel = Panel(
            content,
            title=title,
            border_style=border_style,
            expand=True,
            padding=(1, 2)
        )

        wrapper_table.add_row(panel)
        return wrapper_table

    def create_table(self, title: str = None, show_header: bool = False) -> Table:
        """Create a standardized table."""
        table = Table(title=title, show_header=show_header, box=None)
        return table

    def print_panel(self, panel: Panel, centered: bool = False):
        """Print a panel, optionally centered."""
        if centered:
            self.console.print(Align.center(panel))
        else:
            self.console.print(panel)

    def print_columns(self, panels: List[Panel], equal: bool = True, expand: bool = True):
        """Print panels in columns."""
        if panels:
            self.console.print(Columns(panels, equal=equal, expand=expand))

    def print_two_column_table(self, left_content: str, right_content: str,
                              left_title: str = "", right_title: str = "",
                              left_style: str = "blue", right_style: str = "green"):
        """Print content in a proper 50/50 two-column layout with panels."""
        # Create panels that will expand to fill table cells
        left_panel = Panel(
            left_content,
            title=left_title,
            border_style=left_style,
            expand=True,
            padding=(1, 1)
        )

        right_panel = Panel(
            right_content,
            title=right_title,
            border_style=right_style,
            expand=True,
            padding=(1, 1)
        )

        # Use a table to force exact positioning
        wrapper_table = Table(show_header=False, box=None, padding=(0, 0), width=MAIN_PANEL_WIDTH)
        wrapper_table.add_column("Left", width=HALF_PANEL_WIDTH, justify="left")
        wrapper_table.add_column("Right", width=HALF_PANEL_WIDTH, justify="left")

        # Add panels as table cells
        wrapper_table.add_row(left_panel, right_panel)

        self.console.print(wrapper_table)

    def print_spacing(self, lines: int = 1):
        """Print empty lines for spacing."""
        for _ in range(lines):
            self.console.print()
