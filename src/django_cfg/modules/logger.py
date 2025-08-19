"""
Centralized Logger for Django Config Toolkit

Provides configurable logging with different levels and formatters.
"""

import logging
import os
import sys
import json
from typing import Optional, Dict, Any, Union, List
from pathlib import Path
import yaml
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax


class LoggerConfig:
    """Configuration for django_cfg logger."""

    # Default settings
    DEFAULT_LEVEL = logging.INFO
    DEFAULT_FORMAT = (
        "%(levelname)s %(asctime)s %(name)s %(process)d %(processName)s %(message)s"
    )
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Logger name
    LOGGER_NAME = "django_cfg"

    # Color codes for different levels
    COLORS = {
        logging.DEBUG: "\033[36m",  # Cyan
        logging.INFO: "\033[32m",  # Green
        logging.WARNING: "\033[33m",  # Yellow
        logging.ERROR: "\033[31m",  # Red
        logging.CRITICAL: "\033[35m",  # Magenta
        "RESET": "\033[0m",  # Reset
    }


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""

    def format(self, record):
        # Get the original formatted message
        formatted = super().format(record)

        # Add color if terminal supports it
        if hasattr(sys.stderr, "isatty") and sys.stderr.isatty():
            color = LoggerConfig.COLORS.get(record.levelno, "")
            reset = LoggerConfig.COLORS["RESET"]
            formatted = f"{color}{formatted}{reset}"

        return formatted


class DjangoCfgLogger:
    """Main logger class for Django Config Toolkit."""

    _instance = None
    _initialized = False

    def __new__(cls, name: Optional[str] = None):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name: Optional[str] = None):
        """Initialize logger."""
        if self._initialized:
            return

        self.name = name or LoggerConfig.LOGGER_NAME
        self.logger = logging.getLogger(self.name)
        self._setup_logger()
        self._initialized = True

    def _setup_logger(self, debug: bool = None, use_rich: bool = True) -> None:
        """Setup logger with appropriate configuration."""
        if debug is None:
            debug = os.environ.get("DEBUG", "false").lower() == "true"

        # Determine log level
        log_level = logging.DEBUG if debug else LoggerConfig.DEFAULT_LEVEL
        self.logger.setLevel(log_level)

        # Avoid adding handlers multiple times
        if self.logger.handlers:
            return

        # Use Rich handler if available and requested
        if use_rich:
            try:
                console = Console()
                handler = RichHandler(
                    console=console,
                    show_time=True,
                    show_path=False,
                    markup=True,
                    rich_tracebacks=True,
                )
            except Exception:
                # Fallback to standard handler if rich fails
                handler = self._create_standard_handler()
        else:
            handler = self._create_standard_handler()

        self.logger.addHandler(handler)

    def _create_standard_handler(self, use_colors: bool = True) -> logging.Handler:
        """Create standard logging handler."""
        handler = logging.StreamHandler()

        if use_colors:
            formatter = ColoredFormatter(
                LoggerConfig.DEFAULT_FORMAT,
                datefmt=LoggerConfig.DEFAULT_DATE_FORMAT,
            )
        else:
            formatter = logging.Formatter(
                LoggerConfig.DEFAULT_FORMAT,
                datefmt=LoggerConfig.DEFAULT_DATE_FORMAT,
            )

        handler.setFormatter(formatter)
        return handler

    # Basic logging methods
    def debug(self, message: str, *args, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, *args, **kwargs)

    def info(self, message: str, *args, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, *args, **kwargs)

    # Convenience methods for django_cfg
    def config_built(self, config_name: str) -> None:
        """Log when a configuration is built."""
        self.info(f"✅ Built {config_name} configuration")

    def config_warning(self, config_name: str, warning: str) -> None:
        """Log configuration warning."""
        self.warning(f"⚠️ Warning: {warning}")

    def config_error(self, config_name: str, error: str) -> None:
        """Log configuration error."""
        self.error(f"❌ Failed to build {config_name} configuration: {error}")

    def app_added(self, app_name: str, position: str = "end") -> None:
        """Log when an app is added."""
        self.info(f"  ✅ Added {app_name} to {position}")

    def app_already_installed(self, app_name: str) -> None:
        """Log when an app is already installed."""
        self.warning(f"  ⚠️ App {app_name} already installed")

    def init_complete(self, init_time_ms: float, environment: str) -> None:
        """Log when initialization is complete."""
        self.info(f"🚀 ConfigToolkit initialized in {init_time_ms:.2f}ms")
        self.info(f"🌍 Environment: {environment}")

    def success(self, message: str) -> None:
        """Log success message with emoji."""
        self.info(f"✅ {message}")

    def error_with_details(self, error: str, details: Optional[str] = None) -> None:
        """Log error with optional details."""
        self.error(f"❌ {error}")
        if details:
            self.error(f"   Details: {details}")

    # Data logging methods
    def data(
        self,
        data: Union[Dict, List, str],
        title: str = "Data",
        format_type: str = "auto",
    ) -> None:
        """Log data in a beautiful format."""
        if format_type == "auto":
            if isinstance(data, dict):
                format_type = "json"
            elif isinstance(data, list):
                format_type = "yaml"
            else:
                format_type = "text"

        try:
            if format_type == "json":
                formatted_data = json.dumps(data, indent=2, ensure_ascii=False)
                self.info(f"\n📊 {title}:\n{formatted_data}")
            elif format_type == "yaml" and yaml:
                formatted_data = yaml.dump(
                    data, default_flow_style=False, allow_unicode=True
                )
                self.info(f"\n📊 {title}:\n{formatted_data}")
            else:
                self.info(f"\n📊 {title}:\n{data}")
        except Exception as e:
            self.warning(f"Failed to format {title}: {e}")
            self.info(f"\n📊 {title}:\n{data}")

    def config_details(self, config_name: str, config_data: Dict[str, Any]) -> None:
        """Log configuration details in a structured way."""
        try:
            # Create a table-like structure
            details = []
            for key, value in config_data.items():
                if isinstance(value, str) and len(value) > 50:
                    value = value[:47] + "..."
                details.append(f"  {key}: {value}")

            self.info(f"🔧 {config_name} Configuration:")
            for detail in details:
                self.info(detail)
        except Exception as e:
            self.warning(f"Failed to log {config_name} details: {e}")


