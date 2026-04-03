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

# Configure Django app
default_app_config = "django_cfg.apps.DjangoCfgConfig"

# Version information
__version__ = "2.0.30"
__license__ = "MIT"

# Setup warnings debug early (checks env var only at this point)
from .core.debug import setup_warnings_debug
setup_warnings_debug()

# Start Django startup timer early (at module import time)
try:
    from .core.integration.timing import start_django_timer, get_django_timer
    if not get_django_timer():
        start_django_timer()
except ImportError:
    pass

# Library metadata
from .config import LIB_NAME, LIB_SITE_URL, LIB_HEALTH_URL, get_default_dropdown_items
__author__ = LIB_NAME

# ---------------------------------------------------------------------------
# [GROUP 1] Core configuration & integration
# ---------------------------------------------------------------------------
from .core.config import DjangoConfig, StartupInfoMode, set_current_config
from .core.integration import add_django_cfg_urls, get_django_cfg_urls_info
from .core.exceptions import (
    DjangoCfgException,
    ConfigurationError,
    ValidationError,
    DatabaseError,
    CacheError,
    EnvironmentError,
)
from .core.utils.url_helpers import get_ticket_url, get_otp_url

# ---------------------------------------------------------------------------
# [GROUP 2] Infrastructure models
# ---------------------------------------------------------------------------
from .models.infrastructure.database import DatabaseConfig
from .models.infrastructure.cache import CacheConfig
from .models.infrastructure.security import SecurityConfig
from .models.infrastructure.logging import LoggingConfig

# ---------------------------------------------------------------------------
# [GROUP 3] API models
# ---------------------------------------------------------------------------
from .models.api.drf import DRFConfig, SpectacularConfig, SwaggerUISettings, RedocUISettings
from .models.api.jwt import JWTConfig
from .models.api.oauth import GitHubOAuthConfig, OAuthConfig
from .models.api.limits import LimitsConfig
from .models.api.keys import ApiKeys
from .models.api.twofactor import TwoFactorConfig

# ---------------------------------------------------------------------------
# [GROUP 4] Django models
# ---------------------------------------------------------------------------
from .models.django.environment import EnvironmentConfig
from .models.django.axes import AxesConfig
from .models.django.crypto_fields import CryptoFieldsConfig
from .models.django.django_rq import DjangoRQConfig, RQQueueConfig, RQScheduleConfig
from .modules.django_logging.__cfg__ import DjangoLoggingConfig
from .models.django.currency import CurrencyConfig
from .models.django.geo import GeoConfig
from .models.django.frontend_monitor import FrontendMonitorConfig
from .models.django.constance import ConstanceConfig, ConstanceField
from .models.django.storage import StorageConfig
from .models.django.openapi import OpenAPIClientConfig
from .models.services import EmailConfig, TelegramConfig

# ---------------------------------------------------------------------------
# [GROUP 5] Middleware & routing
# These modules require Django settings at import time (DRF reads REST_FRAMEWORK,
# axes reads AXES_ENABLED). They remain lazy — resolved via __getattr__ below.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# [GROUP 6] Utilities & testing
# ---------------------------------------------------------------------------
from .testing.runners import SmartTestRunner, FastTestRunner

# ---------------------------------------------------------------------------
# [GROUP 7] Services
# ---------------------------------------------------------------------------
from .modules.django_logging import DjangoLogger, get_logger
from .modules.django_email import (
    DjangoEmailService,
    send_email,
    get_admin_emails,
    send_admin_email,
    send_admin_notification,
)
from .modules.django_telegram import (
    DjangoTelegram,
    send_telegram_message,
    send_telegram_photo,
)

# ---------------------------------------------------------------------------
# [GROUP 8] Admin modules
# ---------------------------------------------------------------------------
from .modules.django_admin import (
    AdminConfig,
    FieldConfig,
    FieldsetConfig,
    ActionConfig,
    WidgetRegistry,
)
from .modules.django_admin.icons import Icons, IconCategories

# ---------------------------------------------------------------------------
# [GROUP 9] OpenAPI client
# ---------------------------------------------------------------------------
from .modules.django_client.core.config import OpenAPIGroupConfig, OpenAPIConfig

