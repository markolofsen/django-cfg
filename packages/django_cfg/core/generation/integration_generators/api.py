"""
API frameworks generator.

Handles JWT, DRF, Spectacular, and Django Client (OpenAPI) configuration.
Size: ~250 lines (focused on API frameworks)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class APIFrameworksGenerator:
    """
    Generates API framework settings.

    Responsibilities:
    - JWT authentication configuration
    - Django Client (OpenAPI) framework
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
        settings.update(self._generate_openapi_client_settings())
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

    def _generate_openapi_client_settings(self) -> Dict[str, Any]:
        """
        Generate Django Client (OpenAPI) framework settings.

        Returns:
            Dictionary with OpenAPI configuration and auto-generated DRF configuration
        """
        if not hasattr(self.config, "openapi_client") or not self.config.openapi_client:
            return {}

        settings = {}

        # OpenAPI Client configuration
        openapi_settings = {
            "OPENAPI_CLIENT": self.config.openapi_client.model_dump(),
        }
        settings.update(openapi_settings)

        # Auto-generate DRF configuration from OpenAPIClientConfig
        drf_settings = self._generate_drf_from_openapi()
        if drf_settings:
            settings.update(drf_settings)

        return settings

    def _generate_drf_from_openapi(self) -> Dict[str, Any]:
        """
        Generate DRF + Spectacular settings from OpenAPIClientConfig.

        Returns:
            Dictionary with DRF and Spectacular configuration
        """
        try:
            # Extract DRF parameters from OpenAPIClientConfig
            openapi_config = self.config.openapi_client

            # Get smart defaults for DRF
            from django_cfg.utils.smart_defaults import SmartDefaults
            drf_defaults = SmartDefaults.get_rest_framework_defaults()

            # Build REST_FRAMEWORK settings with smart defaults
            rest_framework = {
                "DEFAULT_SCHEMA_CLASS": "django_cfg.modules.django_client.spectacular.schema.PathBasedAutoSchema",
                "DEFAULT_PAGINATION_CLASS": "django_cfg.middleware.pagination.DefaultPagination",
                "PAGE_SIZE": 100,
                "DEFAULT_RENDERER_CLASSES": [
                    "rest_framework.renderers.JSONRenderer",
                    "django_cfg.modules.django_drf_theme.renderers.TailwindBrowsableAPIRenderer",
                ],
                # Add authentication classes from smart defaults
                "DEFAULT_AUTHENTICATION_CLASSES": drf_defaults["DEFAULT_AUTHENTICATION_CLASSES"],
                # Force ISO 8601 datetime format with Z suffix for all datetime fields
                "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
            }

            # Note: We don't set DEFAULT_PERMISSION_CLASSES here to allow public endpoints
            # Users can override with explicit DRFConfig if they want IsAuthenticated globally
            logger.info("🔐 Auto-configured JWT authentication for DRF (from smart defaults)")

            # Add authentication classes if not browsable
            if not openapi_config.drf_enable_browsable_api:
                rest_framework["DEFAULT_RENDERER_CLASSES"] = [
                    "rest_framework.renderers.JSONRenderer",
                ]

            # Add throttling if enabled
            if openapi_config.drf_enable_throttling:
                rest_framework["DEFAULT_THROTTLE_CLASSES"] = [
                    "rest_framework.throttling.AnonRateThrottle",
                    "rest_framework.throttling.UserRateThrottle",
                ]
                rest_framework["DEFAULT_THROTTLE_RATES"] = {
                    "anon": "100/day",
                    "user": "1000/day",
                }

            # Build SPECTACULAR_SETTINGS
            spectacular_settings = {
                "TITLE": openapi_config.drf_title,
                "DESCRIPTION": openapi_config.drf_description,
                "VERSION": openapi_config.drf_version,
                "SERVE_INCLUDE_SCHEMA": openapi_config.drf_serve_include_schema,
                "SCHEMA_PATH_PREFIX": openapi_config.get_drf_schema_path_prefix(),
                "SERVERS": [{"url": self.config.api_url}],  # Add base URL for OpenAPI schema
                "SWAGGER_UI_SETTINGS": {
                    "deepLinking": True,
                    "persistAuthorization": True,
                    "displayOperationId": True,
                },
                "COMPONENT_SPLIT_REQUEST": True,
                "COMPONENT_SPLIT_PATCH": True,
                # Postprocessing hooks
                "POSTPROCESSING_HOOKS": [
                    "django_cfg.modules.django_client.spectacular.auto_fix_enum_names",
                    "django_cfg.modules.django_client.spectacular.mark_async_operations",
                ],
            }

            drf_settings = {
                "REST_FRAMEWORK": rest_framework,
                "SPECTACULAR_SETTINGS": spectacular_settings,
            }

            logger.info("🚀 Generated DRF + Spectacular settings from OpenAPIClientConfig")
            logger.info("   - Pagination: django_cfg.middleware.pagination.DefaultPagination")
            logger.info("   - Renderer: TailwindBrowsableAPIRenderer")
            logger.info(f"   - API: {openapi_config.drf_title} v{openapi_config.drf_version}")

            return drf_settings

        except Exception as e:
            logger.warning(f"Could not generate DRF config from OpenAPIClientConfig: {e}")
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
        # Import authentication extension to register it with drf-spectacular
        # Only import if apps are ready to avoid warnings
        try:
            from django.apps import apps
            if apps.ready:
                from django_cfg.middleware import authentication  # noqa: F401
        except (ImportError, RuntimeError):
            pass

        # Check if Spectacular settings exist (from OpenAPI Client or elsewhere)
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

        Note: This method should NOT overwrite existing REST_FRAMEWORK settings.
        It should only add missing settings or extend existing ones.

        Returns:
            Dictionary with DRF settings
        """
        # Don't override if OpenAPIClientConfig already created full DRF config
        if hasattr(self.config, 'openapi_client') and self.config.openapi_client:
            logger.info("🔧 DRF settings already configured by OpenAPIClientConfig, skipping django-cfg extensions")
            return {}

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
