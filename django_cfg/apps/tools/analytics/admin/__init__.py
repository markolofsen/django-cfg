"""Analytics admin.

Events and sessions are machine-written and strictly read-only — an editable
analytics row is a corrupted analytics row. Only AnalyticsSite is manageable,
because a site has to be registered before its traffic will be accepted.
"""

from django.contrib import admin
from django_cfg.modules.django_admin import AdminConfig
from django_cfg.modules.django_admin.base import PydanticAdmin

from ..models import AnalyticsEvent, AnalyticsSession, AnalyticsSite

site_admin_config = AdminConfig(
    model=AnalyticsSite,
    list_display=["domain", "name", "timezone", "is_active", "created_at"],
    list_filter=["is_active"],
    search_fields=["domain", "name"],
)

session_admin_config = AdminConfig(
    model=AnalyticsSession,
    select_related=["site", "user"],
    list_display=[
        "started_at", "site", "user", "country",
        "device", "browser", "channel", "pageviews", "is_bounce",
    ],
    list_filter=["site", "device", "channel", "is_bounce"],
    search_fields=["entry_pathname", "exit_pathname"],
)

event_admin_config = AdminConfig(
    model=AnalyticsEvent,
    select_related=["site", "session", "user"],
    list_display=["ts", "site", "event_name", "pathname", "user", "channel"],
    list_filter=["site", "event_name", "channel"],
    search_fields=["pathname", "route", "page_title"],
)


@admin.register(AnalyticsSite)
class AnalyticsSiteAdmin(PydanticAdmin):
    config = site_admin_config


@admin.register(AnalyticsSession)
class AnalyticsSessionAdmin(PydanticAdmin):
    config = session_admin_config

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


@admin.register(AnalyticsEvent)
class AnalyticsEventAdmin(PydanticAdmin):
    config = event_admin_config

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False


__all__ = ["AnalyticsSiteAdmin", "AnalyticsSessionAdmin", "AnalyticsEventAdmin"]
