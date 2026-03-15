"""Country display utility."""
from __future__ import annotations

from typing import Any

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from .._types import CountryDisplayConfig


class CountryDisplay:
    """
    Display country with flag emoji in admin list views.

    Shows: 🇰🇷 South Korea
    """

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: CountryDisplayConfig | None = None) -> SafeString:
        """
        Render country field with flag.

        Config: show_flag (True), show_name (True), show_code (False)
        """
        cfg: CountryDisplayConfig = config or {}
        value = getattr(obj, field_name, None)

        if not value:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        show_flag = cfg.get("show_flag", True)
        show_name = cfg.get("show_name", True)
        show_code = cfg.get("show_code", False)

        if hasattr(value, "iso2"):
            return cls._format_model(value, show_flag, show_name, show_code)
        if isinstance(value, str) and len(value) == 2:
            return cls._format_code(value, show_flag, show_name, show_code)

        return format_html('<span>{}</span>', escape(str(value)))

    @classmethod
    def _format_model(cls, country: Any, show_flag: bool, show_name: bool, show_code: bool) -> SafeString:
        parts = []
        if show_flag:
            emoji = getattr(country, "emoji", "")
            if emoji:
                parts.append(format_html('<span>{}</span>', emoji))
        if show_name:
            parts.append(format_html('<span class="font-medium">{}</span>', country.name))
        elif show_code:
            parts.append(format_html('<span class="font-medium">{}</span>', country.iso2))
        if show_code and show_name:
            parts.append(format_html('<span class="text-base-400">({})</span>', country.iso2))

        return format_html(
            '<span class="flex items-center gap-2">{}</span>',
            format_html(" ".join(str(p) for p in parts)),
        )

    @classmethod
    def _format_code(cls, code: str, show_flag: bool, show_name: bool, show_code: bool) -> SafeString:
        try:
            from django_cfg.apps.tools.geo.services.database import get_geo_db
            country = get_geo_db().get_country(code)
            if country:
                parts = []
                if show_flag and country.emoji:
                    parts.append(format_html('<span>{}</span>', country.emoji))
                if show_name:
                    parts.append(format_html('<span class="font-medium">{}</span>', country.name))
                elif show_code:
                    parts.append(format_html('<span class="font-medium">{}</span>', code))
                if show_code and show_name:
                    parts.append(format_html('<span class="text-base-400">({})</span>', code))
                return format_html(
                    '<span class="flex items-center gap-2">{}</span>',
                    format_html(" ".join(str(p) for p in parts)),
                )
        except Exception:
            pass
        return format_html('<span class="font-medium">{}</span>', code)
