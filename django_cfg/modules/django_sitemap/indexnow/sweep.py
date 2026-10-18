"""One run per host, and the scheduled `submit_changed()`.

Guards, each against a degraded read being sent as fact:

- a source that raises aborts the host's run — a partial read would report the
  unread URLs as removed;
- an empty read aborts, for the same reason;
- more than `shrink_share` of known URLs gone at once is a degraded read, not a
  withdrawal: nothing is sent, and `reseed()` accepts a real one.
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from django.core.cache import cache
from django.utils import timezone
from django.utils.module_loading import import_string

from . import IndexNowError
from .state import commit, diff, seed
from .transport import batches, open_client, post
from .urls import absolute_url, host_of, site_urls

if TYPE_CHECKING:
    from django_cfg.models.django.indexnow import IndexNowConfig, IndexNowSite

logger = logging.getLogger(__name__)

#: One run at a time: an overlap would send the same diff twice.
LOCK_KEY = "django_cfg:indexnow:run"
LOCK_SECONDS = 3600


def extra_urls(config: "IndexNowConfig", site: "IndexNowSite", since: datetime | None) -> list[str]:
    """`extra_urls(since)` filtered to this site; nothing before the first full success."""
    if not config.extra_urls or since is None:
        return []
    single = len(config.resolved_sites()) == 1
    out = []
    for url in import_string(config.extra_urls)(since):
        if url.startswith(("http://", "https://")):
            if host_of(url) == site.host:
                out.append(url)
        elif single:
            out.append(absolute_url(url, site))
        else:
            logger.warning("indexnow: extra_urls returned a bare path %r with several sites; skipped", url)
    return out


def sweep_site(site: "IndexNowSite", *, config: "IndexNowConfig", dry_run: bool = False, client=None) -> dict:
    """One host, one run. Returns a summary; its `status` is also stored on the host."""
    from ..models import IndexNowHost

    host, _ = IndexNowHost.objects.get_or_create(host=site.host)
    started = timezone.now()
    summary = _run(host, site, config=config, dry_run=dry_run, client=client)
    if not dry_run:
        host.last_run_at = started
        host.last_status = summary["status"][:120]
        fields = ["last_run_at", "last_status"]
        if summary.get("complete"):
            host.last_success_at = started
            fields.append("last_success_at")
        host.save(update_fields=fields)
    logger.info("indexnow %s: %s", site.host, summary["status"])
    return summary


def _run(host, site, *, config, dry_run, client) -> dict:
    try:
        served = site_urls(site)
    except Exception as exc:
        logger.warning("indexnow %s: a source failed: %s", site.host, exc, exc_info=True)
        return {"status": f"source_error: {type(exc).__name__}"}
    if not served:
        return {"status": "empty"}

    if host.seeded_at is None:
        if not dry_run:
            seed(host, served)
        return {"status": f"seeded {len(served)}", "urls": len(served), "complete": True}

    d = diff(host, served)
    known = host.urls.count()
    if len(d.removed) > max(config.shrink_floor, config.shrink_share * known):
        logger.warning("indexnow %s: %d of %d URLs gone at once; treating the read as degraded",
                       site.host, len(d.removed), known)
        return {"status": f"shrunk {len(d.removed)} of {known}", **d.counts()}

    all_pending = d.pending()
    pending = all_pending[: config.max_urls_per_run]
    extra = [u for u in extra_urls(config, site, host.last_success_at) if u not in d.changed]
    counts = {**d.counts(), "extra": len(extra)}
    if not pending and not extra:
        return {"status": "no_change", **counts, "complete": True}
    if dry_run:
        return {"status": f"would_send {len(pending) + len(extra)}", **counts, "sample": (pending + extra)[:5]}

    client, owned = open_client(config, client)
    sent = 0
    try:
        for urls, diffed in ((pending, True), (extra, False)):
            for batch in batches(urls):
                status, error = post(client, config, site, batch)
                if error:
                    return {"status": f"http_{status or 'error'} after {sent}", "error": error, **counts}
                if diffed:
                    commit(host, batch, d)
                sent += len(batch)
    finally:
        if owned:
            client.close()

    left = len(all_pending) - len(pending)
    status = f"sent {sent}" + (f", {left} left for the next run" if left else "")
    return {"status": status, "sent": sent, **counts, "complete": True}


def submit_changed(*, dry_run: bool = False, host: str | None = None,
                   config: "IndexNowConfig | None" = None, client=None) -> dict:
    """The scheduled job: diff every site and submit what changed.

    Raises `IndexNowError` after every site has run if any was refused, so the
    job shows as failed.
    """
    from . import get_config

    config = config or get_config()
    if config is None:
        return {"enabled": False}
    sites = [s for s in config.resolved_sites() if host is None or s.host == host.lower()]
    if host and not sites:
        raise IndexNowError(f"{host} is not a configured site")

    if not dry_run and not cache.add(LOCK_KEY, "1", LOCK_SECONDS):
        logger.info("indexnow: another run holds the lock; skipped")
        return {"enabled": True, "skipped": "another run holds the lock"}
    try:
        by_host = {s.host: sweep_site(s, config=config, dry_run=dry_run, client=client) for s in sites}
    finally:
        if not dry_run:
            cache.delete(LOCK_KEY)

    logger.info("indexnow: %s", {h: r["status"] for h, r in by_host.items()})
    refused = [r["error"] for r in by_host.values() if r.get("error")]
    if refused:
        raise IndexNowError(f"{len(refused)} host(s) refused: {refused[0]}")
    return {"enabled": True, "by_host": by_host}
