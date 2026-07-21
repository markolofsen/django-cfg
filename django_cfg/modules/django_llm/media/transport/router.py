"""Automatic media representation selection for provider adapters."""

from __future__ import annotations

import mimetypes
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

from ..publication import SdkRouterPublisher, TemporaryMediaPublisher
from .errors import MediaPolicyError, MediaSourceError
from .models import (
    MediaTarget,
    MediaTransportKind,
    MediaTransportPolicy,
    PreparedMedia,
)
from .policies import DEFAULT_MEDIA_POLICIES
from .sources import (
    MediaSource,
    decode_data_url,
    encode_data_url,
    filename_from_url,
    is_remote_url,
    load_local_media,
    validate_public_url,
)


class MediaLease:
    """Prepared provider input with explicit, idempotent CDN revocation."""

    def __init__(self, prepared: PreparedMedia, publisher: TemporaryMediaPublisher | None = None) -> None:
        self.prepared = prepared
        self._publisher = publisher
        self._revoked = False

    @property
    def managed_publication(self) -> bool:
        return self.prepared.publication is not None

    @property
    def revoked(self) -> bool:
        return self._revoked

    def revoke(self) -> None:
        """Revoke an owned CDN object; direct inputs are harmless no-ops."""
        if self._revoked or self.prepared.publication is None:
            return
        if self._publisher is None:
            raise RuntimeError("managed media lease has no publisher")
        self._publisher.revoke(self.prepared.publication)
        self._revoked = True

    async def arevoke(self) -> None:
        if self._revoked or self.prepared.publication is None:
            return
        if self._publisher is None:
            raise RuntimeError("managed media lease has no publisher")
        await self._publisher.arevoke(self.prepared.publication)
        self._revoked = True


class MediaTransportRouter:
    """Choose the first feasible representation declared by a provider policy."""

    def __init__(
        self,
        *,
        publisher: TemporaryMediaPublisher | None = None,
        policies: Mapping[MediaTarget, MediaTransportPolicy] = DEFAULT_MEDIA_POLICIES,
    ) -> None:
        self._publisher = publisher
        self._policies = dict(policies)

    def prepare_for(
        self,
        target: MediaTarget,
        source: MediaSource,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> MediaLease:
        try:
            policy = self._policies[target]
        except KeyError as exc:
            raise MediaPolicyError(f"no media transport policy registered for {target}") from exc
        return self.prepare(source, policy=policy, filename=filename, content_type=content_type)

    def prepare(
        self,
        source: MediaSource,
        *,
        policy: MediaTransportPolicy,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> MediaLease:
        if isinstance(source, str) and is_remote_url(source):
            if MediaTransportKind.PUBLIC_URL not in policy.transports:
                raise MediaPolicyError(f"{policy.name} does not accept a public URL")
            reference = validate_public_url(source)
            resolved_filename = filename or filename_from_url(reference)
            resolved_type = content_type or mimetypes.guess_type(resolved_filename)[0]
            if resolved_type is None:
                raise MediaSourceError("content_type is required for an untyped remote URL")
            resolved_type = resolved_type.split(";", 1)[0].strip().lower()
            if resolved_type not in policy.content_types:
                raise MediaPolicyError(f"{policy.name} does not accept content type {resolved_type}")
            prepared = PreparedMedia(
                transport=MediaTransportKind.PUBLIC_URL,
                content_type=resolved_type,
                filename=resolved_filename,
                reference=reference,
                verified=False,
            )
            return MediaLease(prepared)

        if isinstance(source, str) and source.startswith("data:"):
            media = decode_data_url(source, max_bytes=policy.max_bytes)
            if filename is not None or content_type is not None:
                media = load_local_media(
                    media.data,
                    max_bytes=policy.max_bytes,
                    filename=filename or media.filename,
                    content_type=content_type or media.content_type,
                )
        else:
            media = load_local_media(
                source,
                max_bytes=policy.max_bytes,
                filename=filename,
                content_type=content_type,
            )
        if media.content_type not in policy.content_types:
            raise MediaPolicyError(
                f"{policy.name} does not accept content type {media.content_type}"
            )

        for transport in policy.transports:
            if transport is MediaTransportKind.DATA_URL:
                return MediaLease(PreparedMedia(
                    transport=transport,
                    content_type=media.content_type,
                    filename=media.filename,
                    byte_size=len(media.data),
                    sha256=media.sha256,
                    reference=encode_data_url(media),
                ))
            if transport is MediaTransportKind.MULTIPART:
                return MediaLease(PreparedMedia(
                    transport=transport,
                    content_type=media.content_type,
                    filename=media.filename,
                    byte_size=len(media.data),
                    sha256=media.sha256,
                    data=media.data,
                ))
            if transport is MediaTransportKind.PUBLIC_URL:
                publisher = self._publisher or SdkRouterPublisher()
                publication = publisher.publish(
                    media.data,
                    filename=media.filename,
                    content_type=media.content_type,
                    expires_in=policy.public_url_ttl,
                    expected_sha256=media.sha256,
                )
                try:
                    publication_url = validate_public_url(publication.url.get_secret_value())
                    minimum_expiry = datetime.now(timezone.utc) + policy.public_url_ttl
                    if (
                        publication.content_type != media.content_type
                        or publication.content_type not in policy.content_types
                        or publication.bytes != len(media.data)
                        or publication.sha256 != media.sha256
                        or publication.filename != media.filename
                        or publication.expires_at < minimum_expiry - timedelta(seconds=10)
                    ):
                        raise MediaPolicyError("publisher receipt does not match prepared media")
                except Exception as exc:
                    try:
                        publisher.revoke(publication)
                    except Exception:
                        pass
                    if isinstance(exc, MediaPolicyError):
                        raise
                    raise MediaPolicyError("publisher returned an invalid public media receipt") from exc
                self._publisher = publisher
                return MediaLease(PreparedMedia(
                    transport=transport,
                    content_type=publication.content_type,
                    filename=media.filename,
                    byte_size=publication.bytes,
                    sha256=publication.sha256,
                    reference=publication_url,
                    publication=publication,
                ), publisher)
        raise MediaPolicyError(f"{policy.name} has no usable media transport")


__all__ = ["MediaLease", "MediaTransportRouter"]
