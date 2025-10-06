"""
Django Revolution Utilities

Common utilities for logging, error handling, and system operations.
"""

import logging
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from rich.console import Console
from rich.logging import RichHandler


class Logger:
    """Enhanced logger with rich output and contextual formatting."""

    def __init__(self, name: str = "django_revolution"):
        """Initialize logger with rich console."""
        self.name = name
        self.console = Console()
        self.logger = logging.getLogger(name)
        self._setup_logging()

    def _setup_logging(self):
        """Setup rich logging with proper formatting."""
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Add rich handler
        rich_handler = RichHandler(
            console=self.console, show_time=True, show_path=False, markup=True
        )
        rich_handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(rich_handler)

    def info(self, message: str):
        """Log info message with icon."""
        self.console.print(f"ℹ️  {message}", style="blue")

    def success(self, message: str):
        """Log success message with icon."""
        self.console.print(f"✅ {message}", style="green bold")

    def warning(self, message: str):
        """Log warning message with icon."""
        self.console.print(f"⚠️  {message}", style="yellow")

    def error(self, message: str):
        """Log error message with icon."""
        self.console.print(f"❌ {message}", style="red bold")

    def debug(self, message: str):
        """Log debug message."""
        if self.logger.level <= logging.DEBUG:
            self.console.print(f"🔍 {message}", style="dim")


