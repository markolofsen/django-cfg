"""
Flash message support for PydanticAdmin.

Provides one-time HTML message display for sensitive data (API keys, passwords,
tokens) that needs to be shown once after object creation and never again.

Usage (imperative):
    class MyAdmin(PydanticAdmin):
        def save_model(self, request, obj, form, change):
            super().save_model(request, obj, form, change)
            if not change and hasattr(obj, '_generated_plain_key'):
                self.flash_once(
                    request, obj,
                    field_name='plain_key_display',
                    content=obj._generated_plain_key,
                    title='Plain API Key (One-Time Display)',
                    message='SAVE THIS KEY NOW - You will not see it again!',
                    style='code_warning',
                )

Usage (declarative):
    class MyAdmin(PydanticAdmin):
        one_time_flash_fields = {
            'plain_key_display': {
                'source': '_generated_plain_key',
                'style': 'code_warning',
                'title': 'Plain API Key (One-Time Display)',
                'message': 'SAVE THIS KEY NOW',
            }
        }
"""

import logging
from typing import Any, Callable, Optional

from django.http import HttpRequest
from django.db import models
from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from .flash_config import FlashPayload, FlashStyle

logger = logging.getLogger(__name__)

SESSION_KEY_PREFIX = '_pydantic_admin_flash'

# Type alias for style renderer functions
StyleRenderer = Callable[[str, str, str], Any]


# ---------------------------------------------------------------------------
# Style renderers — all use format_html() for XSS safety
# ---------------------------------------------------------------------------

def _render_code_warning(content: str, title: str, message: str) -> Any:
    header = format_html(
        '<p style="color:#dc2626;font-weight:bold;margin:0 0 4px 0;">{}</p>'
        '<p style="color:#856404;margin:0 0 8px 0;font-size:13px;">{}</p>',
        title, message,
    ) if (title or message) else mark_safe('')
    return format_html(
        '<div style="padding:16px 20px;background:#fff3cd;border:3px solid #ffc107;'
        'border-radius:6px;margin-bottom:8px;">'
        '{}'
        '<div style="background:#1f2937;padding:16px 20px;border-radius:4px;margin-top:8px;">'
        '<code style="color:#10b981;font-family:monospace;font-size:13px;word-break:break-all;">{}</code>'
        '</div></div>',
        header, content,
    )


def _render_code_error(content: str, title: str, message: str) -> Any:
    header = format_html(
        '<p style="color:#dc2626;font-weight:bold;margin:0 0 4px 0;">{}</p>'
        '<p style="color:#991b1b;margin:0 0 8px 0;font-size:13px;">{}</p>',
        title, message,
    ) if (title or message) else mark_safe('')
    return format_html(
        '<div style="padding:16px 20px;background:#fee2e2;border:3px solid #ef4444;'
        'border-radius:6px;margin-bottom:8px;">'
        '{}'
        '<div style="background:#1f2937;padding:16px 20px;border-radius:4px;margin-top:8px;">'
        '<code style="color:#f87171;font-family:monospace;font-size:13px;word-break:break-all;">{}</code>'
        '</div></div>',
        header, content,
    )


def _render_code_success(content: str, title: str, message: str) -> Any:
    header = format_html(
        '<p style="color:#15803d;font-weight:bold;margin:0 0 4px 0;">{}</p>'
        '<p style="color:#166534;margin:0 0 8px 0;font-size:13px;">{}</p>',
        title, message,
    ) if (title or message) else mark_safe('')
    return format_html(
        '<div style="padding:16px 20px;background:#dcfce7;border:3px solid #22c55e;'
        'border-radius:6px;margin-bottom:8px;">'
        '{}'
        '<div style="background:#1f2937;padding:16px 20px;border-radius:4px;margin-top:8px;">'
        '<code style="color:#4ade80;font-family:monospace;font-size:13px;word-break:break-all;">{}</code>'
        '</div></div>',
        header, content,
    )


def _render_info(content: str, title: str, message: str) -> Any:
    header = format_html(
        '<p style="color:#1d4ed8;font-weight:bold;margin:0 0 4px 0;">{}</p>'
        '<p style="color:#1e40af;margin:0 0 4px 0;font-size:13px;">{}</p>',
        title, message,
    ) if (title or message) else mark_safe('')
    return format_html(
        '<div style="padding:16px 20px;background:#dbeafe;border:2px solid #3b82f6;'
        'border-radius:6px;margin-bottom:8px;">'
        '{}<p style="margin:4px 0 0 0;color:#1e40af;">{}</p></div>',
        header, content,
    )


def _render_warning(content: str, title: str, message: str) -> Any:
    header = format_html(
        '<p style="color:#92400e;font-weight:bold;margin:0 0 4px 0;">{}</p>'
        '<p style="color:#856404;margin:0 0 4px 0;font-size:13px;">{}</p>',
        title, message,
    ) if (title or message) else mark_safe('')
    return format_html(
        '<div style="padding:16px 20px;background:#fff3cd;border:2px solid #ffc107;'
        'border-radius:6px;margin-bottom:8px;">'
        '{}<p style="margin:4px 0 0 0;color:#856404;">{}</p></div>',
        header, content,
    )


def _render_error(content: str, title: str, message: str) -> Any:
    header = format_html(
        '<p style="color:#dc2626;font-weight:bold;margin:0 0 4px 0;">{}</p>'
        '<p style="color:#991b1b;margin:0 0 4px 0;font-size:13px;">{}</p>',
        title, message,
    ) if (title or message) else mark_safe('')
    return format_html(
        '<div style="padding:16px 20px;background:#fee2e2;border:2px solid #ef4444;'
        'border-radius:6px;margin-bottom:8px;">'
        '{}<p style="margin:4px 0 0 0;color:#991b1b;">{}</p></div>',
        header, content,
    )


