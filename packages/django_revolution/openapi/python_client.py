"""
Modern Python Client Generator for Django Revolution

Clean, simple wrapper around openapi-python-client for excellent enum support.
"""

from pathlib import Path
from typing import Dict, Optional, Any

from ..config import DjangoRevolutionSettings, GenerationResult
from ..utils import Logger, ensure_directories
from ..generators import ModernPythonGenerator


class PythonClientGenerator:
    """
    Modern Python client generator wrapper.
    
    Uses openapi-python-client for:
    - Excellent enum support (proper Enum classes, not Optional[str])
    - Pydantic v2 compatibility
    - Modern Python 3.8+ features
    - Type-safe code generation
    - Clean, idiomatic code
    """

    def __init__(
        self, config: DjangoRevolutionSettings, logger: Optional[Logger] = None
    ):
        """
        Initialize Python generator.

        Args:
            config: Django Revolution settings
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or Logger("python_client_generator")
        self.output_dir = Path(config.generators.python.output_directory)
        
        # Initialize the modern generator
        self._generator = ModernPythonGenerator(config, self.logger)

    def is_openapi_generator_available(self) -> bool:
        """
        Check if openapi-python-client is available.

        Returns:
            bool: True if available
        """
        return self._generator.is_available()

    def generate_client(self, zone_name: str, schema_path: Path) -> GenerationResult:
        """
        Generate Python client for a single zone.

        Args:
            zone_name: Name of the zone
            schema_path: Path to OpenAPI schema file

        Returns:
            GenerationResult with operation details
        """
        return self._generator.generate_client(zone_name, schema_path)

    def generate_all(self, schemas: Dict[str, Path]) -> Dict[str, GenerationResult]:
        """
        Generate Python clients for all provided schemas.

        Args:
            schemas: Dictionary mapping zone names to schema paths

        Returns:
            Dictionary mapping zone names to generation results
        """
        return self._generator.generate_all(schemas)

    def clean_output(self) -> bool:
        """
        Clean Python output directory.

        Returns:
            bool: True if cleaning successful
        """
        try:
            if self.output_dir.exists():
                import shutil
                shutil.rmtree(self.output_dir)

            ensure_directories(self.output_dir)
            self.logger.success("Python output directory cleaned")
            return True

        except Exception as e:
            self.logger.error(f"Failed to clean Python output directory: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """
        Get Python generator status.

        Returns:
            Status information dictionary
        """
        base_status = self._generator.get_status()
        
        return {
            **base_status,
            "enabled": self.config.generators.python.enabled,
            "project_name_template": self.config.generators.python.project_name_template,
            "package_name_template": self.config.generators.python.package_name_template,
            "overwrite": self.config.generators.python.overwrite,
            "auto_format": self.config.generators.python.auto_format,
        }