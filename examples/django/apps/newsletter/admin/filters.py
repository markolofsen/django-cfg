"""
Custom admin filters for newsletter app.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserEmailFilter(admin.SimpleListFilter):
    """
    Filter by user email using text input instead of dropdown.
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
            return queryset.filter(
                models.Q(user__email__icontains=self.value()) |
                models.Q(recipient__icontains=self.value())
            )
        return queryset


class UserNameFilter(admin.SimpleListFilter):
    """
    Filter by username using text input instead of dropdown.
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


class HasUserFilter(admin.SimpleListFilter):
    """
    Simple filter to show emails with or without associated users.
    """
    title = _('Has User Account')
    parameter_name = 'has_user'

    def lookups(self, request, model_admin):
        """Return filter options."""
        return (
            ('yes', _('Has User Account')),
            ('no', _('No User Account')),
        )

    def queryset(self, request, queryset):
        """Filter queryset based on user presence."""
        if self.value() == 'yes':
            return queryset.filter(user__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(user__isnull=True)
        return queryset


class EmailOpenedFilter(admin.SimpleListFilter):
    """
    Filter emails by opened status.
    """
    title = _('Email Opened')
    parameter_name = 'email_opened'

    def lookups(self, request, model_admin):
        """Return filter options."""
        return (
            ('yes', _('Opened')),
            ('no', _('Not Opened')),
        )

    def queryset(self, request, queryset):
        """Filter queryset based on opened status."""
        if self.value() == 'yes':
            return queryset.filter(opened_at__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(opened_at__isnull=True)
        return queryset


class EmailClickedFilter(admin.SimpleListFilter):
    """
    Filter emails by clicked status.
    """
    title = _('Link Clicked')
    parameter_name = 'link_clicked'

    def lookups(self, request, model_admin):
        """Return filter options."""
        return (
            ('yes', _('Clicked')),
            ('no', _('Not Clicked')),
        )

    def queryset(self, request, queryset):
        """Filter queryset based on clicked status."""
        if self.value() == 'yes':
            return queryset.filter(clicked_at__isnull=False)
        elif self.value() == 'no':
            return queryset.filter(clicked_at__isnull=True)
        return queryset
