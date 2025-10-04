"""
Shared configuration objects for admin displays.

Provides pre-configured StatusBadgeConfig, MoneyDisplayConfig, etc.
for consistent display across all document admin interfaces.
"""

from django_cfg.modules.django_admin import (
    MoneyDisplayConfig,
    StatusBadgeConfig,
    DateTimeDisplayConfig,
    Icons,
)


class DocumentAdminConfigs:
    """Shared configuration objects for document admins."""

    # Visibility badges
    VISIBILITY_PUBLIC = StatusBadgeConfig(show_icons=True, icon=Icons.PUBLIC)
    VISIBILITY_PRIVATE = StatusBadgeConfig(show_icons=True, icon=Icons.LOCK)

    # Vectorization status badges
    VECTORIZED = StatusBadgeConfig(show_icons=True, icon=Icons.CHECK_CIRCLE)
    NOT_VECTORIZED = StatusBadgeConfig(show_icons=True, icon=Icons.ERROR)

    # Entity type badges
    DOCUMENT_TITLE = StatusBadgeConfig(show_icons=True, icon=Icons.DESCRIPTION)
    CHUNK = StatusBadgeConfig(show_icons=True, icon=Icons.ARTICLE)
    CATEGORY = StatusBadgeConfig(show_icons=True, icon=Icons.FOLDER)

    # Processing status
    PROCESSING_STATUS = StatusBadgeConfig(
        custom_mappings={
            'pending': 'warning',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'secondary'
        },
        show_icons=True
    )

    # Money display configuration
    COST_USD = MoneyDisplayConfig(
        currency="USD",
        decimal_places=6,
        show_sign=False
    )

    # DateTime display configuration
    CREATED_AT = DateTimeDisplayConfig(show_relative=True)

    @classmethod
    def get_processing_status_icon(cls, status: str) -> str:
        """
        Get appropriate icon for processing status.

        Args:
            status: Processing status value

        Returns:
            Icon constant
        """
        status_icons = {
            'completed': Icons.CHECK_CIRCLE,
            'failed': Icons.ERROR,
            'processing': Icons.SCHEDULE,
            'pending': Icons.SCHEDULE,
            'cancelled': Icons.CANCEL
        }
        return status_icons.get(status, Icons.SCHEDULE)
