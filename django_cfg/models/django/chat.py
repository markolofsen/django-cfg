"""
Chat configuration model: the ready assistant chat for a project that has none.

One line turns it on (`chat = ChatConfig()`); everything else has a default. Existing hosts that keep their own
chat tables never set it. See `modules/django_llm/agent/chat/@docs/chat-app.md`.
"""

from typing import TYPE_CHECKING, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from django_cfg.models.django.django_rq import RQScheduleConfig


class ChatConfig(BaseModel):
    """
    Ready assistant chat (`django_cfg.apps.tools.chat`): `Thread`/`Message` tables, one default kind, the API kit at
    `/cfg/chat/`, admin, scheduled `reap`/`prune` (and `vectorise` when `vectors` is on), a generated-client group named `chat`.

    Example:
        ```python
        from django_cfg import DjangoConfig, ChatConfig

        class MyConfig(DjangoConfig):
            chat = ChatConfig(instructions="You help customers of Acme.", models=("openai/gpt-4o-mini",))
        ```
    """

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=True, description="Install the chat app, mount its API and register its schedules")
    paused: bool = Field(default=False, description="Kill switch: sending is refused with 503 while true (reads still work). Drive it from the environment.")

    # The default kind
    default_kind: str = Field(default="assistant", description="Kind name; a new chat that omits `kind` gets it")
    instructions: str = Field(default="You are a helpful, concise assistant.", description="System instructions of the default kind")
    models: List[str] = Field(default_factory=lambda: ["openai/gpt-4o-mini"], min_length=1, description="Model chain, primary first (OpenRouter slugs)")
    title_models: List[str] = Field(default_factory=list, description="Cheap chain that writes the thread title after the first answer; empty = trimmed first message")
    history_window: int = Field(default=20, ge=1, description="Messages the model sees")
    max_tokens: int = Field(default=2000, ge=1, description="Answer length bound")

    # Policy
    messages_per_day: Optional[int] = Field(default=200, ge=1, description="User messages per user per UTC day; None = no cap (429 over it)")
    max_text_chars: int = Field(default=4000, ge=1, description="Longest user message (400 over it)")
    daily_token_budget: Optional[int] = Field(default=None, ge=1, description="Site-wide tokens per UTC day; spent = 503 until midnight. None = no budget")

    # Knowledge folder (off by default)
    knowledge: Union[bool, str, None] = Field(default=None, description="True = the knowledge folder, a string = one subfolder of it")
    knowledge_dir: Optional[str] = Field(default=None, description="Folder of markdown (absolute, or relative to BASE_DIR). Implies knowledge=True")
    knowledge_language: Optional[str] = Field(default=None, description="Language the files are written in")

    # Vectors (off by default; see agent/chat/@docs/vectorisation.md)
    vectors: bool = Field(default=False, description="Embed chats in chunks of 10-20 messages (never per message) and serve GET /cfg/chat/search/. Costs embedding calls")
    vector_model: str = Field(default="openai/text-embedding-3-small", description="Embedding model (OpenRouter slug); multilingual, 1536 dims")
    vector_chunk_messages: int = Field(default=20, ge=10, le=40, description="Most messages in one chunk (the token budget may cut earlier)")
    vector_token_budget: int = Field(default=1500, ge=200, description="Estimated tokens in one chunk")
    vector_interval: Optional[int] = Field(default=300, ge=30, description="Seconds between runs of the indexing job; None = not scheduled (run `chat_vectorise`)")

    # Operations (RQ scheduler; need django_rq enabled)
    reap_interval: Optional[int] = Field(default=60, ge=10, description="Seconds between closing answers stuck in `running`; None = not scheduled")
    prune_days: Optional[int] = Field(default=180, ge=1, description="Delete threads idle this many days (nightly 03:17); None = keep forever")

    def get_rq_schedules(self) -> List["RQScheduleConfig"]:
        """The reaper (interval) and the pruner (nightly)."""
        if not self.enabled:
            return []

        from django_cfg.models.django.django_rq import RQScheduleConfig

        out: List["RQScheduleConfig"] = []
        if self.reap_interval:
            out.append(
                RQScheduleConfig(
                    func="django_cfg.apps.tools.chat.tasks.reap",
                    interval=self.reap_interval,
                    queue="default",
                    description=f"Close stuck chat answers (every {self.reap_interval}s)",
                )
            )
        if self.prune_days:
            out.append(
                RQScheduleConfig(
                    func="django_cfg.apps.tools.chat.tasks.prune",
                    cron="17 3 * * *",
                    queue="default",
                    kwargs={"days": self.prune_days},
                    description=f"Delete chat threads idle for {self.prune_days} days",
                )
            )
        if self.vectors and self.vector_interval:
            out.append(
                RQScheduleConfig(
                    func="django_cfg.apps.tools.chat.tasks.vectorise",
                    interval=self.vector_interval,
                    queue="default",
                    description=f"Embed new chat messages in chunks (every {self.vector_interval}s)",
                )
            )
        return out

    def openapi_group(self):
        """The generated-client group (`chat`) over the app's URLs."""
        from django_cfg.modules.django_generator.openapi.pipeline.config import OpenAPIGroupConfig

        return OpenAPIGroupConfig(
            name="chat",
            apps=["django_cfg.apps.tools.chat"],
            title="Chat API",
            description="Assistant chat: sessions, messages, streamed answers",
            version="1.0.0",
        )


__all__ = ["ChatConfig"]
