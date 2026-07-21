"""Automatic provider media transport selection."""

from .errors import MediaPolicyError, MediaSourceError, MediaTransportError
from .models import (
    MediaTarget,
    MediaTransportKind,
    MediaTransportPolicy,
    PreparedMedia,
)
from .policies import (
    DEFAULT_MEDIA_POLICIES,
    MULTIPART_UPLOAD_POLICY,
    OPENROUTER_IMAGE_POLICY,
    PUBLIC_URL_POLICY,
)
from .router import MediaLease, MediaTransportRouter
from .sources import MediaSource

__all__ = [
    "DEFAULT_MEDIA_POLICIES",
    "MULTIPART_UPLOAD_POLICY",
    "MediaLease",
    "MediaPolicyError",
    "MediaSource",
    "MediaSourceError",
    "MediaTarget",
    "MediaTransportError",
    "MediaTransportKind",
    "MediaTransportPolicy",
    "MediaTransportRouter",
    "OPENROUTER_IMAGE_POLICY",
    "PUBLIC_URL_POLICY",
    "PreparedMedia",
]
