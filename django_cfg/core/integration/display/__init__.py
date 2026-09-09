"""
Django CFG Display System.

Modular, class-based display system for startup information.
"""

from .base import BaseDisplayManager
from .startup import StartupDisplayManager
from .banner import get_banner, print_banner, get_available_styles
from .ai_hints import AIHintsDisplayManager, get_ai_hints_manager, AI_HINTS

__all__ = [
    "BaseDisplayManager",
    "StartupDisplayManager",
    "AIHintsDisplayManager",
    "get_ai_hints_manager",
    "AI_HINTS",
    "get_banner",
    "print_banner",
    "get_available_styles",
]
