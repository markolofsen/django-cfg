"""LLM chat titles (D4): the first exchange is summarised by a cheap model, in the thread's language, off the request.

The thread shows `ChatKind.title_of(first message)` from the first send. After the first answer is stored, `ChatService` starts a
title job (`spawn`, or the host's own `title_job`, e.g. an RQ enqueue of `title_thread`). The job sends **the first exchange only**
(the first user message and the first answer, each cut to 600 characters) to the `ChatPolicy.title_models` chain, and replaces the
fallback title only if the thread still carries it (a renamed thread is left alone). Any failure keeps the fallback. Nothing here
logs text.
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Any

from django_cfg.modules.django_llm.agent.chat import kind as kinds
from django_cfg.modules.django_llm.agent.chat.turn import Role, Status

log = logging.getLogger(__name__)

EXCERPT_CHARS = 600
MAX_TITLE_CHARS = 60
INSTRUCTIONS = (
    "Write a short title (at most 6 words) for the conversation below. "
    "Write it in the language of the user's message. Reply with the title only: no quotes, no trailing period, no preamble."
)


def clean_title(raw: str) -> str:
    """One line, whitespace collapsed, quotes and a trailing period stripped, cut at a word to MAX_TITLE_CHARS."""
    lines = [ln for ln in (raw or "").strip().splitlines() if ln.strip()]
    text = " ".join(lines[0].split()).strip(" \t\"'`«»“”„").rstrip(".。") if lines else ""
    if len(text) > MAX_TITLE_CHARS:
        text = text[:MAX_TITLE_CHARS].rsplit(" ", 1)[0].rstrip(" ,;:-") or text[:MAX_TITLE_CHARS]
    return text


def title_prompt(user_text: str, answer_text: str) -> str:
    return f"User message:\n{user_text[:EXCERPT_CHARS]}\n\nAssistant answer:\n{answer_text[:EXCERPT_CHARS]}"


def write_title(thread_model: Any, thread_id: Any, title: str, *, fallback: str) -> bool:
    """Set the title if the thread still carries the fallback (no `updated_at` bump: the list order does not move)."""
    title = clean_title(title)
    if not title:
        return False
    return thread_model.objects.filter(pk=thread_id, title=fallback).update(title=title) > 0


def title_thread(thread_model: Any, thread_id: Any, models: tuple[str, ...], *, model: Any = None) -> bool:
    """The job body (sync; safe to enqueue). `model` replaces the chain (tests). Returns whether a title was written."""
    from pydantic_ai import Agent

    from django_cfg.modules.django_llm.agent.chat.runner import build_model

    thread = thread_model.objects.filter(pk=thread_id).first()
    if thread is None:
        return False
    rows = thread.messages.order_by("seq")
    user = rows.filter(role=Role.USER).first()
    answer = rows.filter(role=Role.ASSISTANT, status=Status.DONE).first()
    if user is None or answer is None:
        return False
    try:
        fallback = kinds.get(thread.kind).title_of(user.text)[:200]
    except kinds.UnknownKind:
        return False
    if thread.title != fallback:
        return False
    try:
        agent = Agent(model or build_model(models), instructions=INSTRUCTIONS, model_settings={"max_tokens": 40})
        result = agent.run_sync(title_prompt(user.text, answer.text))
        return write_title(thread_model, thread_id, result.output, fallback=fallback)
    except Exception as err:  # noqa: BLE001 - the fallback title stays; the log names the error class, never the text
        log.warning("chat: LLM title failed for thread %s (%s); fallback kept", thread_id, type(err).__name__)
        return False


def spawn(thread_model: Any, thread_id: Any, models: tuple[str, ...], *, run: Callable[..., bool] = title_thread) -> threading.Thread:
    """Default job runner: a daemon thread that closes its own DB connection when done."""

    def work() -> None:
        from django.db import connection

        try:
            run(thread_model, thread_id, models)
        finally:
            connection.close()

    t = threading.Thread(target=work, name="chat-title", daemon=True)
    t.start()
    return t
