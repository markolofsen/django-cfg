"""
URLs for Django CFG Tasks app.

Provides RESTful endpoints for task queue management and monitoring using ViewSets and routers.
"""

from django.urls import path

from .views import dashboard_view

urlpatterns = [

    # Dashboard view
    path('dashboard/', dashboard_view, name='dashboard'),
]
