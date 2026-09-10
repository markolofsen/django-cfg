"""Provider-neutral contracts for asynchronous image-to-video generation."""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

VideoFrameType = Literal["first_frame", "last_frame"]
VideoJobStatus = Literal[
    "pending",
    "queued",
    "in_progress",
    "processing",
    "running",
    "generating",
    "completed",
    "failed",
    "cancelled",
    "expired",
]


def _require_https(value: str, *, field_name: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError(f"{field_name} must be an HTTPS URL without credentials")
    return value


class VideoImageURL(BaseModel):
    """OpenRouter's nested image URL object."""

    model_config = ConfigDict(extra="forbid")

    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, value: str) -> str:
        return _require_https(value, field_name="image URL")


class VideoFrameImage(BaseModel):
    """An exact first or last frame for image-to-video generation."""

    model_config = ConfigDict(extra="forbid")

    type: Literal["image_url"] = "image_url"
    image_url: VideoImageURL
    frame_type: VideoFrameType

    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        frame_type: VideoFrameType = "first_frame",
    ) -> "VideoFrameImage":
        return cls(image_url=VideoImageURL(url=url), frame_type=frame_type)


class VideoGenRequest(BaseModel):
    """A provider-neutral request matching OpenRouter's ``POST /videos`` API."""

    model_config = ConfigDict(extra="forbid")

    model: str = Field(min_length=1)
    prompt: str = Field(min_length=1)
    duration: int | None = Field(default=None, ge=1)
    resolution: str | None = None
    aspect_ratio: str | None = None
    size: str | None = Field(default=None, pattern=r"^[1-9]\d*x[1-9]\d*$")
    frame_images: list[VideoFrameImage] = Field(default_factory=list, max_length=2)
    generate_audio: bool = False
    seed: int | None = None
    callback_url: str | None = None
    provider: dict[str, Any] | None = None

    @field_validator("callback_url")
    @classmethod
    def validate_callback_url(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _require_https(value, field_name="callback URL")

    @model_validator(mode="after")
    def validate_shape_and_frames(self) -> "VideoGenRequest":
        if self.size is not None and (
            self.resolution is not None or self.aspect_ratio is not None
        ):
            raise ValueError("size cannot be combined with resolution or aspect_ratio")
        frame_types = [frame.frame_type for frame in self.frame_images]
        if len(frame_types) != len(set(frame_types)):
            raise ValueError("frame_images may contain each frame_type only once")
        return self

    @classmethod
    def image_to_video(
        cls,
        *,
        model: str,
        prompt: str,
        first_frame_url: str,
        **kwargs: Any,
    ) -> "VideoGenRequest":
        """Build the common first-frame I2V request without exposing wire nesting."""
        return cls(
            model=model,
            prompt=prompt,
            frame_images=[VideoFrameImage.from_url(first_frame_url)],
            **kwargs,
        )

    def to_api_payload(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_none=True, exclude_defaults=False)


class VideoModelCapability(BaseModel):
    """Current capabilities and prices returned by ``GET /videos/models``."""

    model_config = ConfigDict(extra="allow")

    id: str
    canonical_slug: str | None = None
    name: str | None = None
    description: str | None = None
    created: int | None = None
    generate_audio: bool | None = None
    seed: bool | None = None
    supported_durations: list[int] = Field(default_factory=list)
    supported_resolutions: list[str] = Field(default_factory=list)
    supported_aspect_ratios: list[str] = Field(default_factory=list)
    supported_sizes: list[str] | None = None
    supported_frame_images: list[VideoFrameType] = Field(default_factory=list)
    pricing_skus: dict[str, Decimal] = Field(default_factory=dict)
    allowed_passthrough_parameters: list[str] = Field(default_factory=list)

    @field_validator(
        "supported_durations",
        "supported_resolutions",
        "supported_aspect_ratios",
        "supported_frame_images",
        "allowed_passthrough_parameters",
        mode="before",
    )
    @classmethod
    def nullable_lists_are_unknown(cls, value: Any) -> Any:
        """OpenRouter may encode an unknown capability list as JSON null."""
        return [] if value is None else value

    def incompatibilities(self, request: VideoGenRequest) -> list[str]:
        """Return explicit capability mismatches; absent metadata stays unknown."""
        problems: list[str] = []
        if request.duration is not None and self.supported_durations:
            if request.duration not in self.supported_durations:
                problems.append(f"duration={request.duration}")
        if request.resolution is not None and self.supported_resolutions:
            if request.resolution not in self.supported_resolutions:
                problems.append(f"resolution={request.resolution}")
        if request.aspect_ratio is not None and self.supported_aspect_ratios:
            if request.aspect_ratio not in self.supported_aspect_ratios:
                problems.append(f"aspect_ratio={request.aspect_ratio}")
        if request.size is not None and self.supported_sizes:
            if request.size not in self.supported_sizes:
                problems.append(f"size={request.size}")
        for frame in request.frame_images:
            if (
                self.supported_frame_images
                and frame.frame_type not in self.supported_frame_images
            ):
                problems.append(f"frame_type={frame.frame_type}")
        if request.generate_audio and self.generate_audio is False:
            problems.append("generate_audio=true")
        return problems


class VideoUsage(BaseModel):
    """Provider-reported cost evidence for a completed job."""

    model_config = ConfigDict(extra="allow")

    cost: Decimal | None = None
    is_byok: bool | None = None


class VideoGenJob(BaseModel):
    """A submitted or polled OpenRouter video job."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1)
    polling_url: str
    status: VideoJobStatus
    generation_id: str | None = None
    unsigned_urls: list[str] = Field(default_factory=list)
    usage: VideoUsage | None = None
    error: str | dict[str, Any] | None = None

    @property
    def terminal(self) -> bool:
        return self.status in {"completed", "failed", "cancelled", "expired"}


class VideoGenEstimate(BaseModel):
    """Preflight estimate derived from one live capability pricing SKU."""

    model_id: str
    cost_usd: Decimal
    pricing_sku: str
    unit_price_usd: Decimal
    quantity: Decimal
    source: Literal["live-capability"] = "live-capability"


class VideoGenResult(BaseModel):
    """Completed provider result with immutable cost and output URL evidence."""

    job_id: str
    generation_id: str | None = None
    output_urls: list[str] = Field(min_length=1)
    cost_usd: Decimal | None = None
    is_byok: bool | None = None

    @classmethod
    def from_job(cls, job: VideoGenJob) -> "VideoGenResult":
        if job.status != "completed":
            raise ValueError("video result requires a completed job")
        usage = job.usage or VideoUsage()
        return cls(
            job_id=job.id,
            generation_id=job.generation_id,
            output_urls=job.unsigned_urls,
            cost_usd=usage.cost,
            is_byok=usage.is_byok,
        )


__all__ = [
    "VideoFrameImage",
    "VideoFrameType",
    "VideoGenEstimate",
    "VideoGenJob",
    "VideoGenRequest",
    "VideoGenResult",
    "VideoImageURL",
    "VideoJobStatus",
    "VideoModelCapability",
    "VideoUsage",
]
