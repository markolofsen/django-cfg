"""
Terminal App URL Configuration.

REST API endpoints for terminal session management.
Real-time communication is handled via Centrifugo WebSocket.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.api import TerminalSessionViewSet, TerminalCommandViewSet

app_name = 'terminal'

router = DefaultRouter()
router.register('sessions', TerminalSessionViewSet, basename='terminal-session')
router.register('commands', TerminalCommandViewSet, basename='terminal-command')

urlpatterns = [
    path('', include(router.urls)),
]
