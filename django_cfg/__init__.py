"""
Django-CFG: Developer-First Django Configuration with Pydantic v2

A revolutionary Django configuration system that provides type-safe, intelligent,
and zero-boilerplate configuration management through Pydantic v2 models.

Key Features:
- 90% reduction in settings.py boilerplate
- 100% type safety with Pydantic v2 models
- Environment-aware smart defaults
- Seamless third-party integrations
- Zero raw dictionary usage

Example:
    ```python
    from django_cfg import DjangoConfig, DatabaseConfig

    class MyConfig(DjangoConfig):
        project_name: str = "My Project"
        databases: dict[str, DatabaseConfig] = {
            "default": DatabaseConfig(
                engine="django.db.backends.postgresql",
                name="${DATABASE_URL:mydb}",
            )
        }

    config = MyConfig()
    ```
"""

# Version information
__version__ = "2.4.103"
__license__ = "MIT"

# Setup warnings debug early (checks env var only at this point)
from .core.debug import setup_warnings_debug

setup_warnings_debug()

# Start Django startup timer early (at module import time)
try:
    from .core.integration.timing import get_django_timer, start_django_timer
    if not get_django_timer():
        start_django_timer()
except ImportError:
    pass

# Library metadata
from .config import LIB_HEALTH_URL, LIB_NAME, LIB_SITE_URL

__author__ = LIB_NAME

# ---------------------------------------------------------------------------
# [GROUP 1] Core configuration & integration
# ---------------------------------------------------------------------------
from .core.admin_access import admin_urlpatterns
from .core.config import DjangoConfig, StartupInfoMode, set_current_config
from .core.exceptions import (
    CacheError,
    ConfigurationError,
    DatabaseError,
    DjangoCfgException,
    EnvironmentError,
    ValidationError,
)
from .core.integration import add_django_cfg_urls, get_django_cfg_urls_info
from .core.site import Site, SiteConfig, site_for, site_key, sites
from .core.utils.url_helpers import build_api_url, build_media_url, get_api_url, get_media_url
from .icons import IconCategories, Icons
from .models.api.account_emails import AccountEmailsConfig

# ---------------------------------------------------------------------------
# [GROUP 3] API models
# ---------------------------------------------------------------------------
from .models.api.drf import DRFConfig, RedocUISettings, SpectacularConfig, SwaggerUISettings
from .models.api.jwt import JWTConfig
from .models.api.keys import ApiKeys
from .models.api.limits import LimitsConfig
from .models.api.oauth import GitHubOAuthConfig, GoogleOAuthConfig, OAuthConfig
from .models.api.twofactor import TwoFactorConfig
from .models.django.admin_access import AdminAccessConfig
from .models.django.edge import EdgeConfig
from .models.django.visitor_geo import GeoOverride, VisitorGeoConfig
from .models.django.realtime import RealtimeConfig
from .models.django.analytics import AnalyticsConfig
from .models.django.axes import AxesConfig
from .models.django.chat import AttachmentsConfig, ChatConfig
from .models.django.constance import ConstanceConfig, ConstanceField
from .models.django.currency import CurrencyConfig
from .models.django.django_rq import DjangoRQConfig, RQQueueConfig, RQScheduleConfig

# ---------------------------------------------------------------------------
# [GROUP 4] Django models
# ---------------------------------------------------------------------------
from .models.django.environment import EnvironmentConfig
from .models.django.geo import GeoConfig
from .models.django.indexnow import IndexNowConfig, IndexNowSite
from .models.django.openapi import OpenAPIClientConfig
from .models.django.payments import PaymentsConfig
from .models.django.rq_health import QueueHealthThresholds, RQHealthConfig
from .models.django.simple_history import SimpleHistoryConfig
from .models.django.storage import CDNPurgeConfig, FileCleanupConfig, StorageConfig
from .models.django.storage_backend import S3StorageConfig
from .models.infrastructure.cache import CacheConfig

# ---------------------------------------------------------------------------
# [GROUP 2] Infrastructure models
# ---------------------------------------------------------------------------
from .models.infrastructure.database import DatabaseConfig
from .models.infrastructure.logging import LoggingConfig
from .models.infrastructure.security import SecurityConfig
from .models.services import EmailConfig, TelegramConfig

# ---------------------------------------------------------------------------
# [GROUP 8] Admin modules
# ---------------------------------------------------------------------------
from .modules.django_admin import (
    ActionConfig,
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    WidgetRegistry,
)