class ErrorHandler:
    """Comprehensive error handling and validation utilities."""

    def __init__(self, logger: Optional[Logger] = None):
        """Initialize error handler with logger."""
        self.logger = logger or Logger("error_handler")

    def handle_exception(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """
        Handle exception with logging and return structured result.

        Args:
            error: The exception to handle
            context: Additional context for the error

        Returns:
            Dict with success=False and error details
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        self.logger.error(error_msg)

        # Log full traceback in debug mode
        import traceback

        if self.logger.logger.level <= logging.DEBUG:
            self.logger.debug(f"Traceback: {traceback.format_exc()}")

        return {
            "success": False,
            "error": error_msg,
            "error_type": type(error).__name__,
            "context": context,
        }

    def validate_path(self, path: Path, context: str = "") -> bool:
        """Validate if path exists."""
        if not path.exists():
            self.logger.error(f"{context}: Path does not exist: {path}")
            return False
        return True

    def validate_file(self, file_path: Path, context: str = "") -> bool:
        """Validate if file exists and is readable."""
        if not self.validate_path(file_path, context):
            return False

        if not file_path.is_file():
            self.logger.error(f"{context}: Path is not a file: {file_path}")
            return False

        try:
            with open(file_path, "r") as f:
                f.read(1)  # Test readability
            return True
        except Exception as e:
            self.logger.error(f"{context}: File is not readable: {e}")
            return False

    def validate_directory(self, dir_path: Path, context: str = "") -> bool:
        """Validate if directory exists and is accessible."""
        if not self.validate_path(dir_path, context):
            return False

        if not dir_path.is_dir():
            self.logger.error(f"{context}: Path is not a directory: {dir_path}")
            return False

        return True


def auto_install_dependencies() -> bool:
    """
    Automatically install required dependencies.

    Returns:
        bool: True if installation successful, False otherwise
    """
    logger = Logger("dependency_installer")

    dependencies = [
        # TypeScript generator
        {
            "name": "@hey-api/openapi-ts",
            "check_cmd": ["npx", "@hey-api/openapi-ts", "--version"],
            "install_cmd": ["npm", "install", "-g", "@hey-api/openapi-ts"],
        },
        # Python generator
        {
            "name": "datamodel-codegen",
            "check_cmd": ["datamodel-codegen", "--version"],
            "install_cmd": ["pip", "install", "datamodel-codegen"],
        },
    ]

    all_installed = True

    for dep in dependencies:
        logger.info(f"Checking {dep['name']}...")

        if check_dependency(dep["check_cmd"]):
            logger.success(f"{dep['name']} is available")
        else:
            logger.warning(f"{dep['name']} not found, installing...")
            if install_dependency(dep["install_cmd"]):
                logger.success(f"{dep['name']} installed successfully")
            else:
                logger.error(f"Failed to install {dep['name']}")
                all_installed = False

    return all_installed


def check_dependency(cmd: list) -> bool:
    """
    Check if a dependency is available.

    Args:
        cmd: Command to check dependency

    Returns:
        bool: True if dependency is available
    """
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def install_dependency(cmd: list) -> bool:
    """
    Install a dependency.

    Args:
        cmd: Command to install dependency

    Returns:
        bool: True if installation successful
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300  # 5 minutes
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def ensure_directories(*paths: Path) -> bool:
    """
    Ensure directories exist, creating them if necessary.

    Args:
        *paths: Paths to ensure exist

    Returns:
        bool: True if all directories were created/exist
    """
    logger = Logger("directory_manager")

    try:
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        return False


def run_command(
    command: str, cwd: Optional[Path] = None, timeout: int = 120
) -> Tuple[bool, str]:
    """
    Run a shell command and return result.

    Args:
        command: Command to run
        cwd: Working directory
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success, output)
    """
    logger = Logger("command_runner")

    try:
        logger.debug(f"Running command: {command}")
        if cwd:
            logger.debug(f"Working directory: {cwd}")

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = result.stdout or result.stderr
        success = result.returncode == 0

        if success:
            logger.debug(f"Command succeeded: {output}")
        else:
            logger.warning(f"Command failed (code {result.returncode}): {output}")

        return success, output

    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out after {timeout} seconds")
        return False, f"Command timed out after {timeout} seconds"
    except Exception as e:
        logger.error(f"Command execution failed: {e}")
        return False, str(e)


def render_template(template_content: str, context: Dict[str, Any]) -> str:
    """
    Render a Jinja2 template with context.

    Args:
        template_content: Template string
        context: Template variables

    Returns:
        Rendered template string
    """
    try:
        import jinja2

        # Create Jinja2 environment with custom filters
        env = jinja2.Environment(loader=jinja2.BaseLoader(), autoescape=False)

        # Add custom filters
        env.filters["title"] = lambda x: x.replace("_", " ").title()
        env.filters["snake_case"] = (
            lambda x: x.lower().replace(" ", "_").replace("-", "_")
        )
        env.filters["camel_case"] = lambda x: "".join(
            word.capitalize() for word in x.replace("_", " ").split()
        )

        template = env.from_string(template_content)
        return template.render(**context)

    except ImportError:
        # Fallback to simple string formatting
        Logger("template_renderer").warning(
            "Jinja2 not available, using simple formatting"
        )
        return template_content.format(**context)
    except Exception as e:
        Logger("template_renderer").error(f"Template rendering failed: {e}")
        return template_content


def get_config() -> Dict[str, Any]:
    """
    Get configuration from various sources.

    Returns:
        Configuration dictionary
    """
    from .config import get_settings

    return get_settings().to_dict()


def clean_directory(directory: Path, keep_patterns: Optional[List[str]] = None) -> bool:
    """
    Clean a directory, optionally keeping files matching patterns.

    Args:
        directory: Directory to clean
        keep_patterns: Glob patterns for files to keep

    Returns:
        bool: True if cleaning successful
    """
    logger = Logger("directory_cleaner")

    if not directory.exists():
        logger.debug(f"Directory does not exist: {directory}")
        return True

    try:
        keep_patterns = keep_patterns or []

        for item in directory.iterdir():
            # Check if item should be kept
            should_keep = False
            for pattern in keep_patterns:
                if item.match(pattern):
                    should_keep = True
                    break

            if should_keep:
                logger.debug(f"Keeping: {item}")
                continue

            if item.is_dir():
                shutil.rmtree(item)
                logger.debug(f"Removed directory: {item}")
            else:
                item.unlink()
                logger.debug(f"Removed file: {item}")

        logger.success(f"Cleaned directory: {directory}")
        return True

    except Exception as e:
        logger.error(f"Failed to clean directory {directory}: {e}")
        return False


def get_django_manage_py() -> Optional[Path]:
    """
    Find Django manage.py in common locations.

    Returns:
        Path to manage.py if found, None otherwise
    """
    logger = Logger("django_finder")

    # Try Django settings first
    try:
        from django.conf import settings

        if hasattr(settings, "BASE_DIR"):
            possible_paths = [
                Path(settings.BASE_DIR) / "manage.py",
                Path(settings.BASE_DIR).parent / "manage.py",
            ]
        else:
            possible_paths = []
    except ImportError:
        possible_paths = []

    # Add common locations
    # Recursive search for manage.py (up to 3 levels)
    for root, dirs, files in os.walk(Path.cwd()):
        if "manage.py" in files:
            possible_paths.append(Path(root) / "manage.py")
            break

    for path in possible_paths:
        if path.exists() and path.is_file():
            logger.debug(f"Found manage.py at: {path}")
            return path

    logger.warning("Django manage.py not found in any common locations")
    return None
