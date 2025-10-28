"""
URL Configuration for Next.js Admin.

Catch-all pattern to serve Next.js static files with SPA routing support.
"""

from django.urls import re_path
from .views import NextJsAdminView

app_name = 'nextjs_admin'

urlpatterns = [
    # Catch all routes for Next.js SPA
    # Examples:
    #   /cfg/admin/                    → NextJsAdminView (path='')
    #   /cfg/admin/private/centrifugo  → NextJsAdminView (path='private/centrifugo')
    #   /cfg/admin/_next/static/...    → NextJsAdminView (path='_next/static/...')
    re_path(r'^(?P<path>.*)$', NextJsAdminView.as_view(), name='serve'),
]
