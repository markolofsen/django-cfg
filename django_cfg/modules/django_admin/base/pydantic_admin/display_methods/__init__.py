"""
Display method creators — auto-creates Django admin display methods from field configs.

Public API (same as the former display_methods.py):
    highlight_json
    create_jsonfield_display_methods
    create_imagefield_display_methods
    create_markdownfield_display_methods
    create_toonfield_display_methods
    apply_replacements_to_fieldsets
"""

from .fieldsets import apply_replacements_to_fieldsets
from .image_methods import create_imagefield_display_methods
from .json_methods import create_jsonfield_display_methods, highlight_json
from .markdown_methods import create_markdownfield_display_methods
from .toon_methods import create_toonfield_display_methods

__all__ = [
    "highlight_json",
    "create_jsonfield_display_methods",
    "create_imagefield_display_methods",
    "create_markdownfield_display_methods",
    "create_toonfield_display_methods",
    "apply_replacements_to_fieldsets",
]
