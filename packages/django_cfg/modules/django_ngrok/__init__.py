"""
Django Ngrok Module for django_cfg.

Auto-configuring Ngrok integration for local development.
"""

from .service import (
    DjangoNgrok,
    NgrokError,
    NgrokManager,
    get_api_url,
    get_effective_tunnel_url,
    get_ngrok_host_from_env,
    get_ngrok_service,
    get_tunnel_url,
    get_tunnel_url_from_env,
    get_webhook_url,
    is_ngrok_available_from_env,
    is_tunnel_active,
    start_tunnel,
    stop_tunnel,
)

__all__ = [
    "DjangoNgrok",
    "NgrokManager",
    "NgrokError",
    "get_ngrok_service",
    "start_tunnel",
    "stop_tunnel",
    "get_tunnel_url",
    "get_webhook_url",
    "get_api_url",
    "get_tunnel_url_from_env",
    "get_ngrok_host_from_env",
    "is_ngrok_available_from_env",
    "is_tunnel_active",
    "get_effective_tunnel_url",
]
