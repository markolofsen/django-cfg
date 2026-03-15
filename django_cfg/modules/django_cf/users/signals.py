"""
django_cf.users.signals — post_save hook for CustomUser → D1 sync.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def connect_signals() -> None:
    """Wire up post_save on CustomUser. Idempotent — Django deduplicates by dispatch_uid."""
    from django.contrib.auth import get_user_model
    from django.db.models.signals import post_save

    User = get_user_model()
    post_save.connect(
        _on_user_save,
        sender=User,
        dispatch_uid="django_cf.users.sync_user_to_d1",
        weak=False,
    )
    logger.debug("django_cf.users: post_save signal connected for %s", User.__name__)


def _on_user_save(sender: type, instance: object, **kwargs: object) -> None:
    from django_cfg.modules.django_cf import is_ready
    if not is_ready():
        return
    try:
        from django_cfg.modules.django_cf.users.tasks import push_user_task
        push_user_task.delay(str(instance.pk))  # type: ignore[union-attr]
    except Exception as exc:
        logger.warning("django_cf.users: failed to enqueue push_user_task — %s", exc)


__all__ = ["connect_signals"]
