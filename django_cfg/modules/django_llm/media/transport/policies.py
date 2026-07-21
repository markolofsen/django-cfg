"""Single source of truth for built-in provider media policies."""

from types import MappingProxyType
from typing import Final, Mapping

from ..publication.providers.sdkrouter import SDKROUTER_MAX_BYTES
from .models import MediaTarget, MediaTransportKind, MediaTransportPolicy

IMAGE_CONTENT_TYPES: Final = frozenset({
    "image/png", "image/jpeg", "image/webp", "image/gif", "image/avif",
})
PUBLIC_MEDIA_CONTENT_TYPES: Final = IMAGE_CONTENT_TYPES | frozenset({"video/mp4", "video/webm"})

OPENROUTER_IMAGE_POLICY: Final = MediaTransportPolicy(
    name=MediaTarget.OPENROUTER_IMAGE.value,
    transports=(MediaTransportKind.DATA_URL, MediaTransportKind.PUBLIC_URL),
    max_bytes=20 * 1024 * 1024,
    content_types=IMAGE_CONTENT_TYPES,
)
MULTIPART_UPLOAD_POLICY: Final = MediaTransportPolicy(
    name=MediaTarget.MULTIPART_UPLOAD.value,
    transports=(MediaTransportKind.MULTIPART, MediaTransportKind.PUBLIC_URL),
    max_bytes=20 * 1024 * 1024,
    content_types=PUBLIC_MEDIA_CONTENT_TYPES,
)
PUBLIC_URL_POLICY: Final = MediaTransportPolicy(
    name=MediaTarget.PUBLIC_URL.value,
    transports=(MediaTransportKind.PUBLIC_URL,),
    max_bytes=SDKROUTER_MAX_BYTES,
    content_types=PUBLIC_MEDIA_CONTENT_TYPES,
)

DEFAULT_MEDIA_POLICIES: Final[Mapping[MediaTarget, MediaTransportPolicy]] = MappingProxyType({
    MediaTarget.OPENROUTER_IMAGE: OPENROUTER_IMAGE_POLICY,
    MediaTarget.MULTIPART_UPLOAD: MULTIPART_UPLOAD_POLICY,
    MediaTarget.PUBLIC_URL: PUBLIC_URL_POLICY,
})
