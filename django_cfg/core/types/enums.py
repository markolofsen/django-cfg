"""Core enumerations for django-cfg."""

from enum import Enum


class EnvironmentMode(str, Enum):
    """Environment mode enumeration."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"

    @classmethod
    def from_debug(cls, debug: bool) -> "EnvironmentMode":
        """
        Get environment mode from debug flag.

        Args:
            debug: Debug mode flag

        Returns:
            DEVELOPMENT if debug=True, PRODUCTION otherwise
        """
        return cls.DEVELOPMENT if debug else cls.PRODUCTION

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """
        Check if value is a valid environment mode.

        Args:
            value: Value to check

        Returns:
            True if valid, False otherwise
        """
        return value in [mode.value for mode in cls]


class StartupInfoMode(str, Enum):
    """Startup information display mode."""

    NONE = "none"
    SHORT = "short"
    FULL = "full"

    def should_display(self) -> bool:
        """Check if should display startup info."""
        return self != self.NONE
