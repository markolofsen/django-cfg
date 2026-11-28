from django.contrib import admin

from .models import DemoPing


@admin.register(DemoPing)
class DemoPingAdmin(admin.ModelAdmin):
    list_display = ["id", "note", "sender", "created_at"]
    readonly_fields = ["created_at"]
