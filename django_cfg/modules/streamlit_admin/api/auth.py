"""
Streamlit Authentication Utilities.

Handles JWT token management using existing accounts API.
Supports cookie persistence for token across page refreshes.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import streamlit as st
import jwt

from .config import get_base_url


TOKEN_KEY = "auth_token"
REFRESH_TOKEN_KEY = "refresh_token"
USER_INFO_KEY = "user_info"
COOKIE_NAME = "stl_admin_token"


def _get_cookie_controller():
    """Get CookieController instance."""
    try:
        from streamlit_cookies_controller import CookieController
        return CookieController(key="auth_cookies")
    except ImportError:
        return None


def get_token() -> str | None:
    """Get JWT access token from session state, query params, or cookies."""
    # 1. Check session state first (fastest)
    if TOKEN_KEY in st.session_state:
        return st.session_state[TOKEN_KEY]

    # 2. Check query params (from Django redirect)
    if token := st.query_params.get("token"):
        set_token(token)
        st.query_params.clear()
        return token

    # 3. Check cookies (persistence across refresh)
    controller = _get_cookie_controller()
    if controller:
        try:
            token = controller.get(COOKIE_NAME)
            if token and isinstance(token, str):
                # Restore to session state
                st.session_state[TOKEN_KEY] = token
                return token
        except (KeyError, TypeError, AttributeError):
            pass  # Cookie doesn't exist or invalid

    return None


def set_token(access_token: str, refresh_token: str | None = None) -> None:
    """Store JWT tokens in session state and cookies."""
    st.session_state[TOKEN_KEY] = access_token
    if refresh_token:
        st.session_state[REFRESH_TOKEN_KEY] = refresh_token

    try:
        payload = jwt.decode(access_token, options={"verify_signature": False})
        st.session_state[USER_INFO_KEY] = payload
    except jwt.InvalidTokenError:
        pass

    # Save to cookie for persistence across refresh (7 days expiry)
    controller = _get_cookie_controller()
    if controller:
        try:
            expires = datetime.now() + timedelta(days=7)
            controller.set(COOKIE_NAME, access_token, expires=expires)
        except Exception:
            pass  # Cookie set failed, continue without persistence


def clear_token() -> None:
    """Clear all auth tokens and user info from session and cookies."""
    for key in [TOKEN_KEY, REFRESH_TOKEN_KEY, USER_INFO_KEY]:
        if key in st.session_state:
            del st.session_state[key]

    # Clear cookie (ignore if doesn't exist)
    controller = _get_cookie_controller()
    if controller:
        try:
            controller.remove(COOKIE_NAME)
        except KeyError:
            pass  # Cookie doesn't exist, nothing to clear


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
