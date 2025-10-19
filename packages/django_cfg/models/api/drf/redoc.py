"""
Redoc UI settings for DRF Spectacular.
"""

from typing import Any, Dict

from pydantic import BaseModel, Field


class RedocUISettings(BaseModel):
    """Redoc UI specific settings."""

    native_scrollbars: bool = Field(default=True, description="Use native scrollbars")
    theme_color: str = Field(default="#7c3aed", description="Primary theme color")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Redoc UI."""
        return {
            "nativeScrollbars": self.native_scrollbars,
            "theme": {
                "colors": {
                    "primary": {
                        "main": self.theme_color
                    }
                }
            }
        }


__all__ = [
    "RedocUISettings",
]
