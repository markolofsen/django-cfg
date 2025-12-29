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
    "image_preview",
    lambda obj, field, cfg: ImagePreviewDisplay.from_field(obj, field, cfg)
)

# Video widget
from ..utils.displays import VideoDisplay

WidgetRegistry.register(
    "video",
    lambda obj, field, cfg: VideoDisplay.from_field(obj, field, cfg)
)
