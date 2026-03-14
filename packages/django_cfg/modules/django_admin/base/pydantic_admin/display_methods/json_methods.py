"""
Auto-display methods for Django JSONField.

Overrides the default JSON renderer to use ensure_ascii=False (proper Unicode)
and Pygments syntax highlighting.
"""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any, Dict, Tuple

from django.utils.safestring import SafeString, mark_safe

if TYPE_CHECKING:
    from ....config import AdminConfig

logger = logging.getLogger(__name__)


def highlight_json(json_obj: Any) -> SafeString:
    """
    Apply syntax highlighting to JSON using Pygments (Unfold style).

    Returns dual-theme HTML: light uses 'colorful', dark uses 'monokai'.
    Falls back to plain escaped JSON when Pygments is not installed.
    """
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import JsonLexer
    except ImportError:
        import html as html_lib
        formatted_json = json.dumps(json_obj, indent=2, ensure_ascii=False)
        return mark_safe(html_lib.escape(formatted_json))  # type: ignore[return-value]

    def _format(response: str, theme: str) -> str:
        formatter = HtmlFormatter(
            style=theme,
            noclasses=True,
            nobackground=True,
            prestyles="white-space: pre-wrap; word-wrap: break-word;",
        )
        return highlight(response, JsonLexer(), formatter)

    response = json.dumps(json_obj, indent=2, ensure_ascii=False)
    return mark_safe(  # type: ignore[return-value]
        f'<div class="block dark:hidden">{_format(response, "colorful")}</div>'
        f'<div class="hidden dark:block">{_format(response, "monokai")}</div>'
    )


def create_jsonfield_display_methods(
    cls: Any,
    config: AdminConfig,
) -> Tuple[list[str], Dict[str, str]]:
    """
    Auto-create display methods for readonly JSONField fields.

    Django's default display_for_field() uses ensure_ascii=True, which escapes
    Unicode. This override uses ensure_ascii=False + Pygments highlighting.

    Returns:
        (updated_readonly_fields, {field_name: method_name})
    """
    model = config.model
    if not model:
        return list(config.readonly_fields), {}

    updated: list[str] = []
    replacements: Dict[str, str] = {}

    for field_name in config.readonly_fields:
        try:
            field = model._meta.get_field(field_name)  # type: ignore[union-attr]
            if field.__class__.__name__ == "JSONField":
                method_name = f"_auto_display_{field_name}"
                setattr(cls, method_name, _make_json_method(field_name, field))
                replacements[field_name] = method_name
                updated.append(method_name)
                logger.debug("Created JSON display method '%s' for '%s'", method_name, field_name)
            else:
                updated.append(field_name)
        except Exception as exc:
            logger.debug("Skipped JSON display for '%s': %s", field_name, exc)
            updated.append(field_name)

    return updated, replacements


def _make_json_method(fname: str, field_obj: Any) -> Any:
    def json_display_method(self: Any, obj: Any) -> SafeString | str:
        """Display JSONField with proper Unicode support."""
        json_value = getattr(obj, fname, None)
        if not json_value:
            return "—"
        try:
            parsed = json.loads(json_value) if isinstance(json_value, str) else json_value
            return mark_safe(highlight_json(parsed))  # type: ignore[return-value]
        except (json.JSONDecodeError, TypeError, ValueError):
            return mark_safe(f"<code>Invalid JSON: {str(json_value)[:100]}</code>")  # type: ignore[return-value]

    json_display_method.short_description = (  # type: ignore[attr-defined]
        getattr(field_obj, "verbose_name", None) or fname.replace("_", " ").title()
    )
    return json_display_method
