"""
User Profile admin configuration.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturalday
from unfold.admin import ModelAdmin

from ..models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(ModelAdmin):
    """Enhanced admin for UserProfile model."""
    
    list_display = [
        'user_display', 
        'company_display', 
        'job_title', 
        'social_links_display',
        'stats_display',
        'created_at_display'
    ]
    list_display_links = ['user_display']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'company', 'job_title']
    readonly_fields = ['posts_count', 'comments_count', 'orders_count', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
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

    def user_display(self, obj):
        """Enhanced user display with avatar."""
        user = obj.user
        initials = f"{user.first_name[:1]}{user.last_name[:1]}".upper() or user.username[:2].upper()
        return format_html(
            '<div style="display: flex; align-items: center; gap: 8px;">'
            '<div style="width: 24px; height: 24px; border-radius: 50%; background: #6c757d; '
            'color: white; display: flex; align-items: center; justify-content: center; '
            'font-weight: bold; font-size: 10px;">{}</div>'
            '<span>{}</span></div>',
            initials,
            user.get_full_name() or user.username
        )
    
    user_display.short_description = "User"

    def company_display(self, obj):
        """Company with fallback."""
        return obj.company or "—"
    
    company_display.short_description = "Company"

    def social_links_display(self, obj):
        """Display social links count."""
        links = [obj.website, obj.github, obj.twitter, obj.linkedin]
        count = sum(1 for link in links if link)
        if count == 0:
            return "—"
        return f"{count} link{'s' if count != 1 else ''}"
    
    social_links_display.short_description = "Social Links"

    def stats_display(self, obj):
        """Display user statistics."""
        return format_html(
            '<small>📝 {} | 💬 {} | 🛒 {}</small>',
            obj.posts_count,
            obj.comments_count,
            obj.orders_count
        )
    
    stats_display.short_description = "Activity Stats"

    def created_at_display(self, obj):
        """Created date with natural time."""
        return naturalday(obj.created_at)
    
    created_at_display.short_description = "Created"
