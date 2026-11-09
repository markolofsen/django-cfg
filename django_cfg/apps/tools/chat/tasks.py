"""RQ tasks the schedules of `ChatConfig` run: thin wrappers over `chat_reap` / `chat_prune` (`agent.chat.ops`). Counts only."""

from __future__ import annotations

from typing import Any

from django_cfg.modules.django_llm.agent.chat import ops

MODEL = "cfg_chat.Thread"


def reap(older_than_s: float = ops.REAP_AFTER_S) -> int:
    """Close stuck answers and delete uploads nobody sent past their TTL. Returns the answers closed; counts only."""
    model = ops.thread_model(MODEL)
    ops.reap_attachments(model)
    return ops.reap(model, older_than_s=older_than_s)


def prune(days: int = ops.PRUNE_AFTER_DAYS, kind: str | None = None) -> dict[str, Any]:
    result = ops.prune(ops.thread_model(MODEL), days=days, kind=kind)
    return {"threads": result.threads, "messages": result.messages}


def vectorise(limit: int = 200) -> dict[str, Any]:
    """Embed the chunks of threads with new messages (one batched call). Does nothing while `ChatConfig.vectors` is off. Counts only."""
    from django_cfg.apps.tools.chat.vectors import sync

    return sync(limit=limit)
