"""
The outbox worker: delete the queued files, then purge their URLs.

Safe to run twice and late: a missing object counts as deleted, a row is
claimed with a lease so two workers never take the same one, and a failure
moves `next_attempt_at` out with exponential backoff instead of losing the key.
"""

from __future__ import annotations

import logging
import random
from dataclasses import asdict, dataclass
from datetime import timedelta
from typing import Any, Optional

from django.utils import timezone

from ..config import get_config
from .cdn import get_purger
from .guard import refusal
from .storage_walk import walk

logger = logging.getLogger("storage.outbox")

#: A claimed row is invisible to other workers this long; longer than a task's timeout.
LEASE = timedelta(minutes=15)
MAX_BACKOFF = timedelta(hours=6)


@dataclass
class DrainStats:
    """What one run did. `would_delete` counts keys in a dry run."""

    picked: int = 0
    deleted_files: int = 0
    purged_urls: int = 0
    purge_skipped: int = 0
    retried: int = 0
    failed: int = 0
    refused: int = 0
    would_delete: int = 0
    dry_run: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


def drain(*, limit: Optional[int] = None, dry_run: Optional[bool] = None, now: Any = None) -> DrainStats:
    """Process due outbox rows. Never raises for a single row's failure."""
    from ..models import StorageDeletion

    config = get_config()
    dry = config.dry_run if dry_run is None else dry_run
    now = now or timezone.now()
    stats = DrainStats(dry_run=dry)
    purger = get_purger(config.cdn) if not dry else None

    due = StorageDeletion.objects.filter(
        status__in=[StorageDeletion.Status.PENDING, StorageDeletion.Status.PURGE],
        next_attempt_at__lte=now,
        claimed_by="",
    ).order_by("id")[: limit or config.batch_size]

    for row in list(due):
        if not dry:
            claimed = StorageDeletion.objects.filter(pk=row.pk, next_attempt_at=row.next_attempt_at).update(
                next_attempt_at=now + LEASE
            )
            if claimed != 1:
                continue
        stats.picked += 1
        _process(row, config, purger, stats, now, dry)
    return stats


def _process(row: Any, config: Any, purger: Any, stats: DrainStats, now: Any, dry: bool) -> None:
    from ..models import StorageDeletion

    reason = refusal(row.key, row.is_prefix, config.allowed_prefixes)
    if reason:
        logger.warning("refused %s:%s (%s)", row.storage_alias, row.key, reason)
        stats.refused += 1
        if not dry:
            row.status = StorageDeletion.Status.REFUSED
            row.last_error = reason
            row.save(update_fields=["status", "last_error", "updated_at"])
        return

    try:
        from django.core.files.storage import storages

        storage = storages[row.storage_alias]

        if row.status == StorageDeletion.Status.PENDING:
            keys = list(walk(storage, row.key)) if row.is_prefix else [row.key]
            if dry:
                for key in keys:
                    logger.info("dry run: would delete %s:%s", row.storage_alias, key)
                stats.would_delete += len(keys)
                return
            urls = []
            for key in keys:
                storage.delete(key)
                stats.deleted_files += 1
                logger.info("deleted %s:%s (%s %s)", row.storage_alias, key, row.model_label, row.object_pk)
                if config.cdn is not None:
                    urls.append(_url_for(storage, key, config))
            row.status = StorageDeletion.Status.PURGE
            row.purge_urls = urls
            row.save(update_fields=["status", "purge_urls", "updated_at"])

        if dry:
            return

        if row.purge_urls:
            if purger is None:
                stats.purge_skipped += len(row.purge_urls)
                logger.warning("no CDN credentials: %d URLs not purged for %s", len(row.purge_urls), row.key)
            else:
                stats.purged_urls += purger.purge(row.purge_urls)

        row.status = StorageDeletion.Status.DONE
        row.purge_urls = []
        row.last_error = ""
        row.save(update_fields=["status", "purge_urls", "last_error", "updated_at"])
    except Exception as exc:  # noqa: BLE001 - one bad row must not stop the run
        _retry(row, exc, config, stats, now)


def _retry(row: Any, exc: Exception, config: Any, stats: DrainStats, now: Any) -> None:
    from ..models import StorageDeletion

    row.attempts += 1
    row.last_error = f"{type(exc).__name__}: {exc}"[:2000]
    if row.attempts >= config.max_attempts:
        row.status = StorageDeletion.Status.FAILED
        stats.failed += 1
        logger.error("giving up on %s:%s after %d attempts: %s", row.storage_alias, row.key, row.attempts, exc)
    else:
        delay = min(timedelta(seconds=config.backoff_seconds * 2 ** (row.attempts - 1)), MAX_BACKOFF)
        row.next_attempt_at = now + delay * random.uniform(0.8, 1.2)
        stats.retried += 1
        logger.warning("will retry %s:%s in %s: %s", row.storage_alias, row.key, delay, exc)
    row.save(update_fields=["status", "attempts", "last_error", "next_attempt_at", "purge_urls", "updated_at"])


def _url_for(storage: Any, key: str, config: Any) -> str:
    """The public URL the CDN serves `key` under."""
    try:
        url = storage.url(key)
    except Exception:
        url = ""
    if url.startswith(("http://", "https://")):
        return url
    base = (config.cdn.base_url if config.cdn else None) or (f"https://{config.backend_domain}" if config.backend_domain else "")
    return f"{base.rstrip('/')}/{key}" if base else key
