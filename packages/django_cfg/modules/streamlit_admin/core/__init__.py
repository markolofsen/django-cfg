"""Streamlit Admin core functionality."""

from .runner import StreamlitRunner
from .theme import ThemeGenerator, THEMES
from .client_copier import StreamlitClientCopier
from .autostart import (
    StreamlitAutoStart,
    auto_start_streamlit,
    should_auto_start,
)
from .registry import PageRegistry, PageConfig, MenuGroup, page_registry
from .router import PageRouter, RouteConfig

__all__ = [
    "StreamlitRunner",
    "ThemeGenerator",
    "THEMES",
    "StreamlitClientCopier",
    "StreamlitAutoStart",
    "auto_start_streamlit",
    "should_auto_start",
    "PageRegistry",
    "PageConfig",
    "MenuGroup",
    "page_registry",
    "PageRouter",
    "RouteConfig",
]
