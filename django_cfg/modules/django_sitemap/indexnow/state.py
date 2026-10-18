"""The diff state: what each host last had accepted.

Written only after an accepted batch, so whatever was refused or never sent
is found again by the next run.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:
    from ..models import IndexNowHost


@dataclass
class Diff:
    changed: dict[str, str] = field(default_factory=dict)  # new, or lastmod moved
    removed: list[str] = field(default_factory=list)
    new: int = 0

    def pending(self) -> list[str]:
        return list(self.changed) + self.removed

    def counts(self) -> dict[str, int]:
        return {"new": self.new, "changed": len(self.changed) - self.new, "removed": len(self.removed)}


def diff(host: "IndexNowHost", served: dict[str, str]) -> Diff:
    known = dict(host.urls.values_list("url", "lastmod"))
    d = Diff()
    for url, lastmod in served.items():
        if url not in known:
            d.changed[url] = lastmod
            d.new += 1
        elif lastmod and known[url] != lastmod:
            d.changed[url] = lastmod
    d.removed = [u for u in known if u not in served]
    return d


def seed(host: "IndexNowHost", served: dict[str, str]) -> None:
    """Record every URL as already known, without sending it."""
    from ..models import IndexNowUrl, url_digest

    with transaction.atomic():
        host.urls.all().delete()
        IndexNowUrl.objects.bulk_create(
            [IndexNowUrl(host=host, url=u, digest=url_digest(u), lastmod=m) for u, m in served.items()],
            batch_size=2_000,
        )
        host.seeded_at = timezone.now()
        host.save(update_fields=["seeded_at"])


def commit(host: "IndexNowHost", sent: list[str], d: Diff) -> None:
    """Record an accepted batch: changed URLs upserted, removed ones forgotten."""
    from ..models import IndexNowUrl, url_digest

    now = timezone.now()
    changed = {url_digest(u): u for u in sent if u in d.changed}
    removed = [url_digest(u) for u in sent if u not in d.changed]
    with transaction.atomic():
        if removed:
            host.urls.filter(digest__in=removed).delete()
        existing = {row.digest: row for row in host.urls.filter(digest__in=list(changed))}
        updates, creates = [], []
        for digest, url in changed.items():
            row = existing.get(digest)
            if row:
                row.lastmod, row.submitted_at = d.changed[url], now
                updates.append(row)
            else:
                creates.append(IndexNowUrl(host=host, url=url, digest=digest, lastmod=d.changed[url], submitted_at=now))
        IndexNowUrl.objects.bulk_update(updates, ["lastmod", "submitted_at"], batch_size=2_000)
        IndexNowUrl.objects.bulk_create(creates, batch_size=2_000)


def reseed(host: str | None = None) -> int:
    """Forget the diff state, so the next run records and sends nothing.

    For a real mass withdrawal the shrink guard refused, or a URL scheme
    change. Returns the number of hosts reset.
    """
    from ..models import IndexNowHost

    rows = IndexNowHost.objects.all() if host is None else IndexNowHost.objects.filter(host=host.lower())
    count = 0
    for row in rows:
        with transaction.atomic():
            row.urls.all().delete()
            row.seeded_at = None
            row.save(update_fields=["seeded_at"])
        count += 1
    return count
