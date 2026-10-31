"""RQ entry points of the outbox worker. Scheduled through `StorageConfig.get_rq_schedules()`."""

from __future__ import annotations

import logging

logger = logging.getLogger("storage.outbox")


def drain_storage_outbox() -> dict:
    """One worker run. Returns its stats; never raises."""
    try:
        from .worker import drain

        return drain().as_dict()
    except Exception as exc:  # noqa: BLE001
        logger.exception("storage outbox run failed")
        return {"error": str(exc)}


def enqueue_drain() -> None:
    """Ask the queue for a run right after a commit; silent when django_rq is not there (the schedule still runs)."""
    try:
        import django_rq

        django_rq.get_queue("default").enqueue(drain_storage_outbox)
    except Exception:  # noqa: BLE001
        logger.debug("could not nudge the outbox worker", exc_info=True)