# ---------------------------------------------------------------------------
# [OPTIONAL] Unfold admin  (requires: django-unfold)
# ---------------------------------------------------------------------------
try:
    from .modules.django_unfold.models.config import (
        UnfoldConfig,
        UnfoldTheme,
        UnfoldThemeConfig,
        UnfoldColors,
        UnfoldSidebar,
        UnfoldDashboardConfig,
    )
    from .modules.django_unfold.models.navigation import (
        NavigationItem,
        NavigationSection,
        NavigationItemType,
    )
    from .modules.django_unfold.models.dropdown import SiteDropdownItem
except ImportError:
    UnfoldConfig = None  # type: ignore[assignment]
    UnfoldTheme = None  # type: ignore[assignment]
    UnfoldThemeConfig = None  # type: ignore[assignment]
    UnfoldColors = None  # type: ignore[assignment]
    UnfoldSidebar = None  # type: ignore[assignment]
    UnfoldDashboardConfig = None  # type: ignore[assignment]
    NavigationItem = None  # type: ignore[assignment]
    NavigationSection = None  # type: ignore[assignment]
    NavigationItemType = None  # type: ignore[assignment]
    SiteDropdownItem = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# [OPTIONAL] Streamlit admin  (requires: streamlit)
# ---------------------------------------------------------------------------
try:
    from .modules.streamlit_admin import StreamlitAdminConfig
except ImportError:
    StreamlitAdminConfig = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# [OPTIONAL] Centrifugo  (requires: cent)
# ---------------------------------------------------------------------------
try:
    from .modules.django_centrifugo.services.client.config import DjangoCfgCentrifugoConfig
except ImportError:
    DjangoCfgCentrifugoConfig = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# [OPTIONAL] Ngrok  (requires: pyngrok)
# ---------------------------------------------------------------------------
try:
    from .models.ngrok import NgrokConfig
    from .modules.django_ngrok import (
        DjangoNgrok,
        NgrokManager,
        NgrokError,
        get_ngrok_service,
        start_tunnel,
        stop_tunnel,
        get_tunnel_url,
        get_webhook_url,
        get_api_url,
        get_tunnel_url_from_env,
        get_ngrok_host_from_env,
        is_ngrok_available_from_env,
        is_tunnel_active,
        get_effective_tunnel_url,
    )
except ImportError:
    NgrokConfig = None  # type: ignore[assignment]
    DjangoNgrok = None  # type: ignore[assignment]
    NgrokManager = None  # type: ignore[assignment]
    NgrokError = None  # type: ignore[assignment]
    get_ngrok_service = None  # type: ignore[assignment]
    start_tunnel = None  # type: ignore[assignment]
    stop_tunnel = None  # type: ignore[assignment]
    get_tunnel_url = None  # type: ignore[assignment]
    get_webhook_url = None  # type: ignore[assignment]
    get_api_url = None  # type: ignore[assignment]
    get_tunnel_url_from_env = None  # type: ignore[assignment]
    get_ngrok_host_from_env = None  # type: ignore[assignment]
    is_ngrok_available_from_env = None  # type: ignore[assignment]
    is_tunnel_active = None  # type: ignore[assignment]
    get_effective_tunnel_url = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# [OPTIONAL] Cloudflare D1  (requires: cloudflare)
# ---------------------------------------------------------------------------
try:
    from .modules.django_cf import CloudflareConfig
except ImportError:
    CloudflareConfig = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# [OPTIONAL] Django import-export  (requires: django-import-export)
# NOTE: imports Django models (AppRegistryNotReady if done before django.setup()),
# so these remain lazy — accessed via __getattr__ below.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# [OPTIONAL] gRPC  (requires: grpcio)
# ---------------------------------------------------------------------------
try:
    from .modules.django_grpc.__cfg__ import DjangoGrpcModuleConfig
    from .modules.django_grpc.config.server import GrpcServerConfig, GrpcKeepaliveConfig
    from .modules.django_grpc.config.auth import GrpcAuthConfig
    from .modules.django_grpc.config.pool import GrpcPoolConfig
    from .modules.django_grpc.config.resilience import ResilienceConfig as GrpcResilienceConfig
    from .modules.django_grpc.config.observability import (
        ObservabilityConfig as GrpcObservabilityConfig,
        TelegramNotifyConfig as GrpcTelegramNotifyConfig,
        CentrifugoPublishConfig as GrpcCentrifugoPublishConfig,
    )
    from .modules.django_grpc.config.metrics import MetricsConfig as GrpcMetricsConfig
    from .modules.django_grpc.config.tls import TLSConfig as GrpcTLSConfig
