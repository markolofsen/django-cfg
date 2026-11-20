"""Realtime: one WebSocket per client, topic pub/sub over Redis Streams (`modules/django_realtime`).

`realtime_asgi(django_app)` serves `path` in the same process; `publish()` works from any sync Django code. Off by
default: a disabled endpoint refuses the handshake, `publish()` still validates and appends to the backend.

Env: every field as `REALTIME__<FIELD>` (e.g. `REALTIME__ENABLED=true`, `REALTIME__ALLOWED_ORIGINS=https://a.com,https://b.com`).
"""

from __future__ import annotations

from typing import Annotated, Any, List, Literal
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

RealtimeBackend = Literal["auto", "redis", "memory"]

#: Send-queue slots a replay must leave free (for `sub_ok`, live messages, `pong`); a larger replay answers
#: `recovered:false` instead.
REPLAY_MARGIN = 8


class RealtimeConfig(BaseSettings):
    """WebSocket endpoint, limits and backplane of `django_cfg.modules.django_realtime`."""

    model_config = SettingsConfigDict(
        env_prefix="REALTIME__",
        case_sensitive=False,
        validate_assignment=True,
        validate_default=True,
        extra="forbid",
    )

    enabled: bool = Field(default=False, description="Serve the WebSocket endpoint and install the module app")
    path: str = Field(default="/ws", description="URL path of the WebSocket endpoint")
    ping_interval: int = Field(
        default=25, ge=5, le=300,
        description=(
            "Seconds between the client's app-level `ping` (advertised in `hello`). Server-side liveness is uvicorn's "
            "protocol ping (--ws-ping-interval, close 1011); keep both below the proxy idle timeout (Cloudflare ~100 s)"
        ),
    )
    auth_timeout: int = Field(default=5, ge=1, le=60, description="Seconds the server waits for the first frame")
    default_history: int = Field(
        default=100, ge=1, le=100_000, description="Messages kept per topic when the topic sets no `history`",
    )
    max_connections_per_user: int = Field(
        default=10, ge=1, le=10_000,
        description="Open sockets per user (anonymous: per client IP) in one process; above it close 4429",
    )
    max_subscriptions: int = Field(default=100, ge=1, le=10_000, description="Topics per socket; above it sub_err limit")
    max_frame_bytes: int = Field(default=64_000, ge=256, le=1_048_576, description="Largest inbound frame accepted")
    send_queue: int = Field(
        default=256, ge=8, le=100_000,
        description="Outbound frames buffered per socket; a client that falls further behind is closed with 1013",
    )
    max_frames_per_second: int = Field(
        default=20, ge=1, le=10_000, description="Inbound frames per second per socket; above it close 4429",
    )
    db_threads: int = Field(
        default=4, ge=1, le=256,
        description=(
            "Threads that run auth and topic `allow` hooks: the ORM runs there, never on the event loop. Also the "
            "realtime share of the database pool; size the pool for the HTTP threads plus this"
        ),
    )
    hook_timeout: float = Field(
        default=5.0, gt=0, le=60,
        description="Seconds an auth or `allow` hook may take; then close 4500 (auth) or sub_err timeout (allow)",
    )
    reauth_interval: int = Field(
        default=900, ge=0, le=86_400,
        description="Seconds between re-checks of a socket's credential (catches revocations no signal reports); 0 = off",
    )
    history_ttl: int = Field(
        default=300, ge=1, le=7 * 86_400,
        description="Seconds a topic's replay history lives after its last publish (recovery is for short gaps)",
    )
    meta_ttl: int = Field(
        default=86_400, ge=1, le=30 * 86_400,
        description="Seconds a topic's epoch and offset live after its last publish; then the next publish starts a new epoch",
    )
    allowed_origins: Annotated[List[str], NoDecode] = Field(
        default_factory=list,
        description=(
            "Origins allowed on top of the same origin and CSRF_TRUSTED_ORIGINS "
            "(`https://app.example.com`, `https://*.example.com`)"
        ),
    )
    redis_pool_size: int = Field(
        default=20, ge=2, le=1_000,
        description="Redis connections per worker for subscribes and replays (the bus reader has its own); "
                    "callers beyond it wait up to `redis_pool_timeout`",
    )
    redis_pool_timeout: float = Field(
        default=5.0, gt=0, le=60, description="Seconds a subscribe waits for a free Redis connection",
    )
    backend: RealtimeBackend = Field(
        default="auto",
        description="auto: Redis Streams when DjangoConfig.redis_url is set, else in-process memory (dev, tests)",
    )

    @field_validator("path")
    @classmethod
    def _path(cls, value: str) -> str:
        if not value.startswith("/") or any(c in value for c in " ?#"):
            raise ValueError("realtime.path must be an absolute URL path, e.g. /ws")
        return value.rstrip("/") or "/"

    @model_validator(mode="after")
    def _sizes(self) -> "RealtimeConfig":
        if self.default_history + REPLAY_MARGIN > self.send_queue:
            raise ValueError(
                f"realtime.default_history ({self.default_history}) must be at most send_queue - {REPLAY_MARGIN} "
                f"({self.send_queue - REPLAY_MARGIN}): a full replay has to fit the send queue"
            )
        if self.meta_ttl < self.history_ttl:
            raise ValueError("realtime.meta_ttl must be >= history_ttl: history must not outlive its epoch")
        return self

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _split(cls, value: Any) -> Any:
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                import json

                return json.loads(text)
            return [part.strip() for part in text.split(",") if part.strip()]
        return value

    @field_validator("allowed_origins")
    @classmethod
    def _origins(cls, value: List[str]) -> List[str]:
        for item in value:
            parts = urlsplit(item)
            if parts.scheme not in ("http", "https") or not parts.netloc or parts.path not in ("", "/"):
                raise ValueError(f"realtime.allowed_origins: {item!r} is not an origin like https://app.example.com")
        return [item.rstrip("/") for item in value]


__all__ = ["REPLAY_MARGIN", "RealtimeBackend", "RealtimeConfig"]
