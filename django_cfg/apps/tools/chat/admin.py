from django.contrib import admin

from django_cfg.apps.tools.chat.models import Message, Thread
from django_cfg.modules.django_llm.agent.chat.admin import MessageAdminMixin, ThreadAdminMixin


@admin.register(Thread)
class ThreadAdmin(ThreadAdminMixin, admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(MessageAdminMixin, admin.ModelAdmin):
    pass