except ImportError:
    DjangoGrpcModuleConfig = None  # type: ignore[assignment]
    GrpcServerConfig = None  # type: ignore[assignment]
    GrpcKeepaliveConfig = None  # type: ignore[assignment]
    GrpcAuthConfig = None  # type: ignore[assignment]
    GrpcPoolConfig = None  # type: ignore[assignment]
    GrpcResilienceConfig = None  # type: ignore[assignment]
    GrpcObservabilityConfig = None  # type: ignore[assignment]
    GrpcTelegramNotifyConfig = None  # type: ignore[assignment]
    GrpcCentrifugoPublishConfig = None  # type: ignore[assignment]
    GrpcMetricsConfig = None  # type: ignore[assignment]
    GrpcTLSConfig = None  # type: ignore[assignment]

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
    "version_check": ("django_cfg.utils.version_check", "version_check"),
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
    "LIB_NAME", "LIB_SITE_URL", "LIB_HEALTH_URL", "get_default_dropdown_items",
    # core
    "DjangoConfig", "StartupInfoMode", "set_current_config",
    "add_django_cfg_urls", "get_django_cfg_urls_info",
    "DjangoCfgException", "ConfigurationError", "ValidationError",
    "DatabaseError", "CacheError", "EnvironmentError",
    "get_ticket_url", "get_otp_url",
    # infrastructure
    "DatabaseConfig", "CacheConfig", "SecurityConfig", "LoggingConfig",
    # API
    "DRFConfig", "SpectacularConfig", "SwaggerUISettings", "RedocUISettings",
    "JWTConfig", "GitHubOAuthConfig", "OAuthConfig", "LimitsConfig",
    "ApiKeys", "TwoFactorConfig",
    # Django models
    "EnvironmentConfig", "AxesConfig", "CryptoFieldsConfig",
    "DjangoRQConfig", "RQQueueConfig", "RQScheduleConfig",
    "DjangoLoggingConfig",
    "CurrencyConfig", "GeoConfig", "FrontendMonitorConfig",
    "ConstanceConfig", "ConstanceField", "StorageConfig", "OpenAPIClientConfig",
    "EmailConfig", "TelegramConfig",
    # middleware (lazy — DRF reads settings at import time)
    "DefaultPagination", "LargePagination", "SmallPagination", "NoPagination",
    # utils & testing
    "version_check", "SmartTestRunner", "FastTestRunner",
    # services
    "DjangoLogger", "get_logger",
    "DjangoEmailService", "send_email", "get_admin_emails",
    "send_admin_email", "send_admin_notification",
    "DjangoTelegram", "send_telegram_message", "send_telegram_photo",
    # admin
    "AdminConfig", "FieldConfig", "FieldsetConfig", "ActionConfig", "WidgetRegistry",
    "Icons", "IconCategories",
    # openapi client
    "OpenAPIGroupConfig", "OpenAPIConfig",
    # optional: unfold
    "UnfoldConfig", "UnfoldTheme", "UnfoldThemeConfig", "UnfoldColors",
    "UnfoldSidebar", "UnfoldDashboardConfig",
    "NavigationItem", "NavigationSection", "NavigationItemType", "SiteDropdownItem",
    # optional: streamlit
    "StreamlitAdminConfig",
    # optional: centrifugo
    "DjangoCfgCentrifugoConfig",
    # optional: ngrok
    "NgrokConfig",
    "DjangoNgrok", "NgrokManager", "NgrokError",
    "get_ngrok_service", "start_tunnel", "stop_tunnel",
    "get_tunnel_url", "get_webhook_url", "get_api_url",
    "get_tunnel_url_from_env", "get_ngrok_host_from_env",
    "is_ngrok_available_from_env", "is_tunnel_active", "get_effective_tunnel_url",
    # optional: cloudflare
    "CloudflareConfig",
    # optional: import-export (lazy — imports Django admin models)
    "ImportForm", "ExportForm", "SelectableFieldsExportForm",
    "ImportExportMixin", "ImportExportModelAdmin",
    "ExportMixin", "ImportMixin", "BaseResource",
    # optional: grpc
    "DjangoGrpcModuleConfig", "GrpcServerConfig", "GrpcKeepaliveConfig", "GrpcAuthConfig", "GrpcPoolConfig",
    "GrpcResilienceConfig", "GrpcObservabilityConfig", "GrpcTelegramNotifyConfig",
    "GrpcCentrifugoPublishConfig", "GrpcMetricsConfig", "GrpcTLSConfig",
]
