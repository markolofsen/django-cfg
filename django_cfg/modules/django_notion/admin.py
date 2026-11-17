from django.contrib import admin, messages
from django.utils import timezone

from . import outbox
from .models import NotionOutbox


@admin.register(NotionOutbox)
class NotionOutboxAdmin(admin.ModelAdmin):
    list_display = ("key", "target", "status", "attempts", "maybe_created", "telegram_notified_at", "email_notified_at", "notion_page_id", "next_attempt_at", "created_at")
    list_filter = ("status", "target", "maybe_created")
    search_fields = ("key", "notion_page_id", "last_error")
    readonly_fields = [f.name for f in NotionOutbox._meta.fields]
    ordering = ("-created_at",)
    actions = ["retry"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.action(description="Retry (reset attempts and send again)")
    def retry(self, request, queryset):
        rows = list(queryset.exclude(status__in=[NotionOutbox.Status.SENT, NotionOutbox.Status.SENDING]))
        ids = [r.pk for r in rows]
        NotionOutbox.objects.filter(pk__in=ids).update(
            status=NotionOutbox.Status.PENDING, attempts=0, next_attempt_at=timezone.now(), locked_at=None
        )
        for pk in ids:
            outbox.enqueue(pk)
        self.message_user(request, f"{len(ids)} row(s) queued again", messages.SUCCESS)
