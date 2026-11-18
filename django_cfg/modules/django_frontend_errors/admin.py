from django.contrib import admin

from django_cfg.modules.django_admin.base import PydanticAdmin

from .models import FrontendError


@admin.register(FrontendError)
class FrontendErrorAdmin(PydanticAdmin):
    """Read-only list of browser errors; delete is allowed (clearing a fixed error)."""

    list_display = ("last_seen", "count", "event_type", "level", "short_message", "short_url", "environment", "project_name", "browser")
    list_filter = ("environment", "event_type", "level", "project_name", "browser")
    search_fields = ("url", "message", "fingerprint", "build_id")
    date_hierarchy = "last_seen"
    ordering = ("-last_seen",)
    list_per_page = 50
    readonly_fields = [f.name for f in FrontendError._meta.fields]

    @admin.display(description="Message")
    def short_message(self, obj):
        return obj.message[:100]

    @admin.display(description="URL")
    def short_url(self, obj):
        return obj.url[:80]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
