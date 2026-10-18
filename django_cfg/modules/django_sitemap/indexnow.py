"""IndexNow — push changed URLs to Bing, Yandex, Seznam, Naver and others.

Configured by `IndexNowConfig` on `DjangoConfig.indexnow`; without it every
function here is inert. Google does not take part: the sitemap is its channel.

What gets sent:

- every row of a registered sitemap source whose `lastmod_field` is inside the
  window — the same queryset, URL template and fields the sitemap feed uses, so
  IndexNow never announces a URL the sitemap would not list;
- whatever `IndexNowConfig.extra_urls` returns — pages the sitemap cannot see
  because they just left it (deleted, 410, redirected).

Two ways to call it:

- `submit(urls)` from request paths (publish, unpublish). Never raises: a
  search engine being down must not fail a save. The result says what happened.
- `submit_changed()` from the schedule or `manage.py indexnow_submit`. Raises
  on a refusal, so a failing job shows as failed instead of logging into a void.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Iterable
from urllib.parse import urlsplit

from django.utils import timezone
from django.utils.module_loading import import_string

from .registry import all_sources, get
from .sources import SitemapSource, resolve_field

if TYPE_CHECKING:
    from django_cfg.models.django.indexnow import IndexNowConfig, IndexNowSite

logger = logging.getLogger(__name__)

#: The protocol's cap per POST.
MAX_URLS_PER_REQUEST = 10_000

#: Statuses the protocol defines as "received". Anything else is a refusal.
ACCEPTED = (200, 202)

#: What a refusal means, for the log line a person reads at 3 a.m.
REFUSALS = {
    400: "bad request: malformed payload",
    403: "key not valid: the key file is not served at keyLocation, or does not hold the key",
    422: "URLs do not belong to the host, or the key does not match the host",
    429: "too many requests: back off",
}


class IndexNowError(RuntimeError):
    """A batch was refused. Raised only by `submit_changed` / `submit(..., raise_errors=True)`."""


@dataclass
class SubmitResult:
    sent: int = 0
    accepted: int = 0
    statuses: list[int] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def get_config() -> "IndexNowConfig | None":
    """The active `IndexNowConfig`, or None when absent or disabled."""
    from django_cfg.core.state import get_current_config

    cfg = get_current_config()
    ix = getattr(cfg, "indexnow", None) if cfg else None
    return ix if ix and ix.enabled else None


def absolute_url(path: str, site: "IndexNowSite") -> str:
    """A sitemap path (`/catalog/kia/`) on the site's host, in its canonical form."""
    if path.startswith(("http://", "https://")):
        return path
    if site.trailing_slash and not path.endswith("/") and "?" not in path:
        path += "/"
    return f"https://{site.host}{path}"


def _sources(site: "IndexNowSite") -> list[SitemapSource]:
    if site.sources is not None and site.source_suffix is None:
        chosen = [s for s in (get(n) for n in site.sources) if s is not None and s.enabled]
    else:
        chosen = [s for s in all_sources() if site.takes(s.name)]
    return [s for s in chosen if s.lastmod_field]


def changed_paths(source: SitemapSource, since: datetime) -> Iterable[str]:
    """Paths of the source's rows whose lastmod is at or after `since`.

    `lastmod_field` may be an annotation (a sitemap's honest change date is
    often computed), so it is filtered as written; a dotted path becomes an
    ORM lookup.
    """
    lookup = (source.lastmod_field or "").replace(".", "__")
    for row in source.queryset_factory().filter(**{f"{lookup}__gte": since}).iterator(chunk_size=2_000):
        kwargs = {alias: resolve_field(row, path) for alias, path in source.fields.items()}
        yield source.url_template.format(**kwargs)


