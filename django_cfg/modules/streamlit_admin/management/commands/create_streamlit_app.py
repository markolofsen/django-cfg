"""
Django management command to create Streamlit admin app scaffold.

Usage:
    python manage.py create_streamlit_app admin_app
    python manage.py create_streamlit_app admin_app --theme vercel-dark
    python manage.py create_streamlit_app admin_app --with-pages
"""

import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    """Create Streamlit admin app scaffold."""

    help = "Create a new Streamlit admin application"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "path",
            help="Path for new Streamlit app (relative to BASE_DIR)",
        )
        parser.add_argument(
            "--theme",
            default="vercel-dark",
            choices=["vercel-dark", "light"],
            help="Theme preset (default: vercel-dark)",
        )
        parser.add_argument(
            "--with-pages",
            action="store_true",
            help="Include example pages (users, settings)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing directory",
        )

    def handle(self, *args, **options):
        """Handle command execution."""
        from django_cfg.modules.streamlit_admin.core import ThemeGenerator

        # Resolve output path
        output_path = Path(options["path"])
        if not output_path.is_absolute():
            output_path = Path(settings.BASE_DIR) / output_path

        # Check if exists
        if output_path.exists() and not options["force"]:
            raise CommandError(
                f"Directory already exists: {output_path}\n"
                f"Use --force to overwrite"
            )

        theme = options["theme"]
        with_pages = options["with_pages"]

        self.stdout.write(
            self.style.SUCCESS(f"\n📦 Creating Streamlit admin app...")
        )
        self.stdout.write(f"   Path: {output_path}")
        self.stdout.write(f"   Theme: {theme}")
        self.stdout.write(f"   Pages: {'yes' if with_pages else 'no'}\n")

        # Create directory structure
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / ".streamlit").mkdir(exist_ok=True)
        (output_path / "api").mkdir(exist_ok=True)
        (output_path / "components").mkdir(exist_ok=True)
        (output_path / "pages").mkdir(exist_ok=True)

        # Generate config.toml
        theme_gen = ThemeGenerator(theme)
        config_content = theme_gen.generate_config_toml(
            port=8501,
            enable_cors=False,
            enable_xsrf=False,
        )
        (output_path / ".streamlit" / "config.toml").write_text(config_content)
        self.stdout.write(f"   ✅ .streamlit/config.toml")

        # Create API wrapper files
        self._create_api_wrapper(output_path)

        # Copy scaffold files
        self._create_app_py(output_path)
        self._create_requirements(output_path)
        self._create_components(output_path)

        if with_pages:
            self._create_pages(output_path)

        self.stdout.write(
            self.style.SUCCESS(f"\n✅ Streamlit app created at {output_path}")
        )
        self.stdout.write(f"\nNext steps:")
        self.stdout.write(f"  1. Generate Python clients:")
        self.stdout.write(f"     python manage.py generate_client --python --streamlit")
        self.stdout.write(f"  2. Run with Django (auto-starts):")
        self.stdout.write(f"     python manage.py runserver")
        self.stdout.write(f"\nOr run manually:")
        self.stdout.write(f"  python manage.py run_streamlit")

    def _create_api_wrapper(self, output_path: Path) -> None:
        """Create API wrapper module (config, auth, client)."""
        api_path = output_path / "api"

        # api/__init__.py
        init_content = '''"""
Streamlit Admin API.

High-level API wrapper for Streamlit admin applications.

Usage:
    from api import AdminAPI, require_auth, get_base_url

    # Require authentication (stops app if not logged in)
    user = require_auth()

    # Use unified API client
    api = AdminAPI()
    async with api.accounts as client:
        profile = await client.user_profile.profile_retrieve()
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
'''
        (api_path / "__init__.py").write_text(init_content)
        self.stdout.write(f"   ✅ api/__init__.py")

        # api/config.py
        config_content = '''"""
API Configuration.

Handles base URL detection from environment, Streamlit secrets, or defaults.
"""

from __future__ import annotations

import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_base_url() -> str:
    """
    Get Django API base URL.

    Priority:
    1. DJANGO_API_URL environment variable
    2. Streamlit secrets (django_api_url)
    3. Default: http://localhost:8000
    """
    if url := os.getenv("DJANGO_API_URL"):
        return url.rstrip("/")

    try:
        import streamlit as st
        if hasattr(st, "secrets") and "django_api_url" in st.secrets:
            return str(st.secrets["django_api_url"]).rstrip("/")
    except Exception:
        pass

    return "http://localhost:8000"


@lru_cache(maxsize=1)
def get_django_url() -> str:
    """Get Django admin URL (for links, not API calls)."""
    if url := os.getenv("DJANGO_ADMIN_URL"):
        return url.rstrip("/")
    return get_base_url()


DEFAULT_BASE_URL = get_base_url()
'''
        (api_path / "config.py").write_text(config_content)
        self.stdout.write(f"   ✅ api/config.py")

        # api/auth.py
        auth_content = '''"""
Streamlit Authentication Utilities.

Handles JWT token management using existing accounts API.
"""

from __future__ import annotations

from typing import Any

import streamlit as st
import jwt

from .config import get_base_url


TOKEN_KEY = "auth_token"
REFRESH_TOKEN_KEY = "refresh_token"
USER_INFO_KEY = "user_info"


def get_token() -> str | None:
    """Get JWT access token from session state or query params."""
    if TOKEN_KEY in st.session_state:
        return st.session_state[TOKEN_KEY]

    if token := st.query_params.get("token"):
        set_token(token)
        st.query_params.clear()
        return token

    return None


def set_token(access_token: str, refresh_token: str | None = None) -> None:
    """Store JWT tokens in session state."""
    st.session_state[TOKEN_KEY] = access_token
    if refresh_token:
        st.session_state[REFRESH_TOKEN_KEY] = refresh_token

    try:
        payload = jwt.decode(access_token, options={"verify_signature": False})
        st.session_state[USER_INFO_KEY] = payload
    except jwt.InvalidTokenError:
        pass


def clear_token() -> None:
    """Clear all auth tokens and user info from session."""
    for key in [TOKEN_KEY, REFRESH_TOKEN_KEY, USER_INFO_KEY]:
        if key in st.session_state:
            del st.session_state[key]


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return get_token() is not None


def get_user_info() -> dict[str, Any] | None:
    """Get user info from decoded JWT."""
    if USER_INFO_KEY in st.session_state:
        return st.session_state[USER_INFO_KEY]

    token = get_token()
    if not token:
        return None

    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        st.session_state[USER_INFO_KEY] = payload
        return payload
    except jwt.InvalidTokenError:
        return None


def refresh_token() -> str | None:
    """Refresh JWT token using refresh_token from session."""
    refresh = st.session_state.get(REFRESH_TOKEN_KEY)
    if not refresh:
        return None

    try:
        import httpx
        response = httpx.post(
            f"{get_base_url()}/cfg/accounts/token/refresh/",
            json={"refresh": refresh},
            headers={"Content-Type": "application/json"},
            timeout=10.0,
        )

        if response.status_code == 200:
            data = response.json()
            new_access = data.get("access")
            new_refresh = data.get("refresh", refresh)
            if new_access:
                set_token(new_access, new_refresh)
                return new_access

    except Exception:
        pass

    return None


def require_auth() -> dict[str, Any]:
    """Require authentication. Stops the app if not authenticated."""
    token = get_token()

    if not token:
        st.error("Authentication required. Please log in through Django admin.")
        st.info(
            f"Visit [Django Admin]({get_base_url()}/admin/) to log in, "
            f"then access Streamlit admin from there."
        )
        st.stop()

    try:
        payload = jwt.decode(token, options={"verify_signature": False})

        import time
        if exp := payload.get("exp"):
            if exp < time.time():
                if not refresh_token():
                    clear_token()
                    st.error("Session expired. Please log in again.")
                    st.stop()
                payload = get_user_info() or payload

        st.session_state[USER_INFO_KEY] = payload
        return payload

    except jwt.InvalidTokenError as e:
        clear_token()
        st.error(f"Invalid token: {e}")
        st.stop()


def logout() -> None:
    """Log out user and redirect to Django admin."""
    clear_token()
    st.success("Logged out successfully.")
    st.info(f"[Return to Django Admin]({get_base_url()}/admin/)")
'''
        (api_path / "auth.py").write_text(auth_content)
        self.stdout.write(f"   ✅ api/auth.py")

        # api/client.py
        client_content = '''"""
High-level Admin API Client.

Provides unified access to all generated API clients with automatic authentication.
"""

from __future__ import annotations

from typing import Any

from .config import get_base_url
from .auth import get_token


class AdminAPI:
    """
    Unified Admin API Client.

    Provides lazy-loaded access to all API clients with automatic
    token injection from Streamlit session state.

    Example:
        api = AdminAPI()

        async with api.accounts as client:
            profile = await client.user_profile.profile_retrieve()
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
    ):
        self._base_url = base_url or get_base_url()
        self._token = token
        self._clients: dict[str, Any] = {}

    @property
    def token(self) -> str | None:
        """Get current token (from session or provided)."""
        if self._token:
            return self._token
        return get_token()

    @property
    def base_url(self) -> str:
        """Get base URL."""
        return self._base_url

    def _get_or_create_api(self, name: str, api_class: type) -> Any:
        """Get or create API client with token."""
        if name not in self._clients:
            api = api_class(self._base_url)
            if token := self.token:
                api.set_token(token)
            self._clients[name] = api
        return self._clients[name]

    def refresh_tokens(self) -> None:
        """Refresh tokens in all cached clients."""
        token = self.token
        for client in self._clients.values():
            if token:
                client.set_token(token)
            else:
                client.clear_tokens()

    @property
    def accounts(self) -> Any:
        """Accounts API (auth, profile, OAuth)."""
        try:
            from .generated.cfg_accounts import API
            return self._get_or_create_api("accounts", API)
        except ImportError:
            raise ImportError(
                "Generated clients not found. Run: "
                "python manage.py generate_client --python --streamlit"
            )

    @property
    def health(self) -> Any:
        """Health check API."""
        try:
            from .generated.cfg_health import API
            return self._get_or_create_api("health", API)
        except ImportError:
            raise ImportError("cfg_health client not found")

    @property
    def rq(self) -> Any:
        """RQ (Redis Queue) API."""
        try:
            from .generated.cfg_rq import API
            return self._get_or_create_api("rq", API)
        except ImportError:
            raise ImportError("cfg_rq client not found")

    @property
    def totp(self) -> Any:
        """TOTP (2FA) API."""
        try:
            from .generated.cfg_totp import API
            return self._get_or_create_api("totp", API)
        except ImportError:
            raise ImportError("cfg_totp client not found")

    @property
    def centrifugo(self) -> Any:
        """Centrifugo (WebSocket) API."""
        try:
            from .generated.cfg_centrifugo import API
            return self._get_or_create_api("centrifugo", API)
        except ImportError:
            raise ImportError("cfg_centrifugo client not found")

    @property
    def grpc(self) -> Any:
        """gRPC API."""
        try:
            from .generated.cfg_grpc import API
            return self._get_or_create_api("grpc", API)
        except ImportError:
            raise ImportError("cfg_grpc client not found")

    @property
    def cfg(self) -> Any:
        """Full CFG API (all cfg endpoints combined)."""
        try:
            from .generated.cfg import API
            return self._get_or_create_api("cfg", API)
        except ImportError:
            raise ImportError("cfg client not found")
'''
        (api_path / "client.py").write_text(client_content)
        self.stdout.write(f"   ✅ api/client.py")

    def _create_app_py(self, output_path: Path) -> None:
        """Create main app.py file."""
        content = '''"""
Django-CFG Streamlit Admin Panel.

Main entry point for the Streamlit admin application.
Run with: streamlit run app.py
"""

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Admin Panel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Import from api module
from api import require_auth, AdminAPI, logout

# Check authentication (stops if not logged in)
user = require_auth()

# If we get here, user is authenticated
st.sidebar.success(f"Logged in as: {user.get('username', 'Unknown')}")

# Logout button in sidebar
if st.sidebar.button("Logout"):
    logout()
    st.rerun()

# Main page content
st.title("Admin Dashboard")

st.markdown("""
Welcome to the admin panel. Use the sidebar to navigate between pages.

## Quick Stats

Use the navigation on the left to:
- **Dashboard** — View system metrics and stats
- **Users** — Manage user accounts
- **Settings** — Configure application settings
""")

# Example metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Users", "1,234", "+12")

with col2:
    st.metric("Active Sessions", "89", "-3")

with col3:
    st.metric("API Requests", "45.2k", "+2.1k")

with col4:
    st.metric("Error Rate", "0.12%", "-0.03%")

# Example API usage (uncomment after generating clients)
# api = AdminAPI()
# async with api.health as client:
#     health = await client.health.drf_retrieve()
#     st.json(health)

# Footer
st.divider()
st.caption("Powered by Django-CFG + Streamlit")
'''
        (output_path / "app.py").write_text(content)
        self.stdout.write(f"   ✅ app.py")

    def _create_requirements(self, output_path: Path) -> None:
        """Create requirements.txt file."""
        content = '''# Streamlit Admin Requirements
# Install with: pip install -r requirements.txt

# Core
streamlit>=1.32.0
pandas>=2.0.0
httpx>=0.27.0

# Authentication
PyJWT>=2.8.0

# Optional: Enhanced components
# streamlit-extras>=0.4.0
'''
        (output_path / "requirements.txt").write_text(content)
        self.stdout.write(f"   ✅ requirements.txt")

    def _create_components(self, output_path: Path) -> None:
        """Create components directory with utilities."""
        # __init__.py
        init_content = '''"""
Streamlit admin components.

Note: Auth and API client are now in the api/ module.
This module contains additional UI components.
"""

from .utils import show_error, show_success, confirm_action

__all__ = [
    "show_error",
    "show_success",
    "confirm_action",
]
'''
        (output_path / "components" / "__init__.py").write_text(init_content)

        # utils.py - UI utilities
        utils_content = '''"""
UI Utility components for Streamlit admin.
"""

import streamlit as st
from typing import Any, Callable


def show_error(message: str, details: Any = None) -> None:
    """Show error message with optional details."""
    st.error(message)
    if details:
        with st.expander("Error Details"):
            if isinstance(details, dict):
                st.json(details)
            else:
                st.code(str(details))


def show_success(message: str, data: Any = None) -> None:
    """Show success message with optional data."""
    st.success(message)
    if data:
        with st.expander("Details"):
            if isinstance(data, dict):
                st.json(data)
            else:
                st.write(data)


def confirm_action(
    label: str,
    action: Callable[[], Any],
    warning: str = "Are you sure?",
) -> Any:
    """Show confirmation dialog before action."""
    col1, col2 = st.columns([1, 4])

    with col1:
        if st.button(label, type="primary"):
            st.session_state[f"confirm_{label}"] = True

    if st.session_state.get(f"confirm_{label}"):
        st.warning(warning)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, proceed", key=f"yes_{label}"):
                del st.session_state[f"confirm_{label}"]
                return action()
        with col2:
            if st.button("Cancel", key=f"cancel_{label}"):
                del st.session_state[f"confirm_{label}"]
                st.rerun()

    return None
'''
        (output_path / "components" / "utils.py").write_text(utils_content)
        self.stdout.write(f"   ✅ components/utils.py")

    def _create_pages(self, output_path: Path) -> None:
        """Create example pages."""
        # pages/__init__.py
        (output_path / "pages" / "__init__.py").write_text("")

        # 01_users.py
        users_content = '''"""
Users Management Page.

Example CRUD page using API client.
"""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api import require_auth, AdminAPI

user = require_auth()

st.title("Users Management")
st.caption(f"Logged in as: {user.get('username', 'Unknown')}")


# Initialize API client
api = AdminAPI()


tab_list, tab_profile = st.tabs(["User List", "My Profile"])

with tab_list:
    st.subheader("All Users")
    st.info("User list requires admin API endpoints. This is a placeholder.")

with tab_profile:
    st.subheader("My Profile")

    # Display current user info from JWT
    st.json({
        "user_id": user.get("user_id"),
        "username": user.get("username"),
        "email": user.get("email"),
        "is_staff": user.get("is_staff"),
        "is_superuser": user.get("is_superuser"),
    })

    # Example: Fetch profile from API (uncomment after client generation)
    # import asyncio
    #
    # async def get_profile():
    #     async with api.accounts as client:
    #         return await client.user_profile.profile_retrieve()
    #
    # if st.button("Refresh Profile"):
    #     profile = asyncio.run(get_profile())
    #     st.json(profile)
'''
        (output_path / "pages" / "01_users.py").write_text(users_content)
        self.stdout.write(f"   ✅ pages/01_users.py")

        # 02_settings.py
        settings_content = '''"""
Settings Page.

Application settings and configuration.
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api import require_auth, logout, get_base_url

user = require_auth()

if not user.get("is_superuser"):
    st.error("Access denied. Superuser privileges required.")
    st.stop()

st.title("Settings")
st.caption(f"Logged in as: {user.get('username', 'Unknown')}")

# API Configuration (read-only display)
st.subheader("API Configuration")

st.text_input(
    "API Base URL",
    value=get_base_url(),
    disabled=True,
    help="Set via DJANGO_API_URL env var or Streamlit secrets",
)

# Session Info
st.divider()
st.subheader("Session Information")

st.json({
    "user_id": user.get("user_id"),
    "username": user.get("username"),
    "email": user.get("email"),
    "is_staff": user.get("is_staff"),
    "is_superuser": user.get("is_superuser"),
})

# Logout
st.divider()

if st.button("Logout", type="secondary"):
    logout()
    st.rerun()
'''
        (output_path / "pages" / "02_settings.py").write_text(settings_content)
        self.stdout.write(f"   ✅ pages/02_settings.py")
