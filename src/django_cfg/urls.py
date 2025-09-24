"""
URL Configuration for Django Config Toolkit

Provides URL patterns for health checks and other toolkit endpoints.
"""

from django.urls import path, include
from .health import HealthCheckView, SimpleHealthView


app_name = 'django_cfg'

urlpatterns = [
    # Health check endpoints
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/simple/', SimpleHealthView.as_view(), name='simple-health'),
]


def get_toolkit_urls():
    """
    Get URL patterns for Django Config Toolkit.
    
    Include in your main urls.py:
    
        from django_cfg.urls import get_toolkit_urls
        
        urlpatterns = [
            path('admin/', admin.site.urls),
            path('toolkit/', include(get_toolkit_urls())),
        ]
    """
    return urlpatterns
