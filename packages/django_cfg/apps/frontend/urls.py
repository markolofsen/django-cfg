"""URL Configuration for Frontend Apps."""

from django.urls import re_path
from .views import AdminView


app_name = 'frontend'

urlpatterns = [
    # Next.js Admin Panel - catch all routes for client-side routing
    re_path(r'^(?P<path>.*)$', AdminView.as_view(), name='admin'),
]
