"""
django_cf.users.tasks — RQ tasks for user sync.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class _Delayable:
    """Callable with .delay() — enqueues via RQ if available, else runs in daemon thread."""

    def __init__(self, fn) -> None:
        self._fn = fn
        self.__name__ = fn.__name__
        self.__doc__ = fn.__doc__

    def __call__(self, *args, **kwargs):
        return self._fn(*args, **kwargs)

    def delay(self, *args, **kwargs) -> None:
        try:
            import django_rq
            django_rq.get_queue("default").enqueue(self._fn, *args, **kwargs)
        except Exception as exc:
            # RQ unavailable — run in a daemon thread so the HTTP request is not blocked.
            # D1 sync is non-critical: if the thread dies the next save will retry.
            import threading
            logger.debug("django_cf: RQ unavailable (%s) — falling back to thread", exc)
            threading.Thread(
                target=self._fn, args=args, kwargs=kwargs, daemon=True
            ).start()


def _push_user_task(user_id: str) -> None:
    """Upsert a single user to D1. Enqueued by post_save signal."""
    from django.contrib.auth import get_user_model
    from django_cfg.modules.django_cf.users.service import UserSyncService

    User = get_user_model()
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        logger.warning("django_cf.users: user pk=%s not found", user_id)
        return

    result = UserSyncService().push_user(user)
    logger.info("django_cf.users: synced pk=%s (changes=%d)", user_id, result.changes)


def _full_sync_task() -> None:
    """Nightly bulk-upsert all users to D1."""
    from django_cfg.modules.django_cf.users.service import UserSyncService

    stats = UserSyncService().full_sync_users()
    logger.info("django_cf.users: full_sync — %s", stats)


push_user_task = _Delayable(_push_user_task)
full_sync_task = _Delayable(_full_sync_task)

__all__ = ["push_user_task", "full_sync_task"]
