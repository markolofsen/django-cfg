"""DateTime display utilities."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from ...models.display_models import DateTimeDisplayConfig

logger = logging.getLogger(__name__)


class DateTimeDisplay:
    """DateTime display utilities."""

    _display_tz = None  # cached display timezone

    @classmethod
    def _get_display_timezone(cls):
        """
        Get timezone for admin display (cached).

        Priority:
        1. DjangoConfig.admin_timezone (if configured)
        2. System timezone via tzlocal (fallback)
        """
        if cls._display_tz is None:
            try:
                from django.apps import apps
                if apps.ready:
                    from ....modules.base import BaseCfgModule
                    config = BaseCfgModule.get_config()
                    if config and hasattr(config, 'admin_timezone') and config.admin_timezone:
                        from zoneinfo import ZoneInfo
                        cls._display_tz = ZoneInfo(config.admin_timezone)
                        return cls._display_tz
            except Exception:
                pass

            from tzlocal import get_localzone
            cls._display_tz = get_localzone()

        return cls._display_tz

    @classmethod
    def reset_timezone_cache(cls) -> None:
        """Reset timezone cache (useful for testing or config changes)."""
        cls._display_tz = None

    @classmethod
    def _to_local(cls, dt: datetime, use_local_tz: bool = True) -> datetime:
        """Convert datetime to display timezone if needed."""
        if not dt:
            return dt
        if use_local_tz and timezone.is_aware(dt):
            return dt.astimezone(cls._get_display_timezone())
        return dt

    @classmethod
    def _get_tz_abbrev(cls, dt: datetime) -> str:
        """Get timezone abbreviation (e.g., UTC, KST, MSK)."""
        if not dt or not timezone.is_aware(dt):
            return ""
        try:
            return dt.strftime('%Z') or dt.tzinfo.tzname(dt) or ""  # type: ignore[union-attr]
        except Exception:
            return ""

    @classmethod
    def relative(cls, dt: Optional[datetime], config: Optional[DateTimeDisplayConfig] = None) -> SafeString:
        """Display with relative time."""
        config = config or DateTimeDisplayConfig()

        if not dt:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        display_dt = cls._to_local(dt, config.use_local_tz)
        date_str = display_dt.strftime("%Y-%m-%d")
        time_str = display_dt.strftime("%H:%M:%S")
        tz_abbrev = cls._get_tz_abbrev(display_dt)
        relative_time = naturaltime(dt)

        if config.show_relative:
            return format_html(
                '<div class="text-xs" style="white-space: nowrap;">'
                '<div class="font-medium">{}</div>'
                '<div class="text-font-subtle-light dark:text-font-subtle-dark">{} {}</div>'
                '<div class="text-font-subtle-light dark:text-font-subtle-dark">{}</div>'
                '</div>',
                escape(date_str), escape(time_str), escape(tz_abbrev), escape(relative_time),
            )

        return format_html(
            '<div class="text-xs" style="white-space: nowrap;">'
            '<div class="font-medium">{}</div>'
            '<div class="text-font-subtle-light dark:text-font-subtle-dark">{} {}</div>'
            '</div>',
            escape(date_str), escape(time_str), escape(tz_abbrev),
        )

    @classmethod
    def compact(cls, dt: Optional[datetime], config: Optional[DateTimeDisplayConfig] = None) -> SafeString:
        """Compact datetime display."""
        config = config or DateTimeDisplayConfig()

        if not dt:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        display_dt = cls._to_local(dt, config.use_local_tz)
        tz_abbrev = cls._get_tz_abbrev(display_dt)

        now = timezone.now()
        diff = now - dt

        if diff.days < 1:
            display_text = naturaltime(dt)
        elif diff.days < 7:
            display_text = display_dt.strftime('%a %H:%M')
        else:
            display_text = display_dt.strftime('%m/%d/%y')

        full_time = f"{display_dt.strftime(config.datetime_format)} {tz_abbrev}".strip()

        return format_html(
            '<span class="text-xs text-font-default-light dark:text-font-default-dark" title="{}">{}</span>',
            escape(full_time), escape(display_text),
        )
