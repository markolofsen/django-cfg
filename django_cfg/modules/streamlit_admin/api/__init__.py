"""
Streamlit Admin API.

High-level API wrapper for Streamlit admin applications with
automatic authentication from session state.

Usage:
    from django_cfg.modules.streamlit_admin.api import AdminAPI, require_auth

    # Require authentication (stops app if not logged in)
    user = require_auth()

    # Use API with auto-token
    api = AdminAPI()

    async with api as client:
        profile = await client.cfg_user_profile.profile_retrieve()
        queues = await client.cfg_rq_queues.queues_list()

    # Or access directly (proxied to cfg.API)
    api.cfg_auth
    api.cfg_rq_queues
"""

from .config import get_base_url, get_django_url, DEFAULT_BASE_URL
from .auth import (
    get_token,
    set_token,
    clear_token,
    is_authenticated,
    require_auth,
    get_user_info,
    refresh_token,
    logout,
)
from .client import AdminAPI

__all__ = [
    # Config
    "get_base_url",
    "get_django_url",
    "DEFAULT_BASE_URL",
    # Auth
    "get_token",
    "set_token",
    "clear_token",
    "is_authenticated",
    "require_auth",
    "get_user_info",
    "refresh_token",
    "logout",
    # Client
    "AdminAPI",
]
