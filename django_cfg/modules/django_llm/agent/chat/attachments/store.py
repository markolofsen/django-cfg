"""The attachment store: stage an upload, bind it to a message, mint and check links, delete. Sync (ORM and storage); async callers wrap it.

Storage calls never run inside a database transaction that holds a thread lock: bytes are written first, the row after, and a failed
row removes the bytes. A file is the user's data: no name, text or derived text goes to a log line from here.
"""

from __future__ import annotations

import hashlib
import logging
import re
import tempfile
import uuid
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any

from django.core import signing
from django.core.files.base import File
from django.core.files.storage import storages
from django.utils import timezone

from django_cfg.modules.django_llm.agent.chat import kind as kinds
from django_cfg.modules.django_llm.agent.chat.attachments.policy import SUPPORTED_KINDS, AttachmentPolicy
from django_cfg.modules.django_llm.agent.chat.attachments.sniff import sniff
from django_cfg.modules.django_llm.agent.chat.errors import NotFound, QuotaExceeded
from django_cfg.modules.django_llm.agent.chat.turn import InvalidTurn

log = logging.getLogger(__name__)

SALT = "django_cfg.chat.attachment"
_NAME_CLEAN = re.compile(r"[\x00-\x1f\x7f/\\]+")
_CHUNK = 64 * 1024
_INLINE = frozenset({"image", "audio", "video"})


def clean_name(name: str) -> str:
    """A label for the chip: no path, no control characters, at most 200 characters. Never used as a storage key."""
    base = _NAME_CLEAN.sub(" ", (name or "").replace("\\", "/").rsplit("/", 1)[-1]).strip()
    return (base or "file")[:200]


def policy_of(kind_name: str) -> AttachmentPolicy:
    """The kind's policy; a kind that is gone or accepts no file is `NotFound`, the same answer as a missing route."""
    try:
        policy = kinds.get(kind_name).attachments
    except kinds.UnknownKind as err:
        raise NotFound(kind_name) from err
    if policy is None:
        raise NotFound(kind_name)
    return policy


