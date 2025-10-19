"""
Django CFG API URLs

Built-in API endpoints for django_cfg functionality.
"""

import traceback
from typing import List

from django.urls import include, path

from django_cfg.modules.django_logging import get_logger, sanitize_extra

logger = get_logger(__name__)


def get_enabled_cfg_apps() -> List[str]:
    """
    Get list of enabled django-cfg apps based on configuration.
    
    Returns:
        List of enabled app paths (e.g., ['django_cfg.apps.accounts', ...])
    """
    from django_cfg.modules.base import BaseCfgModule

    base_module = BaseCfgModule()
    enabled_apps = []

    if base_module.is_accounts_enabled():
        enabled_apps.append("django_cfg.apps.accounts")

    if base_module.is_knowbase_enabled():
        enabled_apps.append("django_cfg.apps.knowbase")

    if base_module.is_support_enabled():
        enabled_apps.append("django_cfg.apps.support")

    if base_module.is_newsletter_enabled():
        enabled_apps.append("django_cfg.apps.newsletter")

    if base_module.is_leads_enabled():
        enabled_apps.append("django_cfg.apps.leads")

    if base_module.is_agents_enabled():
        enabled_apps.append("django_cfg.apps.agents")

    if base_module.should_enable_tasks():
        enabled_apps.append("django_cfg.apps.tasks")

    if base_module.is_payments_enabled():
        enabled_apps.append("django_cfg.apps.payments")

    if base_module.is_rpc_enabled():
        enabled_apps.append("django_cfg.apps.ipc")

    return enabled_apps


def get_default_cfg_group():
    """
    Returns default OpenAPIGroupConfig for enabled django-cfg apps.
    
    Only includes apps that are enabled in the current configuration.
    
    This can be imported and added to your project's OpenAPIClientConfig groups:
    
    ```python
    from django_cfg.apps.urls import get_default_cfg_group
    
    openapi_client = OpenAPIClientConfig(
        groups=[
            get_default_cfg_group(),
            # ... your custom groups
        ]
    )
    ```
    
    Returns:
        OpenAPIGroupConfig with enabled django-cfg apps
    """
    from django_cfg.modules.django_client.core.config import OpenAPIGroupConfig

    return OpenAPIGroupConfig(
        name="cfg",
        apps=get_enabled_cfg_apps(),
        title="Django-CFG API",
        description="Authentication (OTP), Support, Newsletter, Leads, Knowledge Base, AI Agents, Tasks, Payments",
        version="1.0.0",
    )


def _safe_include(pattern_path: str, module_path: str):
    """
    Helper to safely include URL module if it exists.

    Args:
        pattern_path: URL pattern (e.g., 'cfg/knowbase/')
        module_path: Module path (e.g., 'django_cfg.apps.knowbase.urls')

    Returns:
        URLPattern if successful, None if import fails
    """
    try:
        return path(pattern_path, include(module_path))
    except ImportError as e:
        logger.warning(
            f"Failed to import URL module '{module_path}' for pattern '{pattern_path}': {e}",
            extra=sanitize_extra({
                'pattern': pattern_path,
                'module': module_path,
                'error': str(e),
            })
        )
        logger.debug(f"Traceback for '{module_path}':\n{traceback.format_exc()}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error including URL module '{module_path}' for pattern '{pattern_path}': {e}",
            extra=sanitize_extra({
                'pattern': pattern_path,
                'module': module_path,
                'error': str(e),
                'traceback': traceback.format_exc(),
            })
        )
        return None


# Core API endpoints (always enabled)
# Note: All prefixes are explicit here (cfg/, health/, etc.)
urlpatterns = [
    path('cfg/health/', include('django_cfg.apps.api.health.urls')),
    path('cfg/endpoints/', include('django_cfg.apps.api.endpoints.urls')),
    path('cfg/commands/', include('django_cfg.apps.api.commands.urls')),
    path('cfg/openapi/', include('django_cfg.modules.django_client.urls')),
]

# Django-CFG apps - conditionally registered based on config
# Map app paths to URL patterns (with cfg/ prefix from add_django_cfg_urls)
APP_URL_MAP = {
    "django_cfg.apps.accounts": [
        ("cfg/accounts/", "django_cfg.apps.accounts.urls"),
    ],
    "django_cfg.apps.support": [
        ("cfg/support/", "django_cfg.apps.support.urls"),
    ],
    "django_cfg.apps.newsletter": [
        ("cfg/newsletter/", "django_cfg.apps.newsletter.urls"),
    ],
    "django_cfg.apps.leads": [
        ("cfg/leads/", "django_cfg.apps.leads.urls"),
    ],
    "django_cfg.apps.knowbase": [
        ("cfg/knowbase/", "django_cfg.apps.knowbase.urls"),
        ("cfg/knowbase/admin/", "django_cfg.apps.knowbase.urls_admin"),
        ("cfg/knowbase/system/", "django_cfg.apps.knowbase.urls_system"),
    ],
    "django_cfg.apps.agents": [
        ("cfg/agents/", "django_cfg.apps.agents.urls"),
    ],
    "django_cfg.apps.tasks": [
        ("cfg/tasks/", "django_cfg.apps.tasks.urls"),
        ("cfg/tasks/admin/", "django_cfg.apps.tasks.urls_admin"),
    ],
    "django_cfg.apps.payments": [
        ("cfg/payments/", "django_cfg.apps.payments.urls"),
        # Payments v2.0: No separate urls_admin (uses Django Admin only)
    ],
    "django_cfg.apps.ipc": [
        ("cfg/ipc/", "django_cfg.apps.ipc.urls"),
        ("cfg/ipc/admin/", "django_cfg.apps.ipc.urls_admin"),
    ],
}

# Register URLs for enabled apps only
enabled_apps = get_enabled_cfg_apps()
cfg_app_urls = []

for app_path in enabled_apps:
    if app_path in APP_URL_MAP:
        for url_pattern, url_module in APP_URL_MAP[app_path]:
            cfg_app_urls.append(_safe_include(url_pattern, url_module))

# Maintenance (special case - admin only)
from django_cfg.modules.base import BaseCfgModule

if BaseCfgModule().is_maintenance_enabled():
    cfg_app_urls.append(_safe_include('admin/django_cfg_maintenance/', 'django_cfg.apps.maintenance.urls_admin'))

# Add only successfully imported URLs
urlpatterns.extend([url for url in cfg_app_urls if url is not None])
