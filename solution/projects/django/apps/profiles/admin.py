"""
Admin configuration for Profiles app using django-cfg admin system v2.0.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    DateTimeField,
    FieldsetConfig,
    TextField,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from .models import UserProfile


# =============================================================================
# UserProfile Admin Configuration
# =============================================================================

userprofile_admin_config = AdminConfig(
    model=UserProfile,

    # Performance optimization
    select_related=["user"],

    # List display - use real model fields
    list_display=[
        "user",
        "company",
        "job_title",
        "website",
        "posts_count",
        "comments_count",
        "orders_count",
        "created_at",
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="user",
            title="User",
            ordering="user__username",
            header=True,
        ),
        TextField(
            name="company",
            title="Company",
            truncate=30,
        ),
        TextField(
            name="job_title",
            title="Job Title",
            truncate=30,
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at",
            show_relative=True,
        ),
    ],

    # List options
    list_display_links=["user"],
    list_filter=["created_at", "updated_at"],
    search_fields=["user__username", "user__email", "company", "job_title"],
    ordering=["-created_at"],

    # Form options
    autocomplete_fields=["user"],
    readonly_fields=["posts_count", "comments_count", "orders_count", "created_at", "updated_at"],

    # Fieldsets
    fieldsets=[
        FieldsetConfig(
            title="User",
            fields=["user"],
        ),
        FieldsetConfig(
            title="Social Links",
            fields=["website", "github", "twitter", "linkedin"],
            description="Social media and professional profiles",
        ),
        FieldsetConfig(
            title="Professional Info",
            fields=["company", "job_title"],
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["posts_count", "comments_count", "orders_count"],
            collapsed=True,
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True,
        ),
    ],
)


@admin.register(UserProfile)
class UserProfileAdmin(PydanticAdmin):
    """Enhanced admin for UserProfile model using new Pydantic approach."""

    config = userprofile_admin_config
