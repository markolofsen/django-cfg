"""Sitemap HTTP views — index + feed.

Plain Django views returning JSON. Not on the OpenAPI surface: this is a
server-only contract consumed by Next.js `app/sitemap.ts` at build/ISR
time, never by browsers. Schema lives in
`@plans/plan13-sitemap/01-architecture.md`.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_control

from .. import cache as sitemap_cache
from .. import registry
from ..config import get_sitemap_config
from ..cursors import CursorError, decode_cursor, encode_cursor
from ..pagination import keyset_page
from ..sources import SitemapSource, resolve_field

logger = logging.getLogger(__name__)


def _json(payload: dict[str, Any], status: int = 200, ttl: int | None = None) -> HttpResponse:
    response = JsonResponse(payload, status=status, json_dumps_params={"default": _json_default})
    if ttl is not None and status == 200:
        response["Cache-Control"] = (
            f"public, s-maxage={ttl}, stale-while-revalidate={ttl * 24}"
        )
    return response


def _json_default(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    raise TypeError(f"not JSON serialisable: {type(value).__name__}")


@method_decorator(
    cache_control(public=True, s_maxage=300, stale_while_revalidate=86400),
    name="dispatch",
)
class SitemapIndexView(View):
    """`GET /cfg/sitemap/index/` — chunk catalog across all sources."""

    def get(self, request: HttpRequest) -> HttpResponse:
        cfg = get_sitemap_config()
        key = sitemap_cache.index_key()
        cached = sitemap_cache.cache_get(key)
        if cached is not None:
            return _json(cached, ttl=cfg.cache_index_seconds)

        payload = _build_index(cfg.cache_index_seconds)
        sitemap_cache.cache_set(key, payload, cfg.cache_index_seconds)
        return _json(payload, ttl=cfg.cache_index_seconds)


@method_decorator(
    cache_control(public=True, s_maxage=3600, stale_while_revalidate=86400),
    name="dispatch",
)
class SitemapFeedView(View):
    """`GET /cfg/sitemap/feed/?source=...&cursor=...` — one chunk of entries."""

    def get(self, request: HttpRequest) -> HttpResponse:
        cfg = get_sitemap_config()
        source_name = request.GET.get("source") or ""
        cursor_token = request.GET.get("cursor") or None

        if not source_name:
            return _json({"detail": "source is required"}, status=400)

        source = registry.get(source_name)
        if source is None or not source.enabled:
            return _json({"detail": "unknown source"}, status=404)

        try:
            cursor = decode_cursor(cursor_token) if cursor_token else None
        except CursorError as exc:
            return _json({"detail": str(exc)}, status=400)

        cache_key = sitemap_cache.feed_key(source_name, cursor_token)
        cached = sitemap_cache.cache_get(cache_key)
        if cached is not None:
            return _json(cached, ttl=cfg.cache_feed_seconds)

        payload = _build_feed(source, cursor, cursor_token)
        sitemap_cache.cache_set(cache_key, payload, cfg.cache_feed_seconds)
        return _json(payload, ttl=cfg.cache_feed_seconds)


# ── builders ────────────────────────────────────────────────────────────


def _build_index(ttl_seconds: int) -> dict[str, Any]:
    sources_payload: list[dict[str, Any]] = []
    for source in registry.all_sources():
        chunks, total = _walk_chunks(source)
        sources_payload.append(
            {
                "name": source.name,
                "chunks": chunks,
                "total_estimate": total,
            }
        )
    return {
        "sources": sources_payload,
        "generated_at": datetime.now(tz=timezone.utc),
        "ttl_seconds": ttl_seconds,
    }


def _walk_chunks(source: SitemapSource) -> tuple[list[dict[str, Any]], int]:
    """Stream cursor values, snapshotting one cursor per chunk boundary."""
    qs = source.queryset_factory()
    order_args = _order_args(source)
    cursor_fields_orm = list(source.cursor_fields)

    chunks: list[dict[str, Any]] = []
    total = 0
    page_size = source.page_size
    last_in_chunk: tuple[Any, ...] | None = None

    rows = qs.order_by(*order_args).values_list(*cursor_fields_orm).iterator(
        chunk_size=10_000,
    )
    for idx, row in enumerate(rows, start=1):
        total += 1
        last_in_chunk = row
        if idx % page_size == 0:
            chunks.append(
                {
                    "id": f"{source.name}-{len(chunks) + 1}",
                    "cursor_to": encode_cursor(row),
                    "count_estimate": page_size,
                }
            )

    remainder = total - len(chunks) * page_size
    if remainder > 0 and last_in_chunk is not None:
        chunks.append(
            {
                "id": f"{source.name}-{len(chunks) + 1}",
                "cursor_to": None,
                "count_estimate": remainder,
            }
        )

    return chunks, total


def _build_feed(
    source: SitemapSource,
    cursor: tuple[Any, ...] | None,
    cursor_token: str | None,
) -> dict[str, Any]:
    qs = source.queryset_factory()
    rows, next_cursor = keyset_page(qs, source, cursor)

    entries: list[dict[str, Any]] = []
    for row in rows:
        url_kwargs = {alias: resolve_field(row, path) for alias, path in source.fields.items()}
        loc = source.url_template.format(**url_kwargs)
        lastmod = (
            resolve_field(row, source.lastmod_field) if source.lastmod_field else None
        )
        entries.append({"loc": loc, "lastmod": lastmod})

    chunk_id = _derive_chunk_id(source.name, cursor_token)
    return {
        "source": source.name,
        "chunk_id": chunk_id,
        "count": len(entries),
        "has_more": next_cursor is not None,
        "next_cursor": encode_cursor(next_cursor) if next_cursor else None,
        "entries": entries,
    }


def _order_args(source: SitemapSource) -> list[str]:
    return [c.strip() for c in source.order.split(",") if c.strip()]


def _derive_chunk_id(source: str, cursor_token: str | None) -> str:
    if cursor_token is None:
        return f"{source}-1"
    return f"{source}@{cursor_token[:12]}"
