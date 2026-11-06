"""The concrete chat tables of the ready app. Hosts that already have a chat keep their own and never install this app."""

from django.db import models

from django_cfg.modules.django_llm.agent.chat.models import AbstractMessage, AbstractThread
from django_cfg.modules.django_llm.agent.chat.vectors.models import AbstractChatChunk


class Thread(AbstractThread):
    class Meta(AbstractThread.Meta):
        db_table = "cfg_chat_thread"
        indexes = [models.Index(fields=["owner", "-updated_at"], name="cfg_chat_thread_owner_idx")]


class Message(AbstractMessage):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")  # the name is the contract

    class Meta(AbstractMessage.Meta):
        db_table = "cfg_chat_message"
        indexes = [models.Index(fields=["thread", "-seq"], name="cfg_chat_msg_thread_seq_idx")]


class ThreadChunk(AbstractChatChunk):
    """Optional vectors (`ChatConfig.vectors`): one row per run of 10-20 messages. Empty and unused while the switch is off."""

    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="chunks")

    class Meta(AbstractChatChunk.Meta):
        db_table = "cfg_chat_thread_chunk"
