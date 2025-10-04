"""
Custom admin filters for support app.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class TicketUserEmailFilter(admin.SimpleListFilter):
    """
    Filter tickets by user email using text input instead of dropdown.
    More efficient for large user bases.
    """
    title = _('User Email')
    parameter_name = 'user_email'

    def lookups(self, request, model_admin):
        """Return empty lookups to show text input."""
        return ()

    def queryset(self, request, queryset):
        """Filter queryset based on user email input."""
        if self.value():
            return queryset.filter(user__email__icontains=self.value())
        return queryset


class TicketUserNameFilter(admin.SimpleListFilter):
    """
    Filter tickets by username using text input instead of dropdown.
    More efficient for large user bases.
    """
    title = _('Username')
    parameter_name = 'username'

    def lookups(self, request, model_admin):
        """Return empty lookups to show text input."""
        return ()

    def queryset(self, request, queryset):
        """Filter queryset based on username input."""
        if self.value():
            return queryset.filter(
                models.Q(user__username__icontains=self.value()) |
                models.Q(user__first_name__icontains=self.value()) |
                models.Q(user__last_name__icontains=self.value())
            )
        return queryset


class MessageSenderEmailFilter(admin.SimpleListFilter):
    """
    Filter messages by sender email using text input instead of dropdown.
    More efficient for large user bases.
    """
    title = _('Sender Email')
    parameter_name = 'sender_email'

    def lookups(self, request, model_admin):
        """Return empty lookups to show text input."""
        return ()

    def queryset(self, request, queryset):
        """Filter queryset based on sender email input."""
        if self.value():
            return queryset.filter(sender__email__icontains=self.value())
        return queryset
