"""
Location field widgets for Django Admin.

Select2-based autocomplete widgets for country and city selection.
Follows the same pattern as MoneyFieldWidget for consistency.
"""

from typing import Any, Dict, List, Optional, Tuple

from django import forms
from django.forms.widgets import Select
from django.urls import reverse
from django.utils.safestring import mark_safe

# Unfold-compatible CSS classes (same as money_widget.py)
INPUT_CLASSES = " ".join([
    "border", "border-base-200", "bg-white", "font-medium", "px-3", "py-2",
    "min-w-20", "placeholder-base-400", "rounded-default", "shadow-xs",
    "text-font-default-light", "text-sm", "w-full",
    "focus:outline-2", "focus:-outline-offset-2", "focus:outline-primary-600",
    "dark:bg-base-900", "dark:border-base-700", "dark:text-font-default-dark",
])

SELECT_CLASSES = " ".join([
    *INPUT_CLASSES.split(),
    "pr-8!", "max-w-2xl", "appearance-none", "text-ellipsis",
])

AUTOCOMPLETE_CLASSES = "unfold-admin-autocomplete admin-autocomplete"


def get_country_choices() -> List[Tuple[str, str]]:
    """
    Get country choices from database.

    Returns list of (iso2, display_name) tuples.
    Falls back to empty list if geo app unavailable.
    """
    try:
        from django_cfg.apps.tools.geo.models import Country

        countries = Country.objects.filter(is_active=True).order_by("name")
        return [
            (c.iso2, f"{c.emoji} {c.name}" if c.emoji else c.name)
            for c in countries
        ]
    except Exception:
        return []


class CountrySelectWidget(Select):
    """
    Country autocomplete select widget for Django Admin.

    Features:
    - AJAX search via cfg_geo:search-countries endpoint
    - Displays country name with flag emoji
    - Stores ISO2 code as value
    - Compatible with Unfold admin styling

    Usage:
        # Auto-applied to CountryField in PydanticAdmin
        # Or manually:
        formfield_overrides = {
            CountryField: {'widget': CountrySelectWidget()}
        }
    """

    template_name = "django_admin/widgets/country_select.html"

    def __init__(
        self,
        attrs: Optional[Dict[str, Any]] = None,
        use_autocomplete: bool = True,
    ):
        self.use_autocomplete = use_autocomplete

        if use_autocomplete:
            default_attrs = {
                "class": AUTOCOMPLETE_CLASSES,
                "data-theme": "admin-autocomplete",
                "data-placeholder": "Select country",
                "data-allow-clear": "true",
            }
        else:
            default_attrs = {"class": SELECT_CLASSES}

        if attrs:
            default_attrs.update(attrs)

        super().__init__(attrs=default_attrs, choices=get_country_choices())

    def get_context(
        self, name: str, value: Any, attrs: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        context = super().get_context(name, value, attrs)

        # Add search URL for AJAX autocomplete
        try:
            context["widget"]["search_url"] = reverse("cfg_geo:search-countries")
        except Exception:
            context["widget"]["search_url"] = ""

        return context

    def format_readonly(self, code: str) -> str:
        """
        Render readonly display with flag.

        Returns HTML: 🇰🇷 South Korea
        """
        if not code:
            return mark_safe('<span class="text-base-400">—</span>')

        try:
            from django_cfg.apps.tools.geo.services.database import get_geo_db

            country = get_geo_db().get_country(code)
            if country:
                flag = country.emoji or ""
                return mark_safe(
                    f'<span class="flex items-center gap-2">'
                    f'<span>{flag}</span>'
                    f'<span class="font-medium">{country.name}</span>'
                    f'</span>'
                )
        except Exception:
            pass

        return code


class CitySelectWidget(Select):
    """
    City autocomplete select widget for Django Admin.

    Features:
    - AJAX search via cfg_geo:search-cities endpoint
    - Requires minimum 2 characters for search
    - Optional country filtering
    - Displays city with state and country
    - Stores city ID as value

    Usage:
        # Auto-applied to CityField in PydanticAdmin
        # Or manually:
        formfield_overrides = {
            CityField: {'widget': CitySelectWidget(country_field='country')}
        }
    """

    template_name = "django_admin/widgets/city_select.html"

    def __init__(
        self,
        attrs: Optional[Dict[str, Any]] = None,
        country_field: Optional[str] = None,
    ):
        """
        Initialize city select widget.

        Args:
            attrs: Additional HTML attributes
            country_field: Name of country field for cascade filtering
        """
        self.country_field = country_field

        default_attrs = {
            "class": AUTOCOMPLETE_CLASSES,
            "data-theme": "admin-autocomplete",
            "data-placeholder": "Search city...",
            "data-minimum-input-length": "2",
            "data-allow-clear": "true",
        }

        if attrs:
            default_attrs.update(attrs)

        super().__init__(attrs=default_attrs, choices=[])

    def get_context(
        self, name: str, value: Any, attrs: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        context = super().get_context(name, value, attrs)

        # Add search URL for AJAX autocomplete
        try:
            context["widget"]["search_url"] = reverse("cfg_geo:search-cities")
        except Exception:
            context["widget"]["search_url"] = ""

        # Add country field name for cascade filtering
        context["widget"]["country_field"] = self.country_field

        # Get initial display value for existing city
        if value:
            context["widget"]["initial_display"] = self._get_initial_display(value)

        return context

    def _get_initial_display(self, city_id: Any) -> str:
        """Get display value for initial city selection."""
        try:
            from django_cfg.apps.tools.geo.models import City

            city = City.objects.select_related("state", "country").get(id=city_id)
            return str(city)
        except Exception:
            return str(city_id)

    def format_readonly(self, city_id: Any) -> str:
        """
        Render readonly display with flag.

        Returns HTML: 🇰🇷 Seoul, 11, KR
        """
        if not city_id:
            return mark_safe('<span class="text-base-400">—</span>')

        try:
            from django_cfg.apps.tools.geo.models import City

            city = City.objects.select_related("state", "country").get(id=city_id)
            flag = city.country.emoji if city.country else ""

            parts = []
            if flag:
                parts.append(f'<span>{flag}</span>')

            parts.append(f'<span class="font-medium">{city.name}</span>')

            if city.state:
                state_code = getattr(city.state, "state_code", None) or city.state.name
                parts.append(f'<span class="text-base-400">{state_code}</span>')

            if city.country:
                parts.append(f'<span class="text-base-400">{city.country.iso2}</span>')

            return mark_safe(
                '<span class="flex items-center gap-2">' +
                ', '.join(parts[1:] if flag else parts) +
                '</span>' if not flag else
                f'<span class="flex items-center gap-2">{parts[0]} ' +
                ', '.join(parts[1:]) +
                '</span>'
            )
        except Exception:
            return str(city_id)


class LocationSelectWidget(CitySelectWidget):
    """
    Location select widget - alias for CitySelectWidget.

    Use with LocationField for full location hierarchy resolution.
    """

    pass


__all__ = [
    "CountrySelectWidget",
    "CitySelectWidget",
    "LocationSelectWidget",
]