def changed_urls(since: datetime, config: "IndexNowConfig | None" = None) -> list[str]:
    """Every absolute URL that changed since `since`, across every site.

    Each site's sources first, then `extra_urls`. A path from `extra_urls` is
    joined to the host only when there is one site; with several, it must be
    an absolute URL, or which host it belongs to is a guess.
    """
    config = config or get_config()
    if config is None:
        return []

    sites = config.resolved_sites()
    urls: list[str] = []
    seen: set[str] = set()

    def add(url: str) -> None:
        if url not in seen:
            seen.add(url)
            urls.append(url)

    for site in sites:
        for source in _sources(site):
            for path in changed_paths(source, since):
                add(absolute_url(path, site))
    if config.extra_urls:
        for url in import_string(config.extra_urls)(since):
            if url.startswith(("http://", "https://")):
                add(url)
            elif len(sites) == 1:
                add(absolute_url(url, sites[0]))
            else:
                logger.warning("indexnow: extra_urls returned a bare path %r with several sites; skipped", url)
    return urls


def _by_host(urls: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for url in urls:
        groups.setdefault((urlsplit(url).hostname or "").lower(), []).append(url)
    return groups


def submit(
    urls: Iterable[str],
    *,
    config: "IndexNowConfig | None" = None,
    raise_errors: bool = False,
    client=None,
) -> SubmitResult:
    """POST the URLs in protocol-sized batches. No-op without a config."""
    config = config or get_config()
    result = SubmitResult()
    urls = list(dict.fromkeys(urls))
    if config is None or not urls:
        return result

    import httpx

    sites = {site.host: site for site in config.resolved_sites()}
    own = client is None
    client = client or httpx.Client(timeout=config.timeout)
    try:
        # One request per host: the protocol refuses a batch that mixes them.
        for host, host_urls in _by_host(urls).items():
            site = sites.get(host)
            if site is None:
                message = f"{len(host_urls)} URL(s) on {host or '(no host)'}, which is not a configured site"
                result.errors.append(message)
                logger.warning("indexnow: %s", message)
                continue
            key_location = config.key_location_for(site)
            for i in range(0, len(host_urls), MAX_URLS_PER_REQUEST):
                batch = host_urls[i : i + MAX_URLS_PER_REQUEST]
                result.sent += len(batch)
                try:
                    res = client.post(config.endpoint, json={
                        "host": host,
                        "key": config.key,
                        "keyLocation": key_location,
                        "urlList": batch,
                    })
                except httpx.HTTPError as exc:
                    # `str()` of an httpx error is often empty; name the type.
                    message = f"{host}: {type(exc).__name__}: {exc!s}" if str(exc) else f"{host}: {type(exc).__name__}"
                    result.errors.append(message)
                    logger.warning("indexnow: batch of %d not sent: %s", len(batch), message)
                    continue
                result.statuses.append(res.status_code)
                if res.status_code in ACCEPTED:
                    result.accepted += len(batch)
                    continue
                reason = REFUSALS.get(res.status_code, "unexpected status")
                message = f"{host}: HTTP {res.status_code} ({reason}): {res.text[:200]}"
                result.errors.append(message)
                logger.warning(
                    "indexnow: batch of %d refused: %s", len(batch), message,
                    extra={"host": host, "key_location": key_location},
                )
    finally:
        if own:
            client.close()

    if raise_errors and result.errors:
        raise IndexNowError(f"{len(result.errors)} batch(es) failed: {result.errors[0]}")
    return result


def submit_changed(hours: int | None = None, *, dry_run: bool = False) -> dict:
    """The scheduled job: submit everything that changed in the window."""
    config = get_config()
    if config is None:
        return {"enabled": False}

    since = timezone.now() - timedelta(hours=hours or config.window_hours)
    urls = changed_urls(since, config)
    summary = {
        "enabled": True,
        "since": since.isoformat(),
        "urls": len(urls),
        "by_host": {host: len(u) for host, u in _by_host(urls).items()},
    }
    if dry_run:
        summary["sample"] = urls[:5]
        return summary

    result = submit(urls, config=config, raise_errors=True)
    summary.update(accepted=result.accepted, statuses=result.statuses)
    logger.info("indexnow: %s", summary)
    return summary