# ---------------------------------------------------------------------------
# [GROUP 7] Services
# ---------------------------------------------------------------------------
from .modules.django_email import (
    DjangoEmailService,
    get_admin_emails,
    send_admin_email,
    send_admin_notification,
    send_email,
)

# ---------------------------------------------------------------------------
# [GROUP 9] OpenAPI client
# ---------------------------------------------------------------------------
from .modules.django_generator.openapi.pipeline.config import OpenAPIConfig, OpenAPIGroupConfig
from .modules.django_logging.__cfg__ import DjangoLoggingConfig
from .modules.django_notion import NotionConfig, NotionLead, NotionTarget
from .core.base.config_model import FrontendErrorsConfig
from .modules.django_telegram import (
    DjangoTelegram,
    send_telegram_message,
    send_telegram_photo,
)

# ---------------------------------------------------------------------------
# [GROUP 5] Middleware & routing
# These modules require Django settings at import time (DRF reads REST_FRAMEWORK,
# axes reads AXES_ENABLED). They remain lazy — resolved via __getattr__ below.
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# [GROUP 6] Utilities & testing
# ---------------------------------------------------------------------------
from .testing.runners import FastTestRunner, SmartTestRunner

# ---------------------------------------------------------------------------
# Admin site: branding, sidebar navigation, header links (DjangoConfig.admin_site)
# ---------------------------------------------------------------------------
from .modules.admin_site.models.config import AdminSidebar, AdminSiteConfig
from .modules.admin_site.models.dropdown import SiteDropdownItem
from .modules.admin_site.models.navigation import (
    NavigationItem,
    NavigationItemType,
    NavigationSection,
)

# ---------------------------------------------------------------------------
# Dashboard tabs (always available — no optional deps)
# ---------------------------------------------------------------------------
from .modules.django_dashboard.models import DashboardConfig, DashboardTab

# ---------------------------------------------------------------------------
# [OPTIONAL] Django import-export  (requires: django-import-export)
# NOTE: imports Django models (AppRegistryNotReady if done before django.setup()),
# so these remain lazy — accessed via __getattr__ below.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# [OPTIONAL] MCP (Model Context Protocol for AI agents)
# ---------------------------------------------------------------------------
try:
    from .modules.django_mcp import (
        ALL_TOOLS as MCP_ALL_TOOLS,
    )
    from .modules.django_mcp import (
        PUBLIC_TOOLS as MCP_PUBLIC_TOOLS,
    )
    from .modules.django_mcp import (
        AppMCPConfig as MCPAppMCPConfig,
    )
    from .modules.django_mcp import (
        CommandMCPConfig as MCPCommandMCPConfig,
    )
    from .modules.django_mcp import (
        DjangoMCPModuleConfig,
        MCPConfigBuilder,
        MCPProfile,
    )
    from .modules.django_mcp import (
        IntrospectionConfig as MCPIntrospectionConfig,
    )
    from .modules.django_mcp import (
        ModelMCPConfig as MCPModelMCPConfig,
    )
    from .modules.django_mcp import (
        RedactionConfig as MCPRedactionConfig,
    )
except ImportError:
    DjangoMCPModuleConfig = None  # type: ignore[assignment]
    MCPConfigBuilder = None  # type: ignore[assignment]
    MCPProfile = None  # type: ignore[assignment]
    MCP_ALL_TOOLS = None  # type: ignore[assignment]
    MCP_PUBLIC_TOOLS = None  # type: ignore[assignment]
    MCPIntrospectionConfig = None  # type: ignore[assignment]
    MCPAppMCPConfig = None  # type: ignore[assignment]
    MCPModelMCPConfig = None  # type: ignore[assignment]
    MCPCommandMCPConfig = None  # type: ignore[assignment]
    MCPRedactionConfig = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Lazy imports — these modules read Django settings at import time
