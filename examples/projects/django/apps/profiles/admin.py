"""
Admin configuration for Profiles app using django-cfg admin system v2.0.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    Icons,
    UserField,
)
from django_cfg.modules.django_admin.base import PydanticAdmin
from django_cfg.modules.django_admin.utils import computed_field

from .models import UserProfile

# Declarative Pydantic Config
userprofile_admin_config = AdminConfig(
    model=UserProfile,

    # Performance optimization
    select_related=["user"],

    # List display
    list_display=[
        "user",
        "company",
        "job_title",
        "social_links_count",
        "stats",
        "created_at"
    ],

    # Display fields with UI widgets
    display_fields=[
        UserField(
            name="user",
            title="User",
            ordering="user__username",
            header=True
        ),
        BadgeField(
            name="company",
            title="Company",
            variant="info",
            icon=Icons.BUSINESS,
            empty_value="—"
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            ordering="created_at"
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
            fields=["user"]
        ),
        FieldsetConfig(
            title="Social Links",
            fields=["website", "github", "twitter", "linkedin"],
            description="Social media and professional profiles"
        ),
        FieldsetConfig(
            title="Professional Info",
            fields=["company", "job_title"]
        ),
        FieldsetConfig(
            title="Statistics",
            fields=["posts_count", "comments_count", "orders_count"],
            collapsed=True
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True
        ),
    ],
)


@admin.register(UserProfile)
class UserProfileAdmin(PydanticAdmin):
    """Enhanced admin for UserProfile model using new Pydantic approach."""

    config = userprofile_admin_config

    # Custom display methods using self.html
    @computed_field("Social Links")
    def social_links_count(self, obj):
        """Display social links count with badge."""
        links = [obj.website, obj.github, obj.twitter, obj.linkedin]
        count = sum(1 for link in links if link)

        if count == 0:
            return None  # Will show "—" from decorator

        label = "link" if count == 1 else "links"
        return self.html.badge(f"{count} {label}", variant="primary", icon=Icons.LINK)

    @computed_field("Activity Stats")
    def stats(self, obj):
        """Display user activity statistics using Material Icons."""
        return self.html.inline([
            self.html.icon_text(Icons.EDIT, obj.posts_count),
            self.html.icon_text(Icons.CHAT, obj.comments_count),
            self.html.icon_text(Icons.SHOPPING_CART, obj.orders_count),
        ], size="small")
