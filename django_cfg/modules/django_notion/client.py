"""The Notion client and the data source cache. Tests replace the client with ``set_client_factory``."""

from __future__ import annotations

import logging
from typing import Any, Callable, Dict, Optional

from . import conf
from .__cfg__ import NOTION_API_VERSION, NotionTarget
from .exceptions import NotionConfigError

_factory: Optional[Callable[[], Any]] = None
_data_sources: Dict[str, str] = {}


def set_client_factory(factory: Optional[Callable[[], Any]]) -> None:
    """Replace how the client is built (tests). ``None`` restores the real one. Clears the data source cache."""
    global _factory
    _factory = factory
    _data_sources.clear()


def get_client(target: Optional[NotionTarget] = None):
    if _factory is not None:
        return _factory()
    from notion_client import Client

    cfg = conf.get_notion_config()
    token = (target.token if target is not None and target.token is not None else cfg.token)
    if token is None:
        raise NotionConfigError("no Notion token: set NOTION__TOKEN or NotionTarget.token")
    # retry=False: 429/5xx are handled by the outbox (Retry-After -> next_attempt_at), not by sleeping in a worker.
    return Client(
        auth=token.get_secret_value(),
        notion_version=NOTION_API_VERSION,
        retry=False,
        timeout_ms=int(cfg.timeout_seconds * 1000),
        log_level=logging.ERROR,
    )


def resolve_data_source(client, target: NotionTarget) -> str:
    """The id pages are created under (API 2025-09-03 creates pages under a data source, not a database).

    ``data_source_id`` is used as given. A ``database_id`` is resolved once through ``databases.retrieve`` (needs Read
    content) and cached.
    """
    if target.data_source_id:
        return target.data_source_id
    db_id = target.database_id or ""
    cached = _data_sources.get(db_id)
    if cached:
        return cached
    db = client.databases.retrieve(db_id)
    sources = db.get("data_sources") or []
    if len(sources) != 1:
        raise NotionConfigError(
            f"database {db_id} has {len(sources)} data sources; set NotionTarget.data_source_id to choose one"
        )
    _data_sources[db_id] = sources[0]["id"]
    return sources[0]["id"]
