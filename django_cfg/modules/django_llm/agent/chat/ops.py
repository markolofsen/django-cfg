"""Operator jobs over a host's chat tables: close dead answers, drop idle sessions. The commands `chat_reap` and `chat_prune` call these.

Counts only: nothing here reads, prints or logs a title or a message (they are the user's text).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.apps import apps
from django.db.models import Max
from django.db.models.functions import Coalesce
from django.utils import timezone

from django_cfg.modules.django_llm.agent.chat.models import AbstractThread
from django_cfg.modules.django_llm.agent.chat.service import ChatPolicy, ChatService

REAP_AFTER_S = 120.0  # keep above every kind's `limits.timeout_s`
PRUNE_AFTER_DAYS = 180


class ThreadModelError(LookupError):
    pass


def thread_model(label: str | None = None):
    """The host's concrete thread model: `app_label.Model`, or the only subclass of `AbstractThread` installed."""
    if label:
        try:
            model = apps.get_model(label)
        except (LookupError, ValueError) as err:
            raise ThreadModelError(f"no model {label!r}") from err
        if not issubclass(model, AbstractThread):
            raise ThreadModelError(f"{label} is not a subclass of AbstractThread")
        return model
    found = [m for m in apps.get_models() if issubclass(m, AbstractThread)]
    if len(found) == 1:
        return found[0]
    names = ", ".join(m._meta.label for m in found) or "none installed"
    raise ThreadModelError(f"say which thread model to use with --model (found: {names})")


def reap(model, *, older_than_s: float = REAP_AFTER_S, now: datetime | None = None) -> int:
    """Close every assistant answer left `running` for longer than `older_than_s` as `error` / `failed`."""
    return ChatService(model, ChatPolicy(stale_run_seconds=older_than_s)).reap_stale(now)


def attachment_store(model):
    """`AttachmentStore` over the attachment table of the host's chat, or None when the host declared none."""
    message_model = model.messages.rel.related_model
    descriptor = getattr(message_model, "attachments", None)
    if descriptor is None or not hasattr(descriptor, "rel"):
        return None
    from django_cfg.modules.django_llm.agent.chat.attachments.store import AttachmentStore

    return AttachmentStore(descriptor.rel.related_model)


def reap_attachments(model, *, now: datetime | None = None) -> int:
    """Delete staged uploads nobody sent, past their kind's TTL: the file first, then the row. Returns rows removed."""
    store = attachment_store(model)
    return store.reap_staged(now) if store is not None else 0


@dataclass(frozen=True)
class Pruned:
    threads: int
    messages: int
    files: int = 0


def prune(model, *, days: int = PRUNE_AFTER_DAYS, kind: str | None = None, dry_run: bool = False, batch: int = 500, now: datetime | None = None) -> Pruned:
    """Delete threads (their messages cascade) whose last activity is older than `days`. Activity is the newest message, or the
    thread's creation when it has none. `dry_run` counts and deletes nothing."""
    if days < 1:
        raise ValueError("days must be at least 1")
    cutoff = (now or timezone.now()) - timedelta(days=days)
    message_model = model.messages.rel.related_model
    idle = model.objects.annotate(last_activity=Coalesce(Max("messages__created_at"), "created_at")).filter(last_activity__lt=cutoff)
    if kind:
        idle = idle.filter(kind=kind)
    if dry_run:
        pks = list(idle.values_list("pk", flat=True))
        store = attachment_store(model)
        return Pruned(len(pks), message_model.objects.filter(thread_id__in=pks).count(), store.model.objects.filter(message__thread_id__in=pks).count() if store else 0)
    store = attachment_store(model)
    threads = messages = files = 0
    stuck: set = set()  # threads whose files could not be deleted this run: kept whole, retried by the next one
    while True:
        pks = list(idle.exclude(pk__in=stuck).values_list("pk", flat=True)[:batch])
        if not pks:
            return Pruned(threads, messages, files)
        if store is not None:  # a cascade would drop the rows and strand the bytes in storage: delete the files first
            rows = list(store.model.objects.filter(message__thread_id__in=pks))
            files += store.delete_rows(rows)
            stuck |= set(store.model.objects.filter(message__thread_id__in=pks).values_list("message__thread_id", flat=True))
            pks = [pk for pk in pks if pk not in stuck]
            if not pks:
                continue
        _, per_model = model.objects.filter(pk__in=pks).delete()
        threads += per_model.get(model._meta.label, 0)
        messages += per_model.get(message_model._meta.label, 0)


@dataclass(frozen=True)
class Drift:
    rows: int  # attachment rows examined
    missing: int  # rows whose file is gone from storage
    orphans: int  # files under `chat/` that no row points at
    removed: int  # orphans deleted (`fix=True`, and older than `grace_hours`)


def check_attachments(model, *, fix: bool = False, grace_hours: float = 24.0, now: datetime | None = None) -> Drift:
    """Compare the attachment table with the storage: rows without a file, files without a row. Counts only; no name is read out.

    `fix` deletes orphan files older than `grace_hours` (a file being uploaded has no row for a moment). Missing files are reported, never
    "repaired": a row without its bytes is the user's record of a message and stays.
    """
    from django.core.files.storage import storages

    store = attachment_store(model)
    if store is None:
        return Drift(0, 0, 0, 0)
    now = now or timezone.now()
    rows = missing = orphans = removed = 0
    by_storage: dict[str, set[str]] = {}
    for row in store.model.objects.all().only("storage", "file").iterator():
        rows += 1
        by_storage.setdefault(row.storage, set()).add(row.file.name)
        try:
            if not storages[row.storage].exists(row.file.name):
                missing += 1
        except Exception:  # noqa: BLE001 - an unreachable store is not "missing": do not count it
            continue
    for alias, known in by_storage.items():
        storage = storages[alias]
        for name in _walk(storage, "chat"):
            if name in known:
                continue
            orphans += 1
            if not fix:
                continue
            try:
                if (now - storage.get_modified_time(name).astimezone(now.tzinfo)).total_seconds() < grace_hours * 3600:
                    continue
                storage.delete(name)
                removed += 1
            except Exception:  # noqa: BLE001 - a storage that cannot say its ages is never swept
                continue
    return Drift(rows, missing, orphans, removed)


def _walk(storage, prefix: str):
    try:
        dirs, files = storage.listdir(prefix)
    except (FileNotFoundError, NotImplementedError):
        return
    for f in files:
        yield f"{prefix}/{f}"
    for d in dirs:
        yield from _walk(storage, f"{prefix}/{d}")
