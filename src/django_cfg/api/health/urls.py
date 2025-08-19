"""
Django CFG Health Check URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.HealthCheckView.as_view(), name='django_cfg_health'),
    path('quick/', views.QuickHealthView.as_view(), name='django_cfg_quick_health'),
]
