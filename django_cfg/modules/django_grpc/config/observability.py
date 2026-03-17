"""django_grpc.config.observability — Centrifugo publishing and Telegram notification config."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CentrifugoPublishConfig(BaseModel):
    """Controls which gRPC events are published to Centrifugo and on which channels."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=True, description="Enable Centrifugo event publishing")
    publish_start: bool = Field(default=False, description="Publish rpc_start events (high volume)")
    publish_end: bool = Field(default=True, description="Publish rpc_end events")
    publish_errors: bool = Field(default=True, description="Publish error events")
    publish_stream_messages: bool = Field(default=False, description="Publish per-message stream events (very high volume)")
    channel_template: str = Field(
        default="grpc:{service}:{method}:meta",
        description="Centrifugo channel pattern for method events",
    )
    error_channel_template: str = Field(
        default="grpc:{service}:{method}:errors",
        description="Centrifugo channel pattern for error events",
    )
    max_retries: int = Field(default=3, ge=0, le=10, description="Publish retry attempts on transient failure")
    max_concurrent_publishes: int = Field(
        default=100,
        ge=1,
        le=10_000,
        description="H-1: semaphore cap on concurrent fire-and-forget Centrifugo publish tasks",
    )


class TelegramNotifyConfig(BaseModel):
    """Controls Telegram error/event notifications from the gRPC interceptor."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(default=False, description="Send gRPC notifications to Telegram")
    exclude_methods: list[str] = Field(
        default_factory=lambda: [
            "/grpc.health.v1.Health/Check",
            "/grpc.health.v1.Health/Watch",
            "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo",
        ],
        description="Method paths excluded from Telegram notifications",
    )


class ObservabilityConfig(BaseModel):
    """Observability settings: request logging, Centrifugo publishing, Telegram alerts, OTel."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    centrifugo: CentrifugoPublishConfig = Field(default_factory=CentrifugoPublishConfig)
    telegram: TelegramNotifyConfig = Field(default_factory=TelegramNotifyConfig)
    # H-7: optional OpenTelemetry interceptor. Requires opentelemetry-instrumentation-grpc.
    # When True and the package is installed, OTel interceptor is prepended as the outermost
    # layer: OTel → ErrorHandling → Auth → Observability.
    otel_enabled: bool = Field(
        default=False,
        description="Prepend OpenTelemetryServerInterceptor (requires opentelemetry-instrumentation-grpc)",
    )


__all__ = ["CentrifugoPublishConfig", "TelegramNotifyConfig", "ObservabilityConfig"]
