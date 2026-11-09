"""
Chat configuration model: the ready assistant chat for a project that has none.

One line turns it on (`chat = ChatConfig()`); everything else has a default. Existing hosts that keep their own
chat tables never set it. See `modules/django_llm/agent/chat/@docs/chat-app.md`.
"""

from typing import TYPE_CHECKING, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from django_cfg.models.django.django_rq import RQScheduleConfig


class AttachmentsConfig(BaseModel):
    """Files on a message of the ready chat's default kind (`ChatConfig(attachments=AttachmentsConfig())`). Off while `ChatConfig.attachments` is None.

    Bytes go to the Django storage you already configured (`StorageConfig`, alias `default` unless you say otherwise) under `chat/<kind>/<uuid>`;
    they are served only to their owner or by a short-lived signed link. A kind of your own sets `ChatKind.attachments=AttachmentPolicy(...)` instead.
    """

    model_config = ConfigDict(extra="forbid")

    kinds: List[Literal["image", "text", "document", "audio"]] = Field(default_factory=lambda: ["image", "text", "document"], min_length=1, description="What a user may attach")
    max_files: int = Field(default=4, ge=1, le=20, description="Files per message")
    max_mb: int = Field(default=10, ge=1, le=50, description="Largest file in MB (50 is the ceiling until presigned uploads)")
    max_total_mb: int = Field(default=25, ge=1, le=100, description="Files of one message together, in MB")
    daily_mb: Optional[int] = Field(default=None, ge=1, description="Upload MB per user per UTC day; None = no cap")
    keep_days: Optional[int] = Field(default=30, ge=0, description="Days a sent file's bytes are kept; then they are deleted and the chat keeps the name and what was read from it. 0 = delete as soon as the answer is stored; None = keep")
    staged_ttl_hours: int = Field(default=24, ge=1, description="An upload nobody sent is deleted after this many hours")
    url_ttl_s: int = Field(default=3600, ge=60, description="Life of a file link; a thread read mints fresh ones")
    storage: str = Field(default="default", description="Django STORAGES alias")
    delivery: Literal["signed", "presigned", "public"] = Field(default="signed", description="signed: API route with a token (default); presigned: the store's expiring URL; public: the store's permanent URL (never for private chat)")
    on_unreadable: Literal["describe", "refuse", "note"] = Field(default="describe", description="A file the model chain cannot read: read it through a cheap vision model (default), refuse the message, or pass a note")
    vision: Optional[bool] = Field(default=None, description="True: the chain reads images and PDFs itself; False: always describe through `ocr_models`; None: ask the model catalogue")
    ocr_models: List[str] = Field(default_factory=list, description="Cheap vision chain for the describe path; empty = the library default")
    audio_models: List[str] = Field(default_factory=list, description="Audio-capable chain that transcribes audio; empty = the library default")
    replay_of: int = Field(default=2, ge=1, description="The latest N file-carrying user turns (this one included) send their files; earlier ones keep a stub")

    def policy(self):
        """The `AttachmentPolicy` this block stands for."""
        from django_cfg.modules.django_llm.agent.chat.attachments import AttachmentPolicy

        mb = 1024 * 1024
        return AttachmentPolicy(
            kinds=frozenset(self.kinds), max_files=self.max_files, max_bytes=self.max_mb * mb, max_total_bytes=max(self.max_total_mb, self.max_mb) * mb,
            daily_bytes=self.daily_mb * mb if self.daily_mb else None, staged_ttl_hours=self.staged_ttl_hours, keep_days=self.keep_days, url_ttl_s=self.url_ttl_s,
            storage=self.storage, delivery=self.delivery, on_unreadable=self.on_unreadable, vision=self.vision,
            ocr_models=tuple(self.ocr_models) or None, audio_models=tuple(self.audio_models) or None, replay_of=self.replay_of,
        )


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

    # Attachments (off by default; see agent/chat/@docs/chat-attachments.md)
    attachments: Optional[AttachmentsConfig] = Field(default=None, description="Let users attach files to a message (images, text, PDF, audio). None = no files, the routes answer 404")

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


__all__ = ["AttachmentsConfig", "ChatConfig"]
