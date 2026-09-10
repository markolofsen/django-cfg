"""Typed, provider-neutral contracts for Seedance-style reference video jobs."""

from __future__ import annotations

import base64
import binascii
from decimal import Decimal
import re
from typing import Annotated, Literal
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, model_validator

SeedanceModelFamily = Literal[
    "seedance-2.0",
    "seedance-2.0-fast",
    "seedance-2.0-mini",
]
MediaReferenceKind = Literal["image", "video", "audio"]
MediaReferenceRole = Literal[
    "character",
    "scene",
    "style",
    "storyboard",
    "first_frame",
    "last_frame",
    "motion",
    "camera",
    "audio",
    "source_video",
    "reference",
]
SeedanceRatio = Literal["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"]
SeedanceResolution = Literal["480p", "720p", "1080p", "4k"]
SeedanceJobStatus = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancelled",
    "expired",
]

_DATA_URI = re.compile(
    r"^data:(?P<mime>[a-z0-9.+-]+/[a-z0-9.+-]+);base64,(?P<data>[A-Za-z0-9+/]+={0,2})$"
)
_IMAGE_MIMES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/tiff",
    "image/gif",
    "image/heic",
    "image/heif",
}
_AUDIO_MIMES = {"audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3"}


def _validate_https_or_asset(value: str, *, field_name: str) -> str:
    if value.startswith("asset://"):
        if re.fullmatch(r"asset://[A-Za-z0-9._:-]+", value) is None:
            raise ValueError(f"{field_name} contains an invalid asset:// ID")
        return value
    parsed = urlsplit(value)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.fragment
    ):
        raise ValueError(
            f"{field_name} must be a credential-free HTTPS URL or asset:// ID"
        )
    return value


class SeedanceModel(BaseModel):
    """Canonical model identity separated from a provider ID and UI alias."""

    model_config = ConfigDict(extra="forbid")

    family: SeedanceModelFamily
    provider_model_id: str = Field(min_length=1)
    provider_alias: str | None = Field(default=None, min_length=1)

    @classmethod
    def standard(cls, *, alias: str | None = None) -> "SeedanceModel":
        return cls(
            family="seedance-2.0",
            provider_model_id="dreamina-seedance-2-0-260128",
            provider_alias=alias,
        )

    @classmethod
    def fast(cls, *, alias: str | None = None) -> "SeedanceModel":
        return cls(
            family="seedance-2.0-fast",
            provider_model_id="dreamina-seedance-2-0-fast-260128",
            provider_alias=alias,
        )

    @classmethod
    def mini(
        cls,
        *,
        provider_model_id: str,
        alias: str | None = None,
    ) -> "SeedanceModel":
        """Build Mini from the endpoint/model ID activated in ModelArk."""
        return cls(
            family="seedance-2.0-mini",
            provider_model_id=provider_model_id,
            provider_alias=alias,
        )


