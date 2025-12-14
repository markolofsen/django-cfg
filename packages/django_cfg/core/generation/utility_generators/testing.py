"""
Testing settings generator.

Automatically configures Django test runner and testing-related settings.
Zero configuration - works out of the box.

🔥 Generated with django-cfg
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class TestingSettingsGenerator:
    """
    Generates Django testing settings.

    Responsibilities:
    - Configure SmartTestRunner for automatic test database management
    - Setup test-specific settings
    - Handle test parallelization configuration

    Example:
        ```python
        generator = TestingSettingsGenerator(config)
        settings = generator.generate()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate testing settings.

        Returns:
            Dictionary with test runner and testing configuration

        Features:
        - Automatically uses SmartTestRunner for test database management
        - Handles PostgreSQL extension installation
        - Auto-cleanup of old test databases
        - Zero configuration required

        Example:
            >>> generator = TestingSettingsGenerator(config)
            >>> settings = generator.generate()
            >>> settings['TEST_RUNNER']
            'django_cfg.testing.runners.SmartTestRunner'
        """
        settings = {}

        # 🔥 AUTOMATICALLY use SmartTestRunner for intelligent test database management
        settings['TEST_RUNNER'] = 'django_cfg.testing.runners.SmartTestRunner'

        # Additional testing settings
        settings['TEST_NON_SERIALIZED_APPS'] = []

        # Test output settings
        if self.config.debug:
            # More verbose output in development
            settings['TEST_OUTPUT_VERBOSE'] = True

        return settings


__all__ = ["TestingSettingsGenerator"]