class AttachmentStore:
    def __init__(self, model: Any):
        self.model = model

    # ── stage ───────────────────────────────────────────────────────────────────

    def stage(self, owner, kind_name: str, upload: Any, *, now: datetime | None = None):
        """Read the upload once (counting, hashing, sniffing while it streams), refuse what the policy refuses, keep the bytes, return the row.

        `upload` is a Django `UploadedFile` or anything with `.name` and `.chunks()` / `.read()`. Raises `InvalidTurn("file", code[, 413])`
        (`empty`, `too_large`, `unsupported_type`, `rejected`), `QuotaExceeded` (daily bytes), `NotFound` (the kind takes no files).
        """
        now = now or timezone.now()
        policy = policy_of(kind_name)
        name = clean_name(getattr(upload, "name", "") or "")
        spool = tempfile.SpooledTemporaryFile(max_size=8 * 1024 * 1024)  # noqa: SIM115 - closed in the finally below
        try:
            digest, size, head = hashlib.sha256(), 0, b""
            for chunk in _chunks(upload):
                size += len(chunk)
                if size > policy.max_bytes:
                    raise InvalidTurn("file", "too_large", status=413)  # stops reading: the rest of the body is never buffered
                if len(head) < 8192:
                    head += chunk[: 8192 - len(head)]
                digest.update(chunk)
                spool.write(chunk)
            if size == 0:
                raise InvalidTurn("file", "empty")
            found = sniff(head, name)
            if found is None or found[1] not in SUPPORTED_KINDS or not policy.accepts(*found):
                raise InvalidTurn("file", "unsupported_type", status=415)
            mime, media_kind = found
            self._check_daily(owner, policy, size, now)
            if media_kind == "image":
                _verify_image(spool)
            if policy.scan is not None:
                spool.seek(0)
                policy.scan(spool, mime)
            spool.seek(0)
            row_id = uuid.uuid4()
            key = f"chat/{kind_name}/{row_id}"
            storage = storages[policy.storage]
            saved = storage.save(key, File(spool, name=key))
            try:
                return self.model.objects.create(
                    id=row_id, owner=owner, chat_kind=kind_name, media_kind=media_kind, name=name, mime=mime, size=size,
                    sha256=digest.hexdigest(), storage=policy.storage, file=saved, status="staged", created_at=now,
                )
            except BaseException:
                _drop(storage, saved)
                raise
        finally:
            spool.close()

    def _check_daily(self, owner, policy: AttachmentPolicy, size: int, now: datetime) -> None:
        if policy.daily_bytes is None:
            return
        from django.db.models import Sum

        start = datetime.combine(now.astimezone(dt_timezone.utc).date(), datetime.min.time(), tzinfo=dt_timezone.utc)
        used = self.model.objects.stored_since(owner, start).aggregate(total=Sum("size"))["total"] or 0
        if used + size > policy.daily_bytes:
            raise QuotaExceeded("daily attachment bytes", code="rate_limited", status=429)

    # ── read, delete ────────────────────────────────────────────────────────────

    def get(self, owner, attachment_id: uuid.UUID):
        """The owner's row, or `NotFound`: a stranger's file and a missing one are one answer."""
        found = self.model.objects.for_owner(owner).filter(pk=attachment_id).first()
        if found is None:
            raise NotFound(str(attachment_id))
        return found

    def destroy(self, owner, attachment_id: uuid.UUID) -> None:
        """Remove a staged file (the user took the chip off): the file first, then the row. A sent one stays with its message."""
        row = self.model.objects.for_owner(owner).staged().filter(pk=attachment_id).first()
        if row is None:
            raise NotFound(str(attachment_id))
        self.delete_rows([row])

    def delete_rows(self, rows: list) -> int:
        """Delete the bytes, then the row; a row whose bytes could not be deleted is kept for the next pass. Returns rows removed."""
        gone = 0
        for row in rows:
            if not _drop(storages[row.storage], row.file.name):
                continue
            self.model.objects.filter(pk=row.pk).delete()
            gone += 1
        return gone

    def expire(self, rows: list) -> int:
        """Delete the bytes of sent files and mark the rows `expired` (the row, the name and `derived` stay). A file that could not be deleted
        keeps its row as it was and is tried again by the next pass. Returns rows expired."""
        done = 0
        for row in rows:
            if not _drop(storages[row.storage], row.file.name):
                continue
            self.model.objects.filter(pk=row.pk).update(status="expired", file="")
            done += 1
        return done

    def reap_lapsed(self, now: datetime | None = None, *, batch: int = 200) -> int:
        """Expire every sent file past its kind's `keep_days` (0 and None are not a calendar: 0 is done when the turn ends, None never). Returns rows."""
        now = now or timezone.now()
        total = 0
        for kind_name in list(kinds.names()):
            policy = kinds.get(kind_name).attachments
            if policy is None or not policy.keep_days:
                continue
            cutoff = now - timedelta(days=policy.keep_days)
            total += self.expire(list(self.model.objects.lapsed(cutoff).filter(chat_kind=kind_name)[:batch]))
        return total

    def open(self, row):
        return storages[row.storage].open(row.file.name, "rb")

    # ── bind ────────────────────────────────────────────────────────────────────

    def lock_staged(self, owner, kind_name: str, ids: list[uuid.UUID], policy: AttachmentPolicy) -> list:
        """The rows of `ids`, checked against the policy for a message. Raises `InvalidTurn("attachments", code)`: `too_many`, `duplicate`,
        `unavailable` (not yours, not staged, another kind: one code), `too_large` (the total)."""
        if len(ids) != len(set(ids)):
            raise InvalidTurn("attachments", "duplicate")
        if len(ids) > policy.max_files:
            raise InvalidTurn("attachments", "too_many")
        rows = list(self.model.objects.for_owner(owner).staged().filter(pk__in=ids, chat_kind=kind_name))
        if len(rows) != len(ids):
            raise InvalidTurn("attachments", "unavailable")
        if sum(r.size for r in rows) > policy.max_total_bytes:
            raise InvalidTurn("attachments", "too_large", status=413)
        by_id = {r.pk: r for r in rows}
        return [by_id[i] for i in ids]

    def bind(self, owner, ids: list[uuid.UUID], message_id: uuid.UUID, kind_name: str) -> int:
        """Attach the staged rows to the message. `UPDATE ... WHERE status = 'staged'` decides a race: whoever updates first wins. No storage call."""
        return self.model.objects.for_owner(owner).staged().filter(pk__in=ids, chat_kind=kind_name).update(message_id=message_id, status="attached")

    # ── expiry ──────────────────────────────────────────────────────────────────

    def reap_staged(self, now: datetime | None = None, *, batch: int = 200) -> int:
        """Delete every staged upload past its kind's TTL (file first, then row). Returns rows removed."""
        now = now or timezone.now()
        total = 0
        for kind_name in list(kinds.names()):
            policy = kinds.get(kind_name).attachments
            if policy is None:
                continue
            cutoff = now - timedelta(hours=policy.staged_ttl_hours)
            rows = list(self.model.objects.expired(cutoff).filter(chat_kind=kind_name)[:batch])
            total += self.delete_rows(rows)
        return total

    # ── links ───────────────────────────────────────────────────────────────────

    def token(self, row, actor_id: Any) -> str:
        return signing.dumps({"a": str(row.pk), "u": str(actor_id)}, salt=SALT, compress=False)

    def check_token(self, token: str, attachment_id: uuid.UUID, ttl_s: int) -> str | None:
        """The actor id a valid token names for this attachment, or None (bad, expired, or for another file)."""
        try:
            data = signing.loads(token, salt=SALT, max_age=ttl_s)
        except signing.BadSignature:
            return None
        if not isinstance(data, dict) or data.get("a") != str(attachment_id):
            return None
        return str(data.get("u"))

    def url(self, row, actor_id: Any, policy: AttachmentPolicy, make_signed_url) -> str:
        """A fresh link for a reader. `signed`: the API route with a token (`make_signed_url(row, token)`); `presigned` / `public`: the storage's own."""
        if row.status == "expired" or not row.file:
            return ""
        if policy.delivery == "signed":
            return make_signed_url(row, self.token(row, actor_id))
        storage = storages[row.storage]
        if policy.delivery == "presigned":
            try:
                return storage.url(row.file.name, expire=policy.url_ttl_s)
            except TypeError:  # a storage without expiring links: fall back to the API route rather than leak a permanent URL
                return make_signed_url(row, self.token(row, actor_id))
        return storage.url(row.file.name)


def is_inline(mime: str, media_kind: str) -> bool:
    """Only sniffed image, audio, video and PDF may render in the browser; everything else downloads."""
    return media_kind in _INLINE or mime == "application/pdf"


def _chunks(upload: Any):
    if hasattr(upload, "chunks"):
        yield from upload.chunks(_CHUNK)
        return
    while chunk := upload.read(_CHUNK):
        yield chunk


def _verify_image(spool: Any) -> None:
    try:
        from PIL import Image
    except ImportError:  # Pillow is optional here: the magic bytes already decided the type
        return
    spool.seek(0)
    try:
        with Image.open(spool) as im:
            im.verify()
    except Exception as err:  # noqa: BLE001 - any decoder failure is a refusal
        raise InvalidTurn("file", "unsupported_type", status=415) from err


def _drop(storage: Any, name: str) -> bool:
    try:
        storage.delete(name)
        return True
    except Exception:  # noqa: BLE001 - the row stays; the next reaper pass retries
        log.warning("chat attachments: could not delete a stored file", exc_info=True)
        return False
