"""
Theme configuration for Streamlit Admin.

Provides preset themes including Vercel-style dark theme.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class ThemeConfig:
    """Streamlit theme configuration."""

    # Base
    base: str  # "light" or "dark"

    # Colors
    primary_color: str
    background_color: str
    secondary_background_color: str
    text_color: str

    # Optional
    font: str = "sans serif"

    # Sidebar (optional overrides)
    sidebar_background: Optional[str] = None
    sidebar_secondary_background: Optional[str] = None
    sidebar_text_color: Optional[str] = None

    def to_toml(self) -> str:
        """Generate TOML configuration string."""
        # Note: Streamlit does NOT support [theme.sidebar] section
        # Sidebar colors are controlled by secondaryBackgroundColor
        lines = [
            "[theme]",
            f'base = "{self.base}"',
            f'primaryColor = "{self.primary_color}"',
            f'backgroundColor = "{self.background_color}"',
            f'secondaryBackgroundColor = "{self.secondary_background_color}"',
            f'textColor = "{self.text_color}"',
            f'font = "{self.font}"',
        ]

        return "\n".join(lines)


# Preset themes
THEMES: dict[str, ThemeConfig] = {
    "vercel-dark": ThemeConfig(
        base="dark",
        primary_color="#0070F3",  # Vercel blue
        background_color="#000000",  # Pure black
        secondary_background_color="#111111",
        text_color="#EDEDED",
        font="sans serif",
        sidebar_background="#0A0A0A",
        sidebar_secondary_background="#171717",
        sidebar_text_color="#EDEDED",
    ),
    "light": ThemeConfig(
        base="light",
        primary_color="#0070F3",
        background_color="#FFFFFF",
        secondary_background_color="#FAFAFA",
        text_color="#171717",
        font="sans serif",
    ),
}


class ThemeGenerator:
    """Generates Streamlit theme configuration files."""

    def __init__(self, theme_name: str = "vercel-dark"):
        if theme_name not in THEMES and theme_name != "custom":
            raise ValueError(
                f"Unknown theme: {theme_name}. "
                f"Available: {list(THEMES.keys())}"
            )
        self.theme_name = theme_name
        self.theme = THEMES.get(theme_name)

    def generate_config_toml(
        self,
        *,
        port: int = 8501,
        host: str = "0.0.0.0",
        enable_cors: bool = False,
        enable_xsrf: bool = False,
    ) -> str:
        """
        Generate full .streamlit/config.toml content.

        Args:
            port: Streamlit server port
            host: Streamlit server host
            enable_cors: Enable CORS (disable for iframe)
            enable_xsrf: Enable XSRF protection (disable for iframe)

        Returns:
            Complete config.toml content
        """
        sections = []

        # Server section
        sections.append(f"""[server]
headless = true
enableCORS = {"true" if enable_cors else "false"}
enableXsrfProtection = {"true" if enable_xsrf else "false"}
port = {port}
address = "{host}"
maxUploadSize = 200
enableWebsocketCompression = true""")

        # Browser section
        sections.append("""[browser]
gatherUsageStats = false
serverAddress = "localhost" """)

        # Theme section
        if self.theme:
            sections.append(self.theme.to_toml())

        # Client section
        sections.append("""[client]
showErrorDetails = true
toolbarMode = "developer" """)

        return "\n\n".join(sections)

    def get_theme_config(self) -> Optional[ThemeConfig]:
        """Get the theme configuration object."""
        return self.theme
