"""
API frameworks generator.

Handles JWT, DRF, Spectacular, and Django Revolution configuration.
Size: ~250 lines (focused on API frameworks)
"""

from typing import Dict, Any, TYPE_CHECKING
import logging

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class APIFrameworksGenerator:
    """
    Generates API framework settings.

    Responsibilities:
    - JWT authentication configuration
    - Django Revolution framework
    - Django REST Framework (DRF)
    - DRF Spectacular (OpenAPI/Swagger)
    - Auto-configuration and extensions

    Example:
        ```python
        generator = APIFrameworksGenerator(config)
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
        Generate API framework settings.

        Returns:
            Dictionary with API configurations

        Example:
            >>> generator = APIFrameworksGenerator(config)
            >>> settings = generator.generate()
        """
        settings = {}

        # Generate settings for each API framework
        settings.update(self._generate_jwt_settings())
        settings.update(self._generate_revolution_settings())
        settings.update(self._apply_drf_spectacular_extensions())

        return settings

    def _generate_jwt_settings(self) -> Dict[str, Any]:
        """
        Generate JWT authentication settings.

        Returns:
            Dictionary with JWT configuration
        """
        if not hasattr(self.config, "jwt") or not self.config.jwt:
            return {}

        jwt_settings = self.config.jwt.to_django_settings(self.config.secret_key)
        return jwt_settings

    def _generate_revolution_settings(self) -> Dict[str, Any]:
        """
        Generate Django Revolution framework settings.

        Returns:
            Dictionary with Revolution and auto-generated DRF configuration
        """
        if not hasattr(self.config, "revolution") or not self.config.revolution:
            return {}

        settings = {}

        # Revolution configuration
        revolution_settings = {
            "DJANGO_REVOLUTION": {
                "api_prefix": self.config.revolution.api_prefix,
                "debug": getattr(self.config.revolution, "debug", self.config.debug),
                "auto_install_deps": getattr(self.config.revolution, "auto_install_deps", True),
                "zones": {
                    zone_name: zone_config.model_dump()
                    for zone_name, zone_config in self.config.revolution.get_zones_with_defaults().items()
                },
            }
        }
        settings.update(revolution_settings)

        # Auto-generate DRF configuration using Revolution's core_config
        drf_settings = self._generate_drf_from_revolution()
        if drf_settings:
            settings.update(drf_settings)

        return settings

    def _generate_drf_from_revolution(self) -> Dict[str, Any]:
        """
        Generate DRF + Spectacular settings from Revolution config.

        Returns:
            Dictionary with DRF and Spectacular configuration
        """
        try:
            from django_revolution import create_drf_spectacular_config

            # Extract DRF parameters from RevolutionConfig
            drf_kwargs = {
                "title": getattr(self.config.revolution, "drf_title", "API"),
                "description": getattr(self.config.revolution, "drf_description", "RESTful API"),
                "version": getattr(self.config.revolution, "drf_version", "1.0.0"),
                "schema_path_prefix": f"/{self.config.revolution.api_prefix}/",
                "enable_browsable_api": getattr(self.config.revolution, "drf_enable_browsable_api", False),
                "enable_throttling": getattr(self.config.revolution, "drf_enable_throttling", False),
            }

            # Create DRF + Spectacular config with Revolution's comprehensive settings
            drf_settings = create_drf_spectacular_config(**drf_kwargs)

            logger.info("🚀 Generated DRF + Spectacular settings using Revolution's create_drf_spectacular_config")

            return drf_settings

        except ImportError as e:
            logger.warning(f"Could not import django_revolution.create_drf_spectacular_config: {e}")
            return {}
        except Exception as e:
            logger.warning(f"Could not generate DRF config from Revolution: {e}")
            return {}

    def _apply_drf_spectacular_extensions(self) -> Dict[str, Any]:
        """
        Apply django-cfg DRF and Spectacular extensions.

        This method extends existing DRF/Spectacular settings or creates them if they don't exist.

        Returns:
            Dictionary with extended DRF and Spectacular configuration
        """
        settings = {}

        try:
            # Apply Spectacular extensions
            spectacular_settings = self._apply_spectacular_extensions()
            if spectacular_settings:
                settings.update(spectacular_settings)

            # Apply DRF extensions
            drf_settings = self._apply_drf_extensions()
            if drf_settings:
                settings.update(drf_settings)

        except Exception as e:
            logger.warning(f"Could not apply DRF/Spectacular extensions from django-cfg: {e}")

        return settings

    def _apply_spectacular_extensions(self) -> Dict[str, Any]:
        """
        Apply Spectacular settings extensions.

        Returns:
            Dictionary with Spectacular settings
        """
        # Check if Spectacular settings exist (from Revolution or elsewhere)
        if not hasattr(self, '_has_spectacular_settings'):
            return {}

        settings = {"SPECTACULAR_SETTINGS": {}}

        if self.config.spectacular:
            # User provided explicit spectacular config
            spectacular_extensions = self.config.spectacular.get_spectacular_settings(
                project_name=self.config.project_name
            )
            settings["SPECTACULAR_SETTINGS"].update(spectacular_extensions)
            logger.info("🔧 Extended SPECTACULAR_SETTINGS with django-cfg Spectacular config")
        else:
            # Auto-create minimal spectacular config to set project name
            from django_cfg.models.api.drf import SpectacularConfig

            auto_spectacular = SpectacularConfig()
            spectacular_extensions = auto_spectacular.get_spectacular_settings(
                project_name=self.config.project_name
            )
            settings["SPECTACULAR_SETTINGS"].update(spectacular_extensions)
            logger.info(f"🚀 Auto-configured API title as '{self.config.project_name} API'")

        return settings

    def _apply_drf_extensions(self) -> Dict[str, Any]:
        """
        Apply DRF settings extensions.

        Returns:
            Dictionary with DRF settings
        """
        settings = {}

        if self.config.drf:
            # User provided explicit DRF config
            drf_extensions = self.config.drf.get_rest_framework_settings()
            settings["REST_FRAMEWORK"] = drf_extensions
            logger.info("🔧 Extended REST_FRAMEWORK settings with django-cfg DRF config")
        else:
            # Auto-create minimal DRF config to set default pagination
            from django_cfg.models.api.drf import DRFConfig

            auto_drf = DRFConfig()
            drf_extensions = auto_drf.get_rest_framework_settings()

            # Only apply pagination settings
            pagination_settings = {
                'DEFAULT_PAGINATION_CLASS': drf_extensions['DEFAULT_PAGINATION_CLASS'],
                'PAGE_SIZE': drf_extensions['PAGE_SIZE'],
            }
            settings["REST_FRAMEWORK"] = pagination_settings

            logger.info(f"🚀 Auto-configured default pagination: {drf_extensions['DEFAULT_PAGINATION_CLASS']}")

        return settings


__all__ = ["APIFrameworksGenerator"]
