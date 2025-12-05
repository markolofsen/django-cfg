"""
URL configuration for Django CFG Sample Project.

NOTE: Don't manually register app URLs here!
API URLs are auto-registered via OpenAPIGroupConfig in config.py.
Each group in openapi_client.groups automatically registers its URLs at /api/{name}/.

Example in config.py:
    OpenAPIGroupConfig(
        name="crypto",           # -> /api/crypto/
        apps=["apps.crypto"],    # Uses apps/crypto/urls.py
        ...
    )
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django_cfg import add_django_cfg_urls

# Basic URL patterns
urlpatterns = [
    # Admin interface (with Unfold theme)
    path("admin/", admin.site.urls),

    # Home page
    path("", TemplateView.as_view(template_name="home.html"), name="home"),

]

# This adds:
# - /cfg/health/ (Health check endpoint)
# - /cfg/commands/ (Management commands interface)
# - /admin/rpc/ (RPC Dashboard - if django_cfg_rpc is enabled)
# - Django Client URLs (OpenAPI client endpoints - if available)
# - Debug output (in development)
urlpatterns = add_django_cfg_urls(urlpatterns)

# The above single line replaces manual URL configuration for:
# - Health monitoring
# - Command execution
# - RPC Dashboard (automatic when enabled)
# - API documentation
# - And automatically integrates with other packages!
