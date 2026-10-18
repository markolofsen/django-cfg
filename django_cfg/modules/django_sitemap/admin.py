"""Read-only admin for the IndexNow state: a record, not something to edit."""
from django.contrib import admin

from django_cfg.modules.django_admin import AdminConfig, DateTimeField, FilterConfig
from django_cfg.modules.django_admin.base import PydanticAdmin

from .models import IndexNowHost, IndexNowSubmission


class _ReadOnly(PydanticAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return tuple(f.name for f in self.model._meta.fields)


@admin.register(IndexNowHost)
class IndexNowHostAdmin(_ReadOnly):
    config = AdminConfig(
        model=IndexNowHost,
        list_display=["host", "last_status", "last_run_at", "last_success_at", "seeded_at"],
        ordering=["host"],
        display_fields=[
            DateTimeField(name="last_run_at", show_relative=True),
            DateTimeField(name="last_success_at", show_relative=True),
            DateTimeField(name="seeded_at", show_relative=True),
        ],
    )


@admin.register(IndexNowSubmission)
class IndexNowSubmissionAdmin(_ReadOnly):
    config = AdminConfig(
        model=IndexNowSubmission,
        list_display=["created_at", "host", "url_count", "http_status", "response_excerpt"],
        search_fields=["host", "response_excerpt"],
        ordering=["-created_at"],
        date_hierarchy="created_at",
        list_filter=[
            FilterConfig(field="host", type="choices_dropdown"),
            FilterConfig(field="http_status", type="choices_dropdown"),
        ],
        display_fields=[DateTimeField(name="created_at", show_relative=True)],
    )
