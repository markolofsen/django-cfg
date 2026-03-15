"""
django_cf.users.service — UserSyncService.

Handles pushing Django users and project metadata to Cloudflare D1.
Inherits BaseD1Service for client/api_url/schema plumbing.
"""

from __future__ import annotations

import logging
from typing import Any

from django_cfg.modules.django_cf.core.d1_query import D1Q
from django_cfg.modules.django_cf.core.service import BaseD1Service
from django_cfg.core.state.registry import get_current_config

from .schema import USERS_SCHEMA_STATEMENTS, PROJECTS_TABLE, USERS_TABLE
from .types import ProjectSyncData, UserSyncData

logger = logging.getLogger(__name__)


class UserSyncService(BaseD1Service):
    """Syncs Django users + project metadata to Cloudflare D1."""

    def _get_schema_statements(self) -> list[str]:
        return USERS_SCHEMA_STATEMENTS

    # ── Internal ──────────────────────────────────────────────────────────────

    def _upsert_project(self) -> None:
        """Upsert project row from current DjangoConfig — called before any user write."""
        config = get_current_config()
        if config is None:
            return
        project = ProjectSyncData.from_django_config(config)
        sql, params = D1Q.upsert(PROJECTS_TABLE, project)
        self._get_client().execute(sql, params)
        logger.debug("django_cf: upserted project '%s'", project.project_name)

    # ── Public ────────────────────────────────────────────────────────────────

    def push_user(self, user: Any):
        """Upsert a single user into D1 under the current project's api_url."""
        self._ensure_schema()
        self._upsert_project()
        api_url = self._get_api_url()
        data = UserSyncData.from_user(user, api_url=api_url)
        sql, params = D1Q.upsert(USERS_TABLE, data)
        result = self._get_client().execute(sql, params)
        logger.debug(
            "django_cf: upserted user %s @ %s (changes=%d, %.1fms)",
            data.email, api_url, result.changes, result.duration_ms,
        )
        return result

    def full_sync_users(self) -> dict[str, int]:
        """Bulk-upsert all users from Django ORM to D1. Returns {"synced": N, "failed": M}."""
        from django.contrib.auth import get_user_model

        self._ensure_schema()
        self._upsert_project()
        api_url = self._get_api_url()
        client = self._get_client()

        batch_size = 500
        try:
            from django_cfg.core.state.registry import get_current_config as _gcc
            _cfg = _gcc()
            if _cfg and hasattr(_cfg, "cloudflare") and _cfg.cloudflare:
                batch_size = _cfg.cloudflare.sync_batch_size
        except Exception:
            pass

        User = get_user_model()
        synced = failed = 0
        batch: list[tuple[str, list[str]]] = []

        for user in User.objects.all().order_by("pk").iterator(chunk_size=batch_size):
            try:
                data = UserSyncData.from_user(user, api_url=api_url)
                batch.append(D1Q.upsert(USERS_TABLE, data))
            except Exception as exc:
                logger.warning("django_cf: skipping user pk=%s — %s", user.pk, exc)
                failed += 1
                continue

            if len(batch) >= batch_size:
                ok = self._flush_batch(client, batch)
                synced += ok
                failed += len(batch) - ok
                batch = []

        if batch:
            ok = self._flush_batch(client, batch)
            synced += ok
            failed += len(batch) - ok

        logger.info("django_cf: full_sync @ %s — synced=%d, failed=%d", api_url, synced, failed)
        return {"synced": synced, "failed": failed}

    def _flush_batch(self, client: Any, batch: list[tuple[str, list[str]]]) -> int:
        ok = 0
        for sql, params in batch:
            try:
                client.execute(sql, params)
                ok += 1
            except Exception as exc:
                logger.warning("django_cf: batch upsert failed — %s", exc)
        return ok


__all__ = ["UserSyncService"]
