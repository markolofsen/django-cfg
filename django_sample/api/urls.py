"""
URL configuration for Django CFG Sample Project.

Demonstrates automatic URL integration with django_cfg.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django_cfg import add_django_cfg_urls

# Basic URL patterns
urlpatterns = [
    # Admin interface (with Unfold theme)
    path("admin/", admin.site.urls),
    
    # Sample app URLs
    path("blog/", include("apps.blog.urls")),
    path("shop/", include("apps.shop.urls")),
    path("users/", include("apps.users.urls")),
    
    # Home page
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
]

# Automatically add django_cfg URLs and integrations
# This adds:
# - /cfg/health/ (Health check endpoint)
# - /cfg/commands/ (Management commands interface)
# - Django Revolution URLs (if available)
# - Debug output (in development)
urlpatterns = add_django_cfg_urls(urlpatterns)

# The above single line replaces manual URL configuration for:
# - Health monitoring
# - Command execution
# - API documentation
# - And automatically integrates with other packages!
