"""What the sitemap sources produce for a site, as absolute URLs.

The feed's own queryset, template and fields, so nothing is announced that
the sitemap would not list.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Iterable
from urllib.parse import urlsplit

from ..registry import all_sources, get
from ..sources import SitemapSource, resolve_field

if TYPE_CHECKING:
    from django_cfg.models.django.indexnow import IndexNowSite


def absolute_url(path: str, site: "IndexNowSite") -> str:
    """A sitemap path (`/catalog/kia/`) on the site's host, in its canonical form."""
    if path.startswith(("http://", "https://")):
        return path
    if site.trailing_slash and not path.endswith("/") and "?" not in path:
        path += "/"
    return f"https://{site.host}{path}"


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def by_host(urls: Iterable[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for url in urls:
        groups.setdefault(host_of(url), []).append(url)
    return groups


def site_sources(site: "IndexNowSite") -> list[SitemapSource]:
    if site.sources is not None and site.source_suffix is None:
        return [s for s in (get(n) for n in site.sources) if s is not None and s.enabled]
    return [s for s in all_sources() if site.takes(s.name)]


def _lastmod_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def site_urls(site: "IndexNowSite") -> dict[str, str]:
    """`{absolute url: lastmod}` for every row of every source on the site.

    A source without a lastmod gives "" — its URLs are sent only when they
    appear or go. Raises if any source does: a caller must not diff a partial read.
    """
    out: dict[str, str] = {}
    for source in site_sources(site):
        for row in source.queryset_factory().iterator(chunk_size=2_000):
            kwargs = {alias: resolve_field(row, path) for alias, path in source.fields.items()}
            url = absolute_url(source.url_template.format(**kwargs), site)
            out[url] = _lastmod_text(resolve_field(row, source.lastmod_field)) if source.lastmod_field else ""
    return out
