"""
URLs for Django CFG Tasks app.

Provides RESTful endpoints for task queue management and monitoring using ViewSets and routers.
"""

from django.urls import path
from . import views

urlpatterns = [

    # Dashboard view
    path('dashboard/', views.dashboard_view, name='dashboard'),
]
