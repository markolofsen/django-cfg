"""Admin for letter copy and the send log.

Storing copy in the database only pays off if it is editable, so this is the
point of the model — the fieldsets present the letter in reading order rather
than as an alphabetical field list.

Written with ``PydanticAdmin``/``AdminConfig`` like the rest of django-cfg
(accounts, payments, currency) rather than a bare ``unfold.ModelAdmin``: badges,
filters and datetime rendering then come from one place, and the admin picks up
theme changes without being touched.
"""

from django.contrib import admin

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    FieldsetConfig,
    FilterConfig,
    Icons,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from .models import EmailContent, EmailLog


@admin.register(EmailContent)
class EmailContentAdmin(PydanticAdmin):
    """Per-locale copy for one letter."""

    config = AdminConfig(
        model=EmailContent,
        list_display=["key", "locale", "subject", "is_active", "updated_at"],
        list_display_links=["key", "subject"],
        list_editable=["is_active"],
        search_fields=["key", "locale", "subject", "lede", "points"],
        ordering=["key", "locale"],
        list_filter=[
            FilterConfig(field="key", type="choices_dropdown"),
            FilterConfig(field="locale", type="choices_dropdown"),
            FilterConfig(field="is_active", type="boolean", title="Active"),
        ],
        display_fields=[
            DateTimeField(name="updated_at", show_relative=True),
        ],
        fieldsets=[
            FieldsetConfig(
                title="Which letter, which language",
                fields=["key", "locale", "is_active"],
                description=(
                    "One row per letter per language. A locale with no row falls "
                    "back to its base language, then to English — a missing "
                    "translation is safe, not broken."
                ),
            ),
            FieldsetConfig(
                title="Subject",
                fields=["subject"],
                description=(
                    "The envelope Subject: header. Translate it — an English "
                    "subject over a translated letter is the most visible way to "
                    "get this wrong."
                ),
            ),
            FieldsetConfig(
                title="The letter, in reading order",
                fields=[
                    "greeting",
                    "lede",
                    "run_intro",
                    "run_after",
                    "points",
                    "outro",
                    "signoff",
                    "role",
                ],
                description=(
                    "One paragraph per line in the multi-line fields; the template "
                    "adds the markup. Leave a field empty to fall back to the "
                    "template's own wording for that part. "
                    "{{ project_name }} and {{ site_url }} are substituted — "
                    "nothing else is, so stored text cannot reach the rest of the "
                    "template context."
                ),
            ),
        ],
        readonly_fields=["updated_at"],
    )


@admin.register(EmailLog)
class EmailLogAdmin(PydanticAdmin):
    """What was actually sent. Read-only: a record, not something to edit."""

    config = AdminConfig(
        model=EmailLog,
        list_display=["created_at", "key", "recipient", "locale", "status", "subject"],
        list_display_links=["created_at", "recipient"],
        search_fields=["recipient", "subject", "error"],
        ordering=["-created_at"],
        date_hierarchy="created_at",
        list_filter=[
            FilterConfig(field="status", type="choices_dropdown"),
            FilterConfig(field="key", type="choices_dropdown"),
            FilterConfig(field="created_at", type="range_date", title="Sent"),
        ],
        display_fields=[
            BadgeField(
                name="status",
                icon=Icons.OUTGOING_MAIL,
                label_map={
                    "queued": "info",
                    "sent": "success",
                    "failed": "danger",
                },
            ),
            DateTimeField(name="created_at", show_relative=True),
        ],
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return tuple(field.name for field in self.model._meta.fields)
