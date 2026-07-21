"""Immutable temporary-media receipt returned by a publisher."""
from __future__ import annotations

from datetime import datetime
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator


class PublishedMedia(BaseModel):
    CLEANUP_AUTHORITY_SCHEMA_VERSION: ClassVar[int] = 1
    model_config = ConfigDict(extra="forbid", frozen=True)

    provider: str = Field(min_length=1)
    publication_id: str = Field(min_length=1)
    url: SecretStr
    revoke_token: SecretStr
    created_at: datetime
    expires_at: datetime
    content_type: str = Field(min_length=1)
    bytes: int = Field(gt=0)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    filename: str = Field(min_length=1)

    @model_validator(mode="after")
    def valid_window(self) -> "PublishedMedia":
        if self.created_at.tzinfo is None or self.expires_at.tzinfo is None:
            raise ValueError("publication timestamps must be timezone-aware")
        if self.expires_at <= self.created_at:
            raise ValueError("publication expiry must follow creation")
        return self

    def export_cleanup_authority(self) -> dict[str, Any]:
        """Return the explicit private-only representation needed for revoke."""
        return {
            "schema_version": self.CLEANUP_AUTHORITY_SCHEMA_VERSION,
            "provider": self.provider,
            "publication_id": self.publication_id,
            "url": self.url.get_secret_value(),
            "revoke_token": self.revoke_token.get_secret_value(),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "content_type": self.content_type,
            "bytes": self.bytes,
            "sha256": self.sha256,
            "filename": self.filename,
        }

    @classmethod
    def from_cleanup_authority(cls, value: dict[str, Any]) -> "PublishedMedia":
        """Validate and restore a private cleanup authority envelope."""
        payload = dict(value)
        version = payload.pop("schema_version", None)
        if version != cls.CLEANUP_AUTHORITY_SCHEMA_VERSION:
            raise ValueError(f"unsupported cleanup authority schema version: {version!r}")
        return cls.model_validate(payload)
