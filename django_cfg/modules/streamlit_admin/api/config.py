"""
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