# Global logger instance
logger = DjangoCfgLogger()


# Convenience functions for backward compatibility
def get_logger(name: Optional[str] = None) -> DjangoCfgLogger:
    """Get logger instance."""
    return DjangoCfgLogger(name)


def log_debug(message: str, *args, **kwargs) -> None:
    """Log debug message."""
    logger.debug(message, *args, **kwargs)


def log_info(message: str, *args, **kwargs) -> None:
    """Log info message."""
    logger.info(message, *args, **kwargs)


def log_warning(message: str, *args, **kwargs) -> None:
    """Log warning message."""
    logger.warning(message, *args, **kwargs)


def log_error(message: str, *args, **kwargs) -> None:
    """Log error message."""
    logger.error(message, *args, **kwargs)


def log_critical(message: str, *args, **kwargs) -> None:
    """Log critical message."""
    logger.critical(message, *args, **kwargs)


# Convenience functions for common django_cfg messages
def log_config_built(config_name: str) -> None:
    """Log when a configuration is built."""
    logger.config_built(config_name)


def log_config_warning(config_name: str, warning: str) -> None:
    """Log configuration warning."""
    logger.config_warning(config_name, warning)


def log_config_error(config_name: str, error: str) -> None:
    """Log configuration error."""
    logger.config_error(config_name, error)


def log_app_added(app_name: str, position: str = "end") -> None:
    """Log when an app is added."""
    logger.app_added(app_name, position)


def log_app_already_installed(app_name: str) -> None:
    """Log when an app is already installed."""
    logger.app_already_installed(app_name)


def log_init_complete(init_time_ms: float, environment: str) -> None:
    """Log when initialization is complete."""
    logger.init_complete(init_time_ms, environment)


def log_data(
    data: Union[Dict, List, str], title: str = "Data", format_type: str = "auto"
) -> None:
    """Log data in a beautiful format."""
    logger.data(data, title, format_type)


def log_config_details(config_name: str, config_data: Dict[str, Any]) -> None:
    """Log configuration details in a structured way."""
    logger.config_details(config_name, config_data)


def log_success(message: str) -> None:
    """Log success message with emoji."""
    logger.success(message)


def log_error_with_details(error: str, details: Optional[str] = None) -> None:
    """Log error with optional details."""
    logger.error_with_details(error, details)
