"""Provider-neutral media transport models."""

from __future__ import annotations

from datetime import timedelta
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from ..publication import PublishedMedia


class MediaTransportKind(StrEnum):
    """Wire representations supported by provider APIs."""

    DATA_URL = "data-url"
    MULTIPART = "multipart"
    PUBLIC_URL = "public-url"


class MediaTarget(StrEnum):
    """Built-in destinations with verified transport behavior."""

    OPENROUTER_IMAGE = "openrouter-image"
    MULTIPART_UPLOAD = "multipart-upload"
    PUBLIC_URL = "public-url"


class MediaTransportPolicy(BaseModel):
    """A destination's accepted transports in preference order."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9._-]*$")
    transports: tuple[MediaTransportKind, ...] = Field(min_length=1)
    max_bytes: int = Field(gt=0)
    content_types: frozenset[str] = Field(min_length=1)
    public_url_ttl: timedelta = timedelta(hours=6)

    @model_validator(mode="after")
    def valid_policy(self) -> "MediaTransportPolicy":
        if len(set(self.transports)) != len(self.transports):
            raise ValueError("policy transports must be unique")
        seconds = self.public_url_ttl.total_seconds()
        if seconds < 300 or seconds > 86_400:
            raise ValueError("public_url_ttl must be between 5 minutes and 24 hours")
        if any(not value or "/" not in value for value in self.content_types):
            raise ValueError("policy content_types must contain MIME types")
        return self


class PreparedMedia(BaseModel):
    """Exact provider input plus evidence; raw data is excluded from dumps."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    transport: MediaTransportKind
    content_type: str = Field(min_length=3)
    filename: str = Field(min_length=1)
    byte_size: int | None = Field(default=None, gt=0)
    sha256: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    verified: bool = True
    data: bytes | None = Field(default=None, exclude=True, repr=False)
    reference: SecretStr | None = None
    publication: PublishedMedia | None = Field(default=None, exclude=True, repr=False)

    @model_validator(mode="after")
    def valid_representation(self) -> "PreparedMedia":
        if self.transport is MediaTransportKind.MULTIPART:
            if self.data is None or self.reference is not None:
                raise ValueError("multipart media must contain data only")
        elif self.reference is None or self.data is not None:
            raise ValueError("URL transports must contain a reference only")
        if self.publication is not None and self.transport is not MediaTransportKind.PUBLIC_URL:
            raise ValueError("only public URL media can own a publication")
        if self.verified and (self.byte_size is None or self.sha256 is None):
            raise ValueError("verified media must include byte_size and sha256")
        return self

    def as_bytes(self) -> bytes:
        """Return multipart bytes, failing loudly for reference transports."""
        if self.data is None:
            raise TypeError(f"{self.transport.value} media is not multipart bytes")
        return self.data

    def as_reference(self) -> str:
        """Return a data/public URL, explicitly unmasking provider input."""
        if self.reference is None:
            raise TypeError(f"{self.transport.value} media is not a reference")
        return self.reference.get_secret_value()
