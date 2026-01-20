"""
Widget registry for declarative admin.

Maps ui_widget names to display utilities.
"""

import logging
from typing import Any, Callable, Dict, Optional

from ..models import (
    DateTimeDisplayConfig,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    UserDisplayConfig,
)
from ..utils import (
    AvatarDisplay,
    BooleanDisplay,
    CounterBadge,
    CounterBadgeDisplay,
    DateTimeDisplay,
    ImageDisplay,
    ImagePreviewDisplay,
    JSONDisplay,
    LinkDisplay,
    MoneyDisplay,
    ProgressBadge,
    ShortUUIDDisplay,
    StackedDisplay,
    StatusBadge,
    StatusBadgesDisplay,
    TextDisplay,
    UserDisplay,
)

logger = logging.getLogger(__name__)


class WidgetRegistry:
    """
    Widget registry mapping ui_widget names to render functions.

    Maps declarative widget names to actual display utilities.
    """

    _widgets: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, handler: Callable):
        """Register a custom widget."""
        cls._widgets[name] = handler
        logger.debug(f"Registered widget: {name}")

    @classmethod
    def get(cls, name: str) -> Optional[Callable]:
        """Get widget handler by name."""
        return cls._widgets.get(name)

    @classmethod
    def render(cls, widget_name: str, obj: Any, field_name: str, config: Dict[str, Any]):
        """Render field using specified widget."""
        handler = cls.get(widget_name)

        if handler:
            try:
                return handler(obj, field_name, config)
            except Exception as e:
                logger.error(f"Error rendering widget '{widget_name}': {e}")
                return getattr(obj, field_name, "—")

        # Fallback to field value
        logger.warning(f"Widget '{widget_name}' not found, using field value")
        return getattr(obj, field_name, "—")


