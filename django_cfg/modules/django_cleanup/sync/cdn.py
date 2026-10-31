"""Cloudflare cache purge by URL, with the token and zone read from the environment."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING, Any, Iterable, List, Optional

if TYPE_CHECKING:
    from django_cfg.models.django.storage import CDNPurgeConfig

logger = logging.getLogger(__name__)

API = "https://api.cloudflare.com/client/v4/zones/{zone}/purge_cache"


class CDNPurgeError(Exception):
    """A purge request did not succeed; the caller keeps the URLs and retries."""


class CloudflarePurger:
    """Purges URLs in batches. `session` is injectable for tests."""

    def __init__(self, zone_id: str, token: str, batch_size: int = 30, timeout: int = 15, session: Any = None):
        self.zone_id = zone_id
        self.token = token
        self.batch_size = batch_size
        self.timeout = timeout
        if session is None:
            import requests

            session = requests.Session()
        self.session = session

    def purge(self, urls: Iterable[str]) -> int:
        """Purge every URL; raises `CDNPurgeError` on the first failed batch. Returns how many were sent."""
        pending: List[str] = list(urls)
        sent = 0
        for start in range(0, len(pending), self.batch_size):
            chunk = pending[start : start + self.batch_size]
            try:
                response = self.session.post(
                    API.format(zone=self.zone_id),
                    json={"files": chunk},
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=self.timeout,
                )
                body = response.json()
            except Exception as exc:
                raise CDNPurgeError(f"purge request failed: {exc}") from exc
            if response.status_code != 200 or not body.get("success"):
                errors = body.get("errors") if isinstance(body, dict) else None
                raise CDNPurgeError(f"Cloudflare answered {response.status_code}: {errors}")
            sent += len(chunk)
            logger.info("CDN purge: %d URLs", len(chunk))
        return sent


def get_purger(cdn: Optional["CDNPurgeConfig"]) -> Optional[CloudflarePurger]:
    """A purger, or `None` when no CDN is configured or the token or zone is missing."""
    if cdn is None:
        return None
    token = os.environ.get(cdn.api_token_env, "")
    zone = os.environ.get(cdn.zone_id_env, "")
    if not token or not zone:
        logger.warning("CDN purge skipped: %s or %s is not set", cdn.api_token_env, cdn.zone_id_env)
        return None
    return CloudflarePurger(zone, token, batch_size=cdn.batch_size, timeout=cdn.timeout)
