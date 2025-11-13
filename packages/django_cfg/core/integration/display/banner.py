"""
ASCII Art Banner for Django CFG.

Provides beautiful startup banners for Django CFG display.
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


BANNER_STYLES = {
    "default": r"""
██████╗      ██╗ █████╗ ███╗   ██╗ ██████╗  ██████╗      ██████╗███████╗ ██████╗
██╔══██╗     ██║██╔══██╗████╗  ██║██╔════╝ ██╔═══██╗    ██╔════╝██╔════╝██╔════╝
██║  ██║     ██║███████║██╔██╗ ██║██║  ███╗██║   ██║    ██║     █████╗  ██║  ███╗
██║  ██║██   ██║██╔══██║██║╚██╗██║██║   ██║██║   ██║    ██║     ██╔══╝  ██║   ██║
██████╔╝╚█████╔╝██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝    ╚██████╗██║     ╚██████╔╝
╚═════╝  ╚════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝      ╚═════╝╚═╝      ╚═════╝
""",
}


def get_banner(style: str = "default") -> str:
    """
    Get ASCII art banner by style name.

    Args:
        style: Banner style name (default: "default")

    Returns:
        ASCII art banner string
    """
    return BANNER_STYLES.get(style, BANNER_STYLES["default"])


def print_banner(
    console: Console = None,
    style: str = "default",
    color: str = "cyan",
    with_panel: bool = False,
    panel_title: str = None,
    panel_border_style: str = None,
) -> None:
    """
    Print Django CFG ASCII art banner.

    Args:
        console: Rich Console instance (creates new if None)
        style: Banner style name
        color: Text color for the banner
        with_panel: Whether to wrap banner in a panel
        panel_title: Panel title (if with_panel=True)
        panel_border_style: Panel border style (if with_panel=True)
    """
    if console is None:
        console = Console()

    banner = get_banner(style)

    # Create styled text
    banner_text = Text(banner, style=f"bold {color}")

    if with_panel:
        panel = Panel(
            banner_text,
            title=panel_title or "",
            border_style=panel_border_style or color,
            padding=(0, 2),
        )
        console.print(panel)
    else:
        console.print(banner_text)


def get_available_styles() -> list:
    """
    Get list of available banner styles.

    Returns:
        List of style names
    """
    return list(BANNER_STYLES.keys())


__all__ = [
    'get_banner',
    'print_banner',
    'get_available_styles',
    'BANNER_STYLES',
]