def _render_success(content: str, title: str, message: str) -> Any:
    header = format_html(
        '<p style="color:#15803d;font-weight:bold;margin:0 0 4px 0;">{}</p>'
        '<p style="color:#166534;margin:0 0 4px 0;font-size:13px;">{}</p>',
        title, message,
    ) if (title or message) else mark_safe('')
    return format_html(
        '<div style="padding:16px 20px;background:#dcfce7;border:2px solid #22c55e;'
        'border-radius:6px;margin-bottom:8px;">'
        '{}<p style="margin:4px 0 0 0;color:#166534;">{}</p></div>',
        header, content,
    )


def _render_raw(content: str, title: str, message: str) -> Any:
    return mark_safe(content)


_FLASH_STYLES: dict[str, StyleRenderer] = {
    'code_warning': _render_code_warning,
    'code_error': _render_code_error,
    'code_success': _render_code_success,
    'info': _render_info,
    'warning': _render_warning,
    'error': _render_error,
    'success': _render_success,
    'raw': _render_raw,
}


# ---------------------------------------------------------------------------
# Display method factory
# ---------------------------------------------------------------------------

def create_flash_display_method(field_name: str, title: str) -> Any:
    """
    Create a readonly display method that reads flash data from session,
    renders it once, and deletes it.

    Args:
        field_name: The name used as readonly field key.
        title: short_description for Django admin column header.

    Returns:
        Callable to be set on the admin class via setattr().
    """
    def flash_display_method(self: Any, obj: Any) -> Any:
        request = getattr(self, '_current_request', None)
        if not request or not obj or not obj.pk:
            return format_html('<span style="color:#9ca3af;">—</span>')

        data = self._consume_flash(request, obj, field_name)
        if not data:
            return format_html('<span style="color:#9ca3af;">—</span>')

        style_key = data.get('style', 'code_warning')
        renderer = _FLASH_STYLES.get(style_key, _render_code_warning)
        return renderer(
            data.get('content', ''),
            data.get('title', ''),
            data.get('message', ''),
        )

    flash_display_method.short_description = title  # type: ignore[attr-defined]
    flash_display_method.__name__ = field_name
    return flash_display_method


# ---------------------------------------------------------------------------
# FlashMixin
# ---------------------------------------------------------------------------

class FlashMixin:
    """
    Mixin providing one-time HTML flash message support for PydanticAdmin.

    Stores sensitive data in Django's session with a unique key per model/pk/field,
    renders it once on the change page, then auto-deletes from session.
    """

    def flash_once(
        self,
        request: HttpRequest,
        obj: models.Model,
        field_name: str,
        content: Any,
        title: str = '',
        message: str = '',
        style: FlashStyle = 'code_warning',
    ) -> None:
        """
        Store flash data in session for one-time display on the change page.

        Call this from save_model() after the object has been created.
        PydanticAdmin automatically injects the field into readonly_fields
        and fieldsets on the next changeform_view() call.

        Args:
            request: Django HTTP request.
            obj: The saved model instance (must have pk).
            field_name: Readonly field name to inject (e.g. 'plain_key_display').
            content: The sensitive content to display (string).
            title: Bold header shown above the content box.
            message: Subtitle/instruction shown below the title.
            style: Visual style key. One of: code_warning, code_error, code_success,
                   info, warning, error, success, raw.
        """
        if not obj or not obj.pk:
            logger.warning('flash_once() called before object has pk — skipping')
            return

        payload = FlashPayload(
            content=str(content),
            title=title,
            message=message,
            style=style,
        )
        key = self._flash_session_key(obj, field_name)
        request.session[key] = payload.model_dump()
        request.session.modified = True
        logger.debug(f'Flash stored: {key}')

    def _flash_session_key(self, obj: models.Model, field_name: str) -> str:
        model_label = obj._meta.label_lower.replace('.', '_')
        return f'{SESSION_KEY_PREFIX}_{model_label}_{obj.pk}_{field_name}'

    def _get_pending_flash_fields(
        self,
        request: HttpRequest,
        obj: models.Model,
    ) -> dict[str, dict[str, Any]]:
        """
        Return {field_name: flash_data} for all pending flashes for this object.
        Does NOT consume — only peeks.
        """
        if not obj or not obj.pk:
            return {}
        model_label = obj._meta.label_lower.replace('.', '_')
        prefix = f'{SESSION_KEY_PREFIX}_{model_label}_{obj.pk}_'
        result: dict[str, dict[str, Any]] = {}
        for key in list(request.session.keys()):
            if key.startswith(prefix):
                field_name = key[len(prefix):]
                result[field_name] = request.session[key]
        return result

    def _consume_flash(
        self,
        request: HttpRequest,
        obj: models.Model,
        field_name: str,
    ) -> Optional[dict[str, Any]]:
        """
        Read flash data from session and immediately delete it (one-time).

        Returns the flash data dict or None if not found.
        """
        key = self._flash_session_key(obj, field_name)
        data = request.session.pop(key, None)
        if data is not None:
            request.session.modified = True
            logger.debug(f'Flash consumed: {key}')
        return data

    @staticmethod
    def _render_flash_html(content: str, title: str, message: str, style: FlashStyle) -> Any:
        """Render flash content as safe HTML using format_html (XSS-safe)."""
        renderer = _FLASH_STYLES.get(style, _render_code_warning)
        return renderer(content, title, message)
