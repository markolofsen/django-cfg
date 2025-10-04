"""
Admin configuration for Profiles app using django-cfg admin system.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin
from django_cfg.modules.django_admin import (
    OptimizedModelAdmin,
    DisplayMixin,
    StatusBadgeConfig,
    Icons,
    display,
)

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(OptimizedModelAdmin, DisplayMixin, ModelAdmin):
    """Enhanced admin for UserProfile model using django-cfg admin system."""

    # Performance optimization
    select_related_fields = ['user']

    # List configuration
    list_display = [
        'user_display',
        'company_display',
        'job_title',
        'social_links_display',
        'stats_display',
        'created_display'
    ]
    list_display_links = ['user_display']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'company', 'job_title']
    readonly_fields = ['posts_count', 'comments_count', 'orders_count', 'created_at', 'updated_at']
    ordering = ['-created_at']

    # Autocomplete
    autocomplete_fields = ['user']

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Social Links', {
            'fields': ('website', 'github', 'twitter', 'linkedin'),
            'description': 'Social media and professional profiles'
        }),
        ('Professional Info', {
            'fields': ('company', 'job_title')
        }),
        ('Statistics', {
            'fields': ('posts_count', 'comments_count', 'orders_count'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @display(description="User", ordering="user__username")
    def user_display(self, obj):
        """Display user with avatar using django-cfg utilities."""
        return self.display_user_with_avatar(obj, 'user')

    @display(description="Company")
    def company_display(self, obj):
        """Display company with badge."""
        if not obj.company:
            return "—"
        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=obj.company,
            variant="info",
            config=StatusBadgeConfig(show_icons=True, icon=Icons.BUSINESS)
        )

    @display(description="Social Links")
    def social_links_display(self, obj):
        """Display social links count."""
        links = [obj.website, obj.github, obj.twitter, obj.linkedin]
        count = sum(1 for link in links if link)

        if count == 0:
            return "—"

        from django_cfg.modules.django_admin.utils.badges import StatusBadge
        return StatusBadge.create(
            text=f"{count} link{'s' if count != 1 else ''}",
            variant="primary",
            config=StatusBadgeConfig(show_icons=True, icon=Icons.LINK)
        )

    @display(description="Activity Stats")
    def stats_display(self, obj):
        """Display user activity statistics."""
        from django.utils.html import format_html
        return format_html(
            '<small>📝 {} | 💬 {} | 🛒 {}</small>',
            obj.posts_count,
            obj.comments_count,
            obj.orders_count
        )

    @display(description="Created")
    def created_display(self, obj):
        """Display created date with relative time."""
        return self.display_datetime_relative(obj, 'created_at')
