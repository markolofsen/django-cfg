"""
Custom admin filters for Accounts app.

Enhanced filters with better organization and performance.
"""

from datetime import timedelta

from django.contrib import admin
from django.db import models
from django.db.models import Count
from django.utils import timezone


class UserStatusFilter(admin.SimpleListFilter):
    """Enhanced user status filter with clear categories."""
    title = "User Status"
    parameter_name = "user_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "✅ Active Users"),
            ("deleted", "🗑️ Deleted (soft)"),
            ("inactive", "❌ Inactive (non-deleted)"),
            ("staff", "⚙️ Staff Members"),
            ("superuser", "👑 Superusers"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True, deleted_at__isnull=True)
        elif self.value() == "deleted":
            return queryset.filter(deleted_at__isnull=False)
        elif self.value() == "inactive":
            return queryset.filter(is_active=False, deleted_at__isnull=True)
        elif self.value() == "staff":
            return queryset.filter(is_staff=True, is_superuser=False)
        elif self.value() == "superuser":
            return queryset.filter(is_superuser=True)
        return queryset


class OTPStatusFilter(admin.SimpleListFilter):
    """Enhanced OTP status filter with time-based categories."""
    title = "OTP Status"
    parameter_name = "otp_status"

    def lookups(self, request, model_admin):
        return (
            ("valid", "✅ Valid & Active"),
            ("used", "🔒 Used"),
            ("expired", "⏰ Expired"),
            ("recent", "🕐 Recent (24h)"),
            ("today", "📅 Today"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if self.value() == "valid":
            return queryset.filter(is_used=False, expires_at__gt=now)
        elif self.value() == "used":
            return queryset.filter(is_used=True)
        elif self.value() == "expired":
            return queryset.filter(is_used=False, expires_at__lte=now)
        elif self.value() == "recent":
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        elif self.value() == "today":
            return queryset.filter(created_at__gte=today_start)
        return queryset


class RegistrationSourceStatusFilter(admin.SimpleListFilter):
    """Registration source status filter."""
    title = "Source Status"
    parameter_name = "source_status"

    def lookups(self, request, model_admin):
        return (
            ("active", "✅ Active Sources"),
            ("inactive", "❌ Inactive Sources"),
            ("popular", "🔥 Popular (10+ users)"),
        )

    def queryset(self, request, queryset):
        if self.value() == "active":
            return queryset.filter(is_active=True)
        elif self.value() == "inactive":
            return queryset.filter(is_active=False)
        elif self.value() == "popular":
            # Sources with 10 or more users
            return queryset.annotate(
                user_count=Count('user_registration_sources')
            ).filter(user_count__gte=10)
        return queryset


class ActivityTypeFilter(admin.SimpleListFilter):
    """Enhanced activity type filter with time-based options."""
    title = "Activity Type"
    parameter_name = "activity_type"

    def lookups(self, request, model_admin):
        return (
            ("login", "🔐 Login"),
            ("logout", "🚪 Logout"),
            ("otp_requested", "📧 OTP Requested"),
            ("otp_verified", "✅ OTP Verified"),
            ("profile_updated", "✏️ Profile Updated"),
            ("registration", "👤 Registration"),
            ("recent", "🕐 Recent (24h)"),
            ("today", "📅 Today"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if self.value() == "recent":
            return queryset.filter(created_at__gte=now - timedelta(hours=24))
        elif self.value() == "today":
            return queryset.filter(created_at__gte=today_start)
        elif self.value():
            return queryset.filter(activity_type=self.value())
        return queryset


