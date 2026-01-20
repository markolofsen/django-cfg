"""
Geo widgets using Unfold admin styling.

Provides Select2-compatible autocomplete widgets for country and city selection,
as well as a rich LocationField widget with MapLibre map.
"""

import json
from typing import Any, Optional

from django.conf import settings
from django.forms import Select
from django.urls import reverse

from unfold.widgets import AutocompleteWidgetMixin

from .location_widget import LocationFieldWidget


class GeoAutocompleteWidget(AutocompleteWidgetMixin, Select):
    """
    Base autocomplete widget for geo fields.

    Uses Unfold styling with Select2 for AJAX search.
    """

    option_template_name = "unfold/widgets/select_option_autocomplete.html"
    url_name: str = ""

    def __init__(
        self,
        attrs: Optional[dict[str, Any]] = None,
        choices: tuple | list = (),
    ) -> None:
        self.is_required = False  # Set before calling super
        super().__init__(attrs, choices)

    def build_attrs(
        self,
        base_attrs: dict[str, Any],
        extra_attrs: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        attrs = super().build_attrs(base_attrs, extra_attrs)

        # Add AJAX URL
        if self.url_name:
            try:
                attrs["data-ajax--url"] = reverse(self.url_name)
            except Exception:
                pass

        return attrs


class CountrySelectWidget(GeoAutocompleteWidget):
    """
    Select2 widget for country selection.

    Features:
    - AJAX search via cfg_geo:search-countries endpoint
    - Displays country name with flag emoji
    - Stores ISO2 code as value

    Usage in forms:
        class MyForm(forms.Form):
            country = forms.CharField(widget=CountrySelectWidget())

    Usage in ModelAdmin:
        formfield_overrides = {
            CountryField: {"widget": CountrySelectWidget},
        }
    """

    url_name = "cfg_geo:search-countries"

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "unfold/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


class CitySelectWidget(GeoAutocompleteWidget):
    """
    Select2 widget for city selection.

    Features:
    - AJAX search via cfg_geo:search-cities endpoint
    - Requires minimum 2 characters for search
    - Displays city name with state/country
    - Stores city ID as value

    Usage in forms:
        class MyForm(forms.Form):
            city = forms.IntegerField(widget=CitySelectWidget())

    Usage in ModelAdmin:
        formfield_overrides = {
            CityField: {"widget": CitySelectWidget},
        }
    """

    url_name = "cfg_geo:search-cities"

    def __init__(
        self,
        attrs: Optional[dict[str, Any]] = None,
        choices: tuple | list = (),
        country_code: Optional[str] = None,
    ) -> None:
        self.country_code = country_code
        super().__init__(attrs, choices)

    def build_attrs(
        self,
        base_attrs: dict[str, Any],
        extra_attrs: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        attrs = super().build_attrs(base_attrs, extra_attrs)

        # Set minimum input length for search
        attrs["data-minimum-input-length"] = 2

        # Add country filter if specified
        if self.country_code:
            attrs["data-ajax--data"] = json.dumps({"country": self.country_code})

        return attrs

    class Media:
        extra = "" if settings.DEBUG else ".min"
        js = (
            f"admin/js/vendor/jquery/jquery{extra}.js",
            "admin/js/vendor/select2/select2.full.js",
            "admin/js/jquery.init.js",
            "unfold/js/select2.init.js",
        )
        css = {
            "screen": (
                "admin/css/vendor/select2/select2.css",
                "admin/css/autocomplete.css",
            ),
        }


__all__ = [
    "GeoAutocompleteWidget",
    "CountrySelectWidget",
    "CitySelectWidget",
    "LocationFieldWidget",
]