# (DRF reads REST_FRAMEWORK, import_export imports admin models).
# They are resolved on first access via __getattr__.
# ---------------------------------------------------------------------------
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Pagination (DRF reads REST_FRAMEWORK at class definition time)
    "DefaultPagination": ("django_cfg.middleware.pagination", "DefaultPagination"),
    "LargePagination": ("django_cfg.middleware.pagination", "LargePagination"),
    "SmallPagination": ("django_cfg.middleware.pagination", "SmallPagination"),
    "NoPagination": ("django_cfg.middleware.pagination", "NoPagination"),
    # Utils
    "check_python_version": ("django_cfg.utils.version_check", "check_python_version"),
    # Import-export (imports django.contrib.admin.models → AppRegistryNotReady)
    "ImportForm": ("django_cfg.modules.django_import_export", "ImportForm"),
    "ExportForm": ("django_cfg.modules.django_import_export", "ExportForm"),
    "SelectableFieldsExportForm": ("django_cfg.modules.django_import_export", "SelectableFieldsExportForm"),
    "ImportExportMixin": ("django_cfg.modules.django_import_export", "ImportExportMixin"),
    "ImportExportModelAdmin": ("django_cfg.modules.django_import_export", "ImportExportModelAdmin"),
    "ExportMixin": ("django_cfg.modules.django_import_export", "ExportMixin"),
    "ImportMixin": ("django_cfg.modules.django_import_export", "ImportMixin"),
    "BaseResource": ("django_cfg.modules.django_import_export", "BaseResource"),
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        module_path, class_name = _LAZY_IMPORTS[name]
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# ---------------------------------------------------------------------------
# Explicit __all__
# ---------------------------------------------------------------------------
__all__ = [
    # metadata
    "LIB_NAME", "LIB_SITE_URL", "LIB_HEALTH_URL",
    # core
    "DjangoConfig", "StartupInfoMode", "set_current_config",
    "add_django_cfg_urls", "get_django_cfg_urls_info", "admin_urlpatterns",
    "DjangoCfgException", "ConfigurationError", "ValidationError",
    "DatabaseError", "CacheError", "EnvironmentError",
    "get_media_url", "build_media_url", "build_api_url", "get_api_url",
    # infrastructure
    "DatabaseConfig", "CacheConfig", "SecurityConfig", "LoggingConfig",
    # API
    "DRFConfig", "SpectacularConfig", "SwaggerUISettings", "RedocUISettings",
    "JWTConfig", "GitHubOAuthConfig", "GoogleOAuthConfig", "OAuthConfig", "LimitsConfig",
    "ApiKeys", "TwoFactorConfig", "AccountEmailsConfig",
    # Django models
    "EnvironmentConfig", "AxesConfig",
    "DjangoRQConfig", "RQQueueConfig", "RQScheduleConfig",
    "RQHealthConfig", "QueueHealthThresholds",
    "DjangoLoggingConfig",
    "CurrencyConfig", "PaymentsConfig", "AdminAccessConfig", "EdgeConfig", "VisitorGeoConfig", "GeoOverride", "RealtimeConfig", "GeoConfig", "IndexNowConfig", "IndexNowSite", "Site", "SiteConfig", "site_for", "site_key", "sites", "AnalyticsConfig", "AttachmentsConfig", "ChatConfig", "SimpleHistoryConfig",
    "ConstanceConfig", "ConstanceField", "StorageConfig", "FileCleanupConfig", "CDNPurgeConfig", "S3StorageConfig", "OpenAPIClientConfig",
    "EmailConfig", "TelegramConfig", "NotionConfig", "NotionTarget", "NotionLead", "FrontendErrorsConfig",
    # middleware (lazy — DRF reads settings at import time)
    "DefaultPagination", "LargePagination", "SmallPagination", "NoPagination",
    # utils & testing
    "check_python_version", "SmartTestRunner", "FastTestRunner",
    # services
    "DjangoEmailService", "send_email", "get_admin_emails",
    "send_admin_email", "send_admin_notification",
    "DjangoTelegram", "send_telegram_message", "send_telegram_photo",
    # admin
    "AdminConfig", "FieldConfig", "FieldsetConfig", "ActionConfig", "WidgetRegistry",
    "Icons", "IconCategories",
    # openapi client
    "OpenAPIGroupConfig", "OpenAPIConfig",
    # admin site
    "AdminSiteConfig", "AdminSidebar",
    "NavigationItem", "NavigationSection", "NavigationItemType", "SiteDropdownItem",
    # dashboard
    "DashboardConfig", "DashboardTab",
    # optional: import-export (lazy — imports Django admin models)
    "ImportForm", "ExportForm", "SelectableFieldsExportForm",
    "ImportExportMixin", "ImportExportModelAdmin",
    "ExportMixin", "ImportMixin", "BaseResource",
    "DjangoMCPModuleConfig", "MCPConfigBuilder", "MCPProfile",
    "MCP_ALL_TOOLS", "MCP_PUBLIC_TOOLS",
    "MCPIntrospectionConfig", "MCPAppMCPConfig", "MCPModelMCPConfig",
    "MCPCommandMCPConfig", "MCPRedactionConfig",
]
