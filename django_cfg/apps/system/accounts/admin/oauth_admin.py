"""
OAuth Admin Configuration

Admin interface for OAuth connections and states.
"""

from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from ..models.oauth import OAuthConnection, OAuthState


@admin.register(OAuthConnection)
class OAuthConnectionAdmin(ModelAdmin):
    """Admin for OAuth connections."""

    list_display = [
        'user_email',
        'provider_badge',
        'provider_username',
        'connected_at',
        'last_login_at',
    ]

    list_filter = [
        'provider',
        'connected_at',
        'last_login_at',
    ]

    search_fields = [
        'user__email',
        'user__username',
        'provider_email',
        'provider_username',
    ]

    readonly_fields = [
        'user',
        'provider',
        'provider_user_id',
        'provider_email',
        'provider_username',
        'provider_avatar_url',
        'provider_name',
        'access_token_masked',
        'scopes',
        'connected_at',
        'updated_at',
        'last_login_at',
    ]

    fieldsets = (
        ('Connection', {
            'fields': ('user', 'provider', 'connected_at', 'last_login_at'),
        }),
        ('Provider Data', {
            'fields': (
                'provider_user_id',
                'provider_email',
                'provider_username',
                'provider_name',
                'provider_avatar_url',
            ),
        }),
        ('Token', {
            'fields': ('access_token_masked', 'scopes'),
            'classes': ('collapse',),
        }),
    )

    ordering = ['-connected_at']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'

    def provider_badge(self, obj):
        colors = {
            'github': '#24292e',
            'google': '#4285f4',
            'gitlab': '#fc6d26',
        }
        color = colors.get(obj.provider, '#666')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_provider_display()
        )
    provider_badge.short_description = 'Provider'

    def access_token_masked(self, obj):
        if obj.access_token:
            return f"{obj.access_token[:8]}...{obj.access_token[-4:]}"
        return "-"
    access_token_masked.short_description = 'Access Token'

    def has_add_permission(self, request):
        # OAuth connections should only be created through OAuth flow
        return False

    def has_change_permission(self, request, obj=None):
        # Read-only
        return False


@admin.register(OAuthState)
class OAuthStateAdmin(ModelAdmin):
    """Admin for OAuth states (temporary CSRF tokens)."""

    list_display = [
        'state_short',
        'provider',
        'created_at',
        'expires_at',
        'is_expired_badge',
    ]

    list_filter = [
        'provider',
        'created_at',
    ]

    search_fields = [
        'state',
        'redirect_uri',
    ]

    readonly_fields = [
        'state',
        'provider',
        'redirect_uri',
        'source_url',
        'created_at',
        'expires_at',
    ]

    ordering = ['-created_at']

    actions = ['cleanup_expired']

    def state_short(self, obj):
        return f"{obj.state[:12]}..."
    state_short.short_description = 'State'

    def is_expired_badge(self, obj):
        if obj.is_expired:
            return format_html(
                '<span style="color: red;">Expired</span>'
            )
        return format_html(
            '<span style="color: green;">Valid</span>'
        )
    is_expired_badge.short_description = 'Status'

    def cleanup_expired(self, request, queryset):
        deleted = OAuthState.cleanup_expired()
        self.message_user(request, f"Deleted {deleted} expired states.")
    cleanup_expired.short_description = "Clean up expired states"

    def has_add_permission(self, request):
        # States should only be created through OAuth flow
        return False

    def has_change_permission(self, request, obj=None):
        # Read-only
        return False
