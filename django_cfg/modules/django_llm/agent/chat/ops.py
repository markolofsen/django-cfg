"""Operator jobs over a host's chat tables: close dead answers, drop idle sessions. The commands `chat_reap` and `chat_prune` call these.

Counts only: nothing here reads, prints or logs a title or a message (they are the user's text).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from django.apps import apps
from django.db.models import Max
from django.db.models.functions import Coalesce
from django.utils import timezone

from django_cfg.modules.django_llm.agent.chat.models import AbstractThread
from django_cfg.modules.django_llm.agent.chat.service import ChatPolicy, ChatService

REAP_AFTER_S = 120.0  # keep above every kind's `limits.timeout_s`
PRUNE_AFTER_DAYS = 180


class ThreadModelError(LookupError):
    pass


def thread_model(label: str | None = None):
    """The host's concrete thread model: `app_label.Model`, or the only subclass of `AbstractThread` installed."""
    if label:
        try:
            model = apps.get_model(label)
        except (LookupError, ValueError) as err:
            raise ThreadModelError(f"no model {label!r}") from err
        if not issubclass(model, AbstractThread):
            raise ThreadModelError(f"{label} is not a subclass of AbstractThread")
        return model
    found = [m for m in apps.get_models() if issubclass(m, AbstractThread)]
    if len(found) == 1:
        return found[0]
    names = ", ".join(m._meta.label for m in found) or "none installed"
    raise ThreadModelError(f"say which thread model to use with --model (found: {names})")


def reap(model, *, older_than_s: float = REAP_AFTER_S, now: datetime | None = None) -> int:
    """Close every assistant answer left `running` for longer than `older_than_s` as `error` / `failed`."""
    return ChatService(model, ChatPolicy(stale_run_seconds=older_than_s)).reap_stale(now)


@dataclass(frozen=True)
class Pruned:
    threads: int
    messages: int


def prune(model, *, days: int = PRUNE_AFTER_DAYS, kind: str | None = None, dry_run: bool = False, batch: int = 500, now: datetime | None = None) -> Pruned:
    """Delete threads (their messages cascade) whose last activity is older than `days`. Activity is the newest message, or the
    thread's creation when it has none. `dry_run` counts and deletes nothing."""
    if days < 1:
        raise ValueError("days must be at least 1")
    cutoff = (now or timezone.now()) - timedelta(days=days)
    message_model = model.messages.rel.related_model
    idle = model.objects.annotate(last_activity=Coalesce(Max("messages__created_at"), "created_at")).filter(last_activity__lt=cutoff)
    if kind:
        idle = idle.filter(kind=kind)
    if dry_run:
        pks = list(idle.values_list("pk", flat=True))
        return Pruned(len(pks), message_model.objects.filter(thread_id__in=pks).count())
    threads = messages = 0
    while True:
        pks = list(idle.values_list("pk", flat=True)[:batch])
        if not pks:
            return Pruned(threads, messages)
        _, per_model = model.objects.filter(pk__in=pks).delete()
        threads += per_model.get(model._meta.label, 0)
        messages += per_model.get(message_model._meta.label, 0)