class MediaReference(BaseModel):
    """One ordered input with a portable semantic role.

    ``duration_seconds`` is required for video/audio so aggregate provider limits
    can be rejected before a paid submission. Image dimensions and binary sizes
    remain the caller's resolver responsibility; the transport validates the
    source form accepted by BytePlus.
    """

    model_config = ConfigDict(extra="forbid")

    kind: MediaReferenceKind
    role: MediaReferenceRole
    source: str = Field(min_length=1)
    duration_seconds: float | None = Field(default=None, ge=2, le=15)

    @model_validator(mode="after")
    def validate_source_and_duration(self) -> "MediaReference":
        if self.kind == "video":
            _validate_https_or_asset(self.source, field_name="video source")
            if self.source.startswith("data:"):
                raise ValueError("video references do not support Base64 data URIs")
        elif self.kind == "image":
            self._validate_data_or_remote(_IMAGE_MIMES, field_name="image source")
        else:
            self._validate_data_or_remote(_AUDIO_MIMES, field_name="audio source")

        if self.kind == "image" and self.duration_seconds is not None:
            raise ValueError("image references cannot have duration_seconds")
        if self.kind in {"video", "audio"} and self.duration_seconds is None:
            raise ValueError(f"{self.kind} references require duration_seconds")
        if self.role in {"first_frame", "last_frame"} and self.kind != "image":
            raise ValueError(f"{self.role} must be an image reference")
        return self

    def _validate_data_or_remote(
        self, allowed_mimes: set[str], *, field_name: str
    ) -> None:
        if not self.source.startswith("data:"):
            _validate_https_or_asset(self.source, field_name=field_name)
            return
        match = _DATA_URI.fullmatch(self.source)
        if match is None or match.group("mime") not in allowed_mimes:
            allowed = ", ".join(sorted(allowed_mimes))
            raise ValueError(
                f"{field_name} must use valid Base64 with one of: {allowed}"
            )
        try:
            decoded = base64.b64decode(match.group("data"), validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError(f"{field_name} contains invalid Base64") from exc
        maximum_bytes = 30 * 1024 * 1024 if self.kind == "image" else 15 * 1024 * 1024
        if len(decoded) >= maximum_bytes:
            maximum_mb = maximum_bytes // (1024 * 1024)
            raise ValueError(f"{field_name} must be smaller than {maximum_mb} MB")


class VideoOutputSpec(BaseModel):
    """Deterministic output settings supported by Seedance 2.0 series."""

    model_config = ConfigDict(extra="forbid")

    duration_seconds: Annotated[int, Field(ge=4, le=15)]
    ratio: SeedanceRatio
    resolution: SeedanceResolution
    generate_audio: bool = False
    watermark: bool = False
    return_last_frame: bool = True


class SeedanceGenerationRequest(BaseModel):
    """One paid candidate request; it carries no implicit retry policy."""

    model_config = ConfigDict(extra="forbid")

    model: SeedanceModel
    prompt: str = Field(min_length=1, max_length=10_000)
    references: list[MediaReference] = Field(default_factory=list, max_length=15)
    output: VideoOutputSpec
    safety_identifier: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_capabilities(self) -> "SeedanceGenerationRequest":
        images = [ref for ref in self.references if ref.kind == "image"]
        videos = [ref for ref in self.references if ref.kind == "video"]
        audios = [ref for ref in self.references if ref.kind == "audio"]
        if len(images) > 9:
            raise ValueError("Seedance supports at most 9 image references")
        if len(videos) > 3:
            raise ValueError("Seedance supports at most 3 video references")
        if len(audios) > 3:
            raise ValueError("Seedance supports at most 3 audio references")
        if sum(ref.duration_seconds or 0 for ref in videos) > 15:
            raise ValueError("Seedance reference videos may total at most 15 seconds")
        if sum(ref.duration_seconds or 0 for ref in audios) > 15:
            raise ValueError("Seedance reference audios may total at most 15 seconds")
        if audios and not (images or videos):
            raise ValueError("audio requires at least one image or video reference")
        estimated_body_bytes = (
            len(self.prompt.encode("utf-8"))
            + sum(
                len(ref.source.encode("ascii"))
                for ref in self.references
                if ref.source.startswith("data:")
            )
            + len(self.references) * 256
            + 4096
        )
        if estimated_body_bytes > 64 * 1024 * 1024:
            raise ValueError("BytePlus request body may not exceed 64 MB")

        exact_frames = [
            ref for ref in images if ref.role in {"first_frame", "last_frame"}
        ]
        if exact_frames:
            if len(exact_frames) != len(self.references):
                raise ValueError(
                    "exact first/last-frame mode cannot be mixed with multimodal references"
                )
            roles = [ref.role for ref in exact_frames]
            if roles.count("first_frame") != 1 or roles.count("last_frame") > 1:
                raise ValueError(
                    "exact-frame mode requires one first_frame and at most one last_frame"
                )

        if self.model.family != "seedance-2.0" and self.output.resolution in {
            "1080p",
            "4k",
        }:
            raise ValueError("Seedance Fast and Mini support only 480p or 720p")
        return self


class SeedanceUsage(BaseModel):
    model_config = ConfigDict(extra="allow")

    completion_tokens: int | None = Field(default=None, ge=0)
    total_tokens: int | None = Field(default=None, ge=0)


class SeedanceJob(BaseModel):
    """Submitted or retrieved BytePlus content-generation task."""

    model_config = ConfigDict(extra="allow")

    id: str = Field(min_length=1)
    status: SeedanceJobStatus = "queued"
    provider_reported_model_id: str | None = None
    video_url: str | None = None
    last_frame_url: str | None = None
    usage: SeedanceUsage | None = None
    error: dict[str, object] | None = None
    raw: dict[str, object] = Field(default_factory=dict)

    @property
    def terminal(self) -> bool:
        return self.status in {"succeeded", "failed", "cancelled", "expired"}


class SeedanceResult(BaseModel):
    """Immutable output and billing evidence from one completed task."""

    model_config = ConfigDict(extra="forbid")

    job_id: str
    canonical_model_family: SeedanceModelFamily
    provider_model_id: str
    provider_model_alias: str | None = None
    provider_reported_model_id: str | None = None
    video_url: str
    last_frame_url: str | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: Decimal | None = None
    cost_source: Literal["caller-supplied-token-rate"] | None = None


__all__ = [
    "MediaReference",
    "MediaReferenceKind",
    "MediaReferenceRole",
    "SeedanceGenerationRequest",
    "SeedanceJob",
    "SeedanceJobStatus",
    "SeedanceModel",
    "SeedanceModelFamily",
    "SeedanceRatio",
    "SeedanceResolution",
    "SeedanceResult",
    "SeedanceUsage",
    "VideoOutputSpec",
]
