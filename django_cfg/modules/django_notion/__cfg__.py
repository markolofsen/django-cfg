"""django_notion configuration: ``DjangoConfig.notion``."""

from __future__ import annotations

import os
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

NOTION_API_VERSION = "2025-09-03"
TOKEN_ENV = "NOTION__TOKEN"

# Logical field -> default column name of the "Leads" database. A target may rename a column,
# or set it to ``None`` to stop writing it (the value then goes to Details).
DEFAULT_COLUMNS: Dict[str, str] = {
    "name": "Name",
    "status": "Status",
    "source": "Source",
    "brand": "Brand",
    "email": "Email",
    "phone": "Phone",
    "message": "Message",
    "form": "Form",
    "page_url": "Page URL",
    "received_at": "Received at",
    "details": "Details",
    "run_id": "Hub run id",
}

# Column type each logical field needs (Notion property type), used by ``notion_doctor``.
COLUMN_TYPES: Dict[str, str] = {
    "name": "title", "status": "select", "source": "select", "brand": "multi_select", "email": "email",
    "phone": "phone_number", "message": "rich_text", "form": "rich_text", "page_url": "url",
    "received_at": "date", "details": "rich_text", "run_id": "rich_text",
}


class NotionTarget(BaseModel):
    """One Notion "Leads" database."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    database_id: Optional[str] = Field(
        default=None,
        description="Database id (the Notion page id of the database). Resolved once to its data source, which "
        "needs the Read content capability. With an Insert-only integration set data_source_id instead.",
    )
    data_source_id: Optional[str] = Field(
        default=None,
        description="Data source id (collection://<id> in the Notion MCP). Pages are created under it; no read call needed.",
    )
    token: Optional[SecretStr] = Field(
        default=None,
        repr=False,
        description="This target's own integration token (a workspace may keep one integration per CRM). "
        "Empty: NotionConfig.token is used.",
    )
    columns: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Overrides of DEFAULT_COLUMNS: logical name -> column name, or None to not write that column "
        "(its value goes to Details).",
    )
    lookup_before_retry: bool = Field(
        default=False,
        description="After an ambiguous failure (timeout, 5xx) query the data source by the idempotency key before "
        "creating again. Needs the Read content capability; off keeps Insert-only setups working (at-least-once).",
    )

    @field_validator("database_id", "data_source_id")
    @classmethod
    def _clean_id(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().removeprefix("collection://")
        if not v:
            raise ValueError("id is empty")
        return v

    @field_validator("columns")
    @classmethod
    def _known_columns(cls, v: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        unknown = sorted(set(v) - set(DEFAULT_COLUMNS))
        if unknown:
            raise ValueError(f"unknown logical column(s) {unknown}; known: {sorted(DEFAULT_COLUMNS)}")
        return v

    def model_post_init(self, __context) -> None:
        if not (self.database_id or self.data_source_id):
            raise ValueError("a target needs database_id or data_source_id")

    def column(self, logical: str) -> Optional[str]:
        """Column name for ``logical`` (None = not written)."""
        if logical in self.columns:
            return self.columns[logical]
        return DEFAULT_COLUMNS[logical]


def _token_from_env() -> Optional[SecretStr]:
    raw = os.environ.get(TOKEN_ENV, "").strip()
    return SecretStr(raw) if raw else None


class NotionConfig(BaseModel):
    """``DjangoConfig.notion``. The token is read from the environment (``NOTION__TOKEN``) only."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = Field(default=False, description="Install the django_notion app")
    token: Optional[SecretStr] = Field(
        default_factory=_token_from_env,
        repr=False,
        description=f"Integration token. Read from ${TOKEN_ENV}; never put it in code.",
    )
    targets: Dict[str, NotionTarget] = Field(default_factory=dict, description="Target name -> Notion database")
    project: str = Field(default="", description="Prefix of the idempotency key; defaults to the DjangoConfig project name")
    project_keys: Dict[str, str] = Field(
        default_factory=dict,
        description="django-cfg site key (DjangoConfig.sites; 'default' for a single-site project) -> project key, a "
        "lowercase slug such as 'carapis' or 'mls-bali'. The server sets it per site, never the visitor. It becomes the "
        "'Project key' Details line, the Brand option whose name matches it, and the X-Project-Key header of the notice",
    )
    enrich: bool = Field(default=True, description="Add the project key, Project, Environment, Site and API host from the project config to every lead")
    notify_telegram: bool = Field(default=True, description="Also send every lead to Telegram (DjangoConfig.telegram); skipped silently when Telegram is not configured")
    notify_email: bool = Field(default=True, description="Also email every lead to the administrators (config.admin_emails, then Django ADMINS); skipped silently with no recipients")
    notify_link_wait_seconds: int = Field(default=30, ge=0, le=600, description="Telegram and admin email wait up to this long after the lead for the Notion page, so they can carry its link; then they go without it (never twice). 0 = do not wait. No wait when Notion has no token for the lead")
    acknowledge: bool = Field(default=True, description="Email the lead's author a short plain-text 'your request was received' letter (needs a valid email on the lead; at most one per address per 24 h)")
    acknowledge_reply_within: str = Field(default="", description="Free text for 'we usually reply within ...', e.g. '2 business hours'; the sentence is omitted when empty")
    acknowledge_subject: str = Field(default="", description="Override of the letter subject; placeholders {name} {project} {site}. Empty = built-in text per language")
    acknowledge_body: str = Field(default="", description="Override of the letter's main paragraph; placeholders {name} {project} {site}. Empty = built-in text per language")
    queue: str = Field(default="default", description="RQ queue for delivery jobs")
    max_attempts: int = Field(default=8, ge=1, le=50, description="Attempts before a row is marked dead")
    max_backoff_seconds: int = Field(default=3600, ge=30, description="Upper bound of the retry pause")
    stuck_after_seconds: int = Field(default=600, ge=60, description="A 'sending' row older than this is re-queued")
    sweep_interval_seconds: int = Field(default=60, ge=10, description="How often the sweeper runs (RQ schedule)")
    retention_days: int = Field(default=90, ge=1, description="Sent rows older than this are purged (they hold the payload)")
    timeout_seconds: float = Field(default=15.0, gt=0, le=120, description="HTTP timeout per Notion request")

    @field_validator("project_keys")
    @classmethod
    def _slug_keys(cls, v: Dict[str, str]) -> Dict[str, str]:
        from .keys import is_key

        out = {}
        for site, key in v.items():
            key = str(key).strip()
            if not is_key(key):
                raise ValueError(f"project key {key!r} of site {site!r} is not a lowercase slug like 'carapis' or 'mls-bali'")
            out[str(site).strip()] = key
        return out

    def get_rq_schedules(self):
        if not self.enabled:
            return []
        from django_cfg.models.django.django_rq import RQScheduleConfig

        return [
            RQScheduleConfig(
                func="django_cfg.modules.django_notion.tasks.sweep_outbox",
                interval=self.sweep_interval_seconds,
                timeout=300,
                queue=self.queue,
                description="Re-queue due and stuck Notion outbox rows, purge old sent rows",
            )
        ]

    def __repr_args__(self):  # never show the token, even masked
        for name, value in super().__repr_args__():
            if name != "token":
                yield name, value
        yield "token", "set" if self.token else "missing"


__all__ = ["NOTION_API_VERSION", "NotionConfig", "NotionTarget", "DEFAULT_COLUMNS", "COLUMN_TYPES", "TOKEN_ENV"]
