"""The chat housekeeping as RQ schedule entries: a host adds them with one line and writes no task module.

    from django_cfg.modules.django_llm.agent.chat.schedules import schedules

    RQConfig(schedules=[*schedules("chat.Thread", stale_after_s=150, prune_days=180, queue="default"), ...])

Import it from here, not from `ops`: settings are built before the app registry, and `ops` imports the models. This module
touches no model at import time; the task functions below resolve the thread model by its label when the worker runs them.
`ops.schedules` is the same function, for code that runs after Django is set up.

Counts only: a task returns numbers and never reads or logs a title or a message.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django_cfg.models.django.django_rq import RQScheduleConfig

REAP_EVERY_S = 60
ATTACHMENTS_EVERY_S = 3600
PRUNE_EVERY_S = 86400


def schedules(thread_model, *, stale_after_s: float, prune_days: int | None = None, queue: str = "default") -> list[RQScheduleConfig]:
    """The entries for one chat: reap dead answers, reap uploads (when the chat has an attachment table), prune idle sessions.

    `thread_model` is the model or its `app_label.Model` label. `stale_after_s` must stay above every kind's `limits.timeout_s`.
    `prune_days=None` keeps threads for ever (no prune entry). `queue` must be one a worker reads. Moving an entry to another
    `queue` or renaming it leaves the old one registered in Redis: cancel it by hand.
    """
    from django_cfg.models.django.django_rq import RQScheduleConfig

    if stale_after_s <= 0:
        raise ValueError("stale_after_s must be positive")
    if prune_days is not None and prune_days < 1:
        raise ValueError("prune_days must be at least 1")
    label = thread_model if isinstance(thread_model, str) else thread_model._meta.label
    if "." not in label:
        raise ValueError(f"thread_model must be an 'app_label.Model' label or a model, got {label!r}")
    here = __name__
    entries = [
        RQScheduleConfig(
            func=f"{here}.reap", interval=REAP_EVERY_S, queue=queue, timeout=60,
            kwargs={"model": label, "stale_after_s": float(stale_after_s)},
            description=f"chat {label}: close answers left running by a dead worker",
        )
    ]
    if _has_attachments(label):
        entries.append(
            RQScheduleConfig(
                func=f"{here}.reap_attachments", interval=ATTACHMENTS_EVERY_S, queue=queue, timeout=300,
                kwargs={"model": label},
                description=f"chat {label}: delete unsent uploads and the bytes of files past their retention",
            )
        )
    if prune_days is not None:
        entries.append(
            RQScheduleConfig(
                func=f"{here}.prune", interval=PRUNE_EVERY_S, queue=queue, timeout=900,
                kwargs={"model": label, "days": int(prune_days)},
                description=f"chat {label}: delete sessions idle for {prune_days} days",
            )
        )
    return entries


def _has_attachments(label: str) -> bool:
    """False only when Django is up and the chat has no attachment table. Before that (settings time) the entry is kept:
    the task is a no-op without a table, so the schedule never has to know."""
    from django.apps import apps

    if not apps.ready:
        return True
    from django_cfg.modules.django_llm.agent.chat import ops

    return ops.attachment_store(apps.get_model(label)) is not None


# --- what the worker runs ---------------------------------------------------


def reap(model: str, stale_after_s: float) -> dict:
    from django.apps import apps

    from django_cfg.modules.django_llm.agent.chat import ops

    return {"closed": ops.reap(apps.get_model(model), older_than_s=stale_after_s)}


def reap_attachments(model: str) -> dict:
    from django.apps import apps

    from django_cfg.modules.django_llm.agent.chat import ops

    return {"touched": ops.reap_attachments(apps.get_model(model))}


def prune(model: str, days: int) -> dict:
    from django.apps import apps

    from django_cfg.modules.django_llm.agent.chat import ops

    done = ops.prune(apps.get_model(model), days=days)
    return {"threads": done.threads, "messages": done.messages, "files": done.files}
