"""
Display mixin for convenient wrapper methods.
"""

from typing import Optional, Any
from django.utils.safestring import SafeString

from ..utils.displays import UserDisplay, MoneyDisplay, StatusDisplay, DateTimeDisplay
from ..utils.badges import StatusBadge, CounterBadge
from ..models.display_models import UserDisplayConfig, MoneyDisplayConfig, DateTimeDisplayConfig
from ..models.badge_models import StatusBadgeConfig


class DisplayMixin:
    """Mixin for Django ModelAdmin classes with convenient display methods."""
    
    def display_user_with_avatar(self, obj: Any, user_field: str = 'user',
                                config: Optional[UserDisplayConfig] = None) -> list:
        """Display user with avatar for @display(header=True)."""
        user = getattr(obj, user_field, None)
        return UserDisplay.with_avatar(user, config)
    
    def display_user_simple(self, obj: Any, user_field: str = 'user',
                           config: Optional[UserDisplayConfig] = None) -> SafeString:
        """Simple user display."""
        user = getattr(obj, user_field, None)
        return UserDisplay.simple(user, config)
    
    def display_money_amount(self, obj: Any, amount_field: str,
                            config: Optional[MoneyDisplayConfig] = None) -> SafeString:
        """Display money amount."""
        amount = getattr(obj, amount_field, None)
        return MoneyDisplay.amount(amount, config)
    
    def display_money_breakdown(self, obj: Any, main_field: str, breakdown_fields: dict,
                               config: Optional[MoneyDisplayConfig] = None) -> SafeString:
        """Display money with breakdown."""
        main_amount = getattr(obj, main_field, 0)
        
        breakdown_items = []
        for label, field_name in breakdown_fields.items():
            amount = getattr(obj, field_name, 0)
            breakdown_items.append({
                'label': label,
                'amount': amount,
                'color': 'warning' if amount > 0 else 'secondary'
            })
        
        return MoneyDisplay.with_breakdown(main_amount, breakdown_items, config)
    
    def display_status_auto(self, obj: Any, status_field: str = 'status',
                           config: Optional[StatusBadgeConfig] = None) -> SafeString:
        """Display status with auto color mapping."""
        status = getattr(obj, status_field, '')
        return StatusBadge.auto(status, config)
    
    def display_datetime_relative(self, obj: Any, datetime_field: str,
                                 config: Optional[DateTimeDisplayConfig] = None) -> SafeString:
        """Display datetime with relative time."""
        dt = getattr(obj, datetime_field, None)
        return DateTimeDisplay.relative(dt, config)
    
    def display_datetime_compact(self, obj: Any, datetime_field: str,
                                config: Optional[DateTimeDisplayConfig] = None) -> SafeString:
        """Display datetime compact."""
        dt = getattr(obj, datetime_field, None)
        return DateTimeDisplay.compact(dt, config)
    
    def display_count_simple(self, obj: Any, count_field: str, label: str = None) -> SafeString:
        """Display count as badge."""
        count = getattr(obj, count_field, 0)
        return CounterBadge.simple(count, label)
    
    def display_related_count(self, obj: Any, related_name: str, label: str = None) -> SafeString:
        """Display count of related objects."""
        try:
            related_manager = getattr(obj, related_name)
            count = related_manager.count()
            return CounterBadge.simple(count, label)
        except AttributeError:
            return CounterBadge.simple(0, label)