# Helper to filter out internal keys from config
def _filter_internal_keys(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Filter out internal keys like 'is_link' before passing to Pydantic models."""
    if not cfg:
        return cfg
    internal_keys = {'is_link'}
    return {k: v for k, v in cfg.items() if k not in internal_keys}


# Register built-in widgets

# User widgets
WidgetRegistry.register(
    "user_avatar",
    lambda obj, field, cfg: UserDisplay.with_avatar(
        getattr(obj, field),
        UserDisplayConfig(**_filter_internal_keys(cfg)) if cfg else None
    )
)

WidgetRegistry.register(
    "user_simple",
    lambda obj, field, cfg: UserDisplay.simple(
        getattr(obj, field),
        UserDisplayConfig(**_filter_internal_keys(cfg)) if cfg else None
    )
)

# Money widgets
WidgetRegistry.register(
    "currency",
    lambda obj, field, cfg: MoneyDisplay.amount(
        getattr(obj, field),
        MoneyDisplayConfig(**_filter_internal_keys(cfg)) if cfg else None
    )
)

WidgetRegistry.register(
    "money_breakdown",
    lambda obj, field, cfg: MoneyDisplay.with_breakdown(
        getattr(obj, field),
        cfg.get('breakdown_items', []),
        MoneyDisplayConfig(**{k: v for k, v in _filter_internal_keys(cfg).items() if k != 'breakdown_items'}) if cfg else None
    )
)


def _render_money_field(obj, field, cfg):
    """
    Render MoneyField with compact display format.

    Uses MoneyFieldWidget.format_readonly() for consistent display
    in list view and readonly forms.
    """
    from .money_widget import MoneyFieldWidget

    field_names = cfg.get('field_names', {}) if cfg else {}
    target_currency = cfg.get('target_currency', 'USD') if cfg else 'USD'
    default_currency = cfg.get('default_currency', 'USD') if cfg else 'USD'

    # Get field values
    amount_field = field_names.get('amount', field)
    currency_field = field_names.get('currency', f'{field}_currency')
    target_field = field_names.get('target', f'{field}_target')
    rate_field = field_names.get('rate', f'{field}_rate')
    rate_at_field = field_names.get('rate_at', f'{field}_rate_at')

    amount = getattr(obj, amount_field, None)
    currency = getattr(obj, currency_field, None) or default_currency
    target_amount = getattr(obj, target_field, None)
    rate = getattr(obj, rate_field, None)
    rate_at = getattr(obj, rate_at_field, None)

    # Use widget for consistent rendering
    widget = MoneyFieldWidget(
        default_currency=default_currency,
        target_currency=target_currency,
    )

    return widget.format_readonly(
        amount=amount,
        currency=currency,
        target_amount=target_amount,
        rate=rate,
        rate_at=rate_at,
    )


WidgetRegistry.register("money_field", _render_money_field)

# Badge widgets
WidgetRegistry.register(
    "badge",
    lambda obj, field, cfg: StatusBadge.auto(
        getattr(obj, field),
        StatusBadgeConfig(**_filter_internal_keys(cfg)) if cfg else None
    )
)

WidgetRegistry.register(
    "progress",
    lambda obj, field, cfg: ProgressBadge.percentage(
        getattr(obj, field)
    )
)

WidgetRegistry.register(
    "counter",
    lambda obj, field, cfg: CounterBadge.simple(
        getattr(obj, field),
        cfg.get('label') if cfg else None
    )
)

# DateTime widgets
WidgetRegistry.register(
    "datetime_relative",
    lambda obj, field, cfg: DateTimeDisplay.relative(
        getattr(obj, field),
        DateTimeDisplayConfig(**_filter_internal_keys(cfg)) if cfg else None
    )
)

WidgetRegistry.register(
    "datetime_compact",
    lambda obj, field, cfg: DateTimeDisplay.compact(
        getattr(obj, field),
        DateTimeDisplayConfig(**_filter_internal_keys(cfg)) if cfg else None
    )
)

# Simple widgets
WidgetRegistry.register(
    "text",
    lambda obj, field, cfg: TextDisplay.from_field(obj, field, cfg or {})
)

WidgetRegistry.register(
    "boolean",
    lambda obj, field, cfg: BooleanDisplay.icon(
        getattr(obj, field, False),
        cfg.get('true_icon') if cfg else None,
        cfg.get('false_icon') if cfg else None
    )
)

# Decimal widget
from ..utils.displays import DecimalDisplay

WidgetRegistry.register(
    "decimal",
    lambda obj, field, cfg: DecimalDisplay.from_field(obj, field, cfg or {})
)


# Register widgets using Display classes
# All render logic moved to utils/displays/ and templates/

WidgetRegistry.register(
    "image",
    lambda obj, field, cfg: ImageDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "json_editor",
    lambda obj, field, cfg: JSONDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "avatar",
    lambda obj, field, cfg: AvatarDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "link",
    lambda obj, field, cfg: LinkDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "status_badges",
    lambda obj, field, cfg: StatusBadgesDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "counter_badge",
    lambda obj, field, cfg: CounterBadgeDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "short_uuid",
    lambda obj, field, cfg: ShortUUIDDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "stacked",
    lambda obj, field, cfg: StackedDisplay.from_field(obj, field, cfg)
)

WidgetRegistry.register(
    "image_preview",
    lambda obj, field, cfg: ImagePreviewDisplay.from_field(obj, field, cfg)
)

# Video widget
from ..utils.displays import VideoDisplay

WidgetRegistry.register(
    "video",
    lambda obj, field, cfg: VideoDisplay.from_field(obj, field, cfg)
)

# Markdown widget
from ..utils.html.markdown_integration import MarkdownIntegration

WidgetRegistry.register(
    "markdown",
    lambda obj, field, cfg: MarkdownIntegration.markdown_docs(
        content=getattr(obj, field, "") or "",
        collapsible=cfg.get('collapsible', True) if cfg else True,
        title=cfg.get('title', 'Documentation') if cfg else 'Documentation',
        icon=cfg.get('header_icon', 'description') if cfg else 'description',
        max_height=cfg.get('max_height', '500px') if cfg else '500px',
        enable_plugins=cfg.get('enable_plugins', True) if cfg else True,
        default_open=cfg.get('default_open', False) if cfg else False,
    )
)


# Geo widgets
def _render_country_field(obj, field, cfg):
    """Render CountryField with flag emoji."""
    from .location_widget import CountrySelectWidget

    code = getattr(obj, field, None)
    widget = CountrySelectWidget()
    return widget.format_readonly(code)


def _render_city_field(obj, field, cfg):
    """Render CityField with location display."""
    from .location_widget import CitySelectWidget

    city_id = getattr(obj, field, None)
    widget = CitySelectWidget()
    return widget.format_readonly(city_id)


def _render_location_field(obj, field, cfg):
    """Render LocationField with full location hierarchy."""
    from .location_widget import CitySelectWidget

    city_id = getattr(obj, field, None)
    show_flag = cfg.get('show_flag', True) if cfg else True
    show_coordinates = cfg.get('show_coordinates', False) if cfg else False

    widget = CitySelectWidget()
    return widget.format_readonly(city_id)


WidgetRegistry.register("country", _render_country_field)
WidgetRegistry.register("city", _render_city_field)
WidgetRegistry.register("location", _render_location_field)
