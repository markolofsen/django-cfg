"""
Auto-display methods for MarkdownField (readonly_fields on change form).

Renders field values as collapsible, plugin-aware markdown docs using
MarkdownIntegration.markdown_docs().
"""
from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any, Dict, Tuple

from django.utils.safestring import SafeString, mark_safe

if TYPE_CHECKING:
    from ....config import AdminConfig

logger = logging.getLogger(__name__)


def create_markdownfield_display_methods(
    cls: Any,
    readonly_fields: list[str],
    config: AdminConfig,
) -> Tuple[list[str], Dict[str, str]]:
    """
    Auto-create display methods for fields with MarkdownField config.

    Scans display_fields for MarkdownField entries that are also in
    readonly_fields and creates a display method rendering markdown.

    Returns:
        (updated_readonly_fields, {field_name: method_name})
    """
    from ....config.field_config.markdown import MarkdownField

    if not config.display_fields:
        return list(readonly_fields), {}

    updated = list(readonly_fields)
    replacements: Dict[str, str] = {}

    for field_config in config.display_fields:
        if not isinstance(field_config, MarkdownField):
            continue

        field_name = field_config.name
        if field_name not in readonly_fields:
            continue

        method_name = f"{field_name}_md_display"
        title = field_config.title or field_name.replace("_", " ").title()

        method = _make_markdown_method(
            fname=field_name,
            title=title,
            collapsible=field_config.collapsible,
            default_open=field_config.default_open,
            max_height=field_config.max_height,
            icon=field_config.header_icon,
            enable_plugins=field_config.enable_plugins,
            full_width=field_config.full_width,
        )
        setattr(cls, method_name, method)
        replacements[field_name] = method_name

        try:
            updated[updated.index(field_name)] = method_name
        except ValueError:
            pass

        logger.debug("Created markdown display method '%s' for '%s'", method_name, field_name)

    return updated, replacements


def _make_markdown_method(
    fname: str,
    title: str,
    collapsible: bool,
    default_open: bool,
    max_height: str,
    icon: str | None,
    enable_plugins: bool,
    full_width: bool,
) -> Any:
    from ....utils.html.markdown_integration import MarkdownIntegration

    def display_method(self: Any, obj: Any) -> SafeString | str:
        value = getattr(obj, fname, None)
        if not value:
            return mark_safe('<span class="text-gray-400 italic">—</span>')  # type: ignore[return-value]

        content = MarkdownIntegration.markdown_docs(
            content=value,
            collapsible=collapsible,
            title=title,
            icon=icon or "description",
            max_height=max_height,
            enable_plugins=enable_plugins,
            default_open=default_open,
        )

        if not full_width:
            return content

        uid = str(uuid.uuid4())[:8]
        return mark_safe(  # type: ignore[return-value]
            f'<div id="md-{uid}" class="markdown-full-width">'
            f"{content}"
            f"</div>"
            f"<style>"
            f".readonly:has(#md-{uid}) {{ max-width: none !important; width: 100% !important; }}"
            f"#md-{uid} {{ width: 100% !important; }}"
            f"</style>"
        )

    display_method.short_description = title  # type: ignore[attr-defined]
    return display_method
