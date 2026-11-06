"""Chunk, embed, store, search: the functions a host calls (or a scheduled job wraps). Nothing here is gated: the switch is the
caller's setting (`ChatConfig.vectors` in the ready app, the host's own flag elsewhere), so a host that never calls these pays nothing.

    sync_threads(ThreadChunk, threads, embed)        # new and grown chunks, one batched embedding call
    sync_pending(ThreadChunk, Thread, embed)         # the scheduled job and the backfill: threads with unindexed messages
    search(ThreadChunk, "как оформить возврат", embed, owner=user)

A chunk is written only when its text hash is new, so a run over unchanged threads costs no embedding. An embedder that returns `[]`
for a text (no key, mock) leaves that chunk unwritten and counted as `skipped`; the next run tries again.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from django.db.models import F, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce

from django_cfg.modules.django_llm.agent.chat.turn import Role, Status
from django_cfg.modules.django_llm.agent.chat.vectors import chunking, rank
from django_cfg.modules.django_llm.agent.chat.vectors.embedder import DEFAULT_MODEL, Embedder, embed_batched

SNIPPET_CHARS = 300


@dataclass
class SyncResult:
    threads: int = 0
    created: int = 0
    reembedded: int = 0
    unchanged: int = 0
    skipped: int = 0


@dataclass(frozen=True)
class Hit:
    thread_id: Any
    title: str
    kind: str
    first_seq: int
    last_seq: int
    score: float
    snippet: str


def _message_model(chunk_model):
    return chunk_model._meta.get_field("thread").related_model._meta.get_field("messages").related_model


def thread_lines(message_model, thread) -> list[chunking.Line]:
    rows = message_model.objects.filter(
        thread=thread, status=Status.DONE.value, role__in=[Role.USER.value, Role.ASSISTANT.value]
    ).order_by("seq").values_list("seq", "role", "text")
    return [chunking.Line(seq, role, text) for seq, role, text in rows]


def sync_threads(
    chunk_model,
    threads: Iterable,
    embed: Embedder,
    *,
    model: str = DEFAULT_MODEL,
    max_messages: int = chunking.MAX_MESSAGES,
    token_budget: int = chunking.TOKEN_BUDGET,
) -> SyncResult:
    """Bring the chunks of `threads` up to date. All texts that need a vector go to the embedder together."""
    message_model = _message_model(chunk_model)
    result = SyncResult()
    todo: list[tuple[Any, chunking.Span, Any]] = []  # (thread, span, existing row or None)
    for thread in threads:
        result.threads += 1
        spans = chunking.chunk_lines(thread_lines(message_model, thread), max_messages=max_messages, token_budget=token_budget)
        existing = {c.first_seq: c for c in chunk_model.objects.filter(thread=thread)}
        for span in spans:
            row = existing.get(span.first_seq)
            if row is not None and row.text_hash == span.text_hash and row.embedding:
                if row.closed != span.closed or row.last_seq != span.last_seq:  # same text implies the same span; belt and braces
                    chunk_model.objects.filter(pk=row.pk).update(closed=span.closed, last_seq=span.last_seq)
                result.unchanged += 1
            else:
                todo.append((thread, span, row))
    if not todo:
        return result
    vectors = embed_batched(embed, [span.text for _, span, _ in todo])
    for (thread, span, row), vector in zip(todo, vectors):
        if not vector:
            result.skipped += 1
            continue
        fields = dict(
            last_seq=span.last_seq, message_count=span.count, closed=span.closed, text_hash=span.text_hash, model=model, embedding=vector
        )
        if row is None:
            chunk_model.objects.create(thread=thread, first_seq=span.first_seq, **fields)
            result.created += 1
        else:
            for name, value in fields.items():
                setattr(row, name, value)
            row.save()
            result.reembedded += 1
    return result


def pending_threads(chunk_model, thread_model=None):
    """Threads with messages past their last chunk (never indexed, or the open tail grew)."""
    thread_model = thread_model or chunk_model._meta.get_field("thread").related_model
    covered = (
        chunk_model.objects.filter(thread=OuterRef("pk")).order_by("-last_seq").values("last_seq")[:1]
    )
    return thread_model.objects.annotate(indexed_seq=Coalesce(Subquery(covered, output_field=IntegerField()), 0)).filter(
        last_seq__gt=F("indexed_seq")
    )


def sync_pending(chunk_model, embed: Embedder, *, limit: int = 200, **options) -> SyncResult:
    """One run of the background job: the `limit` least recently touched threads that have unindexed messages. The backfill is the
    same call repeated until `threads == 0`. A thread whose messages have no text (only errors) is revisited and costs one query."""
    threads = list(pending_threads(chunk_model).order_by("updated_at")[:limit])
    return sync_threads(chunk_model, threads, embed, **options)


def search(
    chunk_model,
    query: str,
    embed: Embedder,
    *,
    owner=None,
    threads=None,
    kind: str | None = None,
    limit: int = 8,
    candidates: int = 3000,
    min_score: float = 0.0,
) -> list[Hit]:
    """Cross-thread search: the chunks nearest to `query`, among the threads of `owner` (or the queryset `threads`).

    The query is embedded as it was written, in any language; the cross-language match is the model's. Candidates are the newest
    `candidates` chunks of the scope, ranked in memory."""
    if not query.strip():
        return []
    vectors = embed([query.strip()])
    if not vectors or not vectors[0]:
        return []
    rows = chunk_model.objects.select_related("thread").exclude(embedding=[])
    if threads is not None:
        rows = rows.filter(thread__in=threads)
    elif owner is not None:
        rows = rows.filter(thread__owner=owner)
    else:
        raise ValueError("search needs an owner or a threads queryset: chunks are the user's text")
    if kind:
        rows = rows.filter(thread__kind=kind)
    pool = list(rows.order_by("-embedded_at")[:candidates])
    best = rank.top(vectors[0], ((c, c.embedding) for c in pool), limit, min_score)
    message_model = _message_model(chunk_model)
    out = []
    for c, score in best:
        lines = [l for l in thread_lines(message_model, c.thread) if c.first_seq <= l.seq <= c.last_seq]
        text = "\n".join(chunking.render(l) for l in lines)
        out.append(Hit(c.thread_id, c.thread.title, c.thread.kind, c.first_seq, c.last_seq, round(score, 4), text[:SNIPPET_CHARS]))
    return out
