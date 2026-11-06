"""Consecutive messages to chunks. Pure: no I/O, no database, no embedder, so the knowledge base's embedding lane can reuse it.

A chunk is a run of consecutive messages of one thread. It is cut by count (`max_messages`, default 20) and by a token budget
(estimated, `CHARS_PER_TOKEN` characters a token): the next message that would break either bound starts the next chunk, and a
single message above the budget is clipped to it. Every chunk but the last is *closed* (its text never changes again); the last is
*open* and is re-embedded when it grows. The text of a chunk is `role: text` per message, so a hit reads as a conversation.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from dataclasses import dataclass

MIN_MESSAGES = 10  # a floor the settings may not go under: below it a chunk is a message with extra steps
MAX_MESSAGES = 20
TOKEN_BUDGET = 1500
CHARS_PER_TOKEN = 4


@dataclass(frozen=True)
class Line:
    seq: int
    role: str
    text: str


@dataclass(frozen=True)
class Span:
    first_seq: int
    last_seq: int
    count: int
    text: str
    tokens: int
    closed: bool

    @property
    def text_hash(self) -> str:
        return hashlib.sha256(self.text.encode()).hexdigest()


def estimate_tokens(text: str) -> int:
    return max(1, -(-len(text) // CHARS_PER_TOKEN)) if text else 0


def render(line: Line, budget: int = TOKEN_BUDGET) -> str:
    body = line.text.strip()[: budget * CHARS_PER_TOKEN]
    return f"{line.role}: {body}"


def chunk_lines(lines: Sequence[Line], *, max_messages: int = MAX_MESSAGES, token_budget: int = TOKEN_BUDGET) -> list[Span]:
    """Spans over `lines` (ordered by seq; empty texts are skipped). Deterministic from the start of the thread, so a closed
    span is the same on every run and only the last one can change."""
    if max_messages < MIN_MESSAGES:
        raise ValueError(f"max_messages must be at least {MIN_MESSAGES}")
    spans: list[Span] = []
    buf: list[Line] = []
    rendered: list[str] = []
    tokens = 0

    def close(closed: bool) -> None:
        text = "\n".join(rendered)
        spans.append(Span(buf[0].seq, buf[-1].seq, len(buf), text, tokens, closed))

    for line in lines:
        if not line.text.strip():
            continue
        piece = render(line, token_budget)
        cost = estimate_tokens(piece)
        if buf and (len(buf) >= max_messages or tokens + cost > token_budget):
            close(True)
            buf, rendered, tokens = [], [], 0
        buf.append(line)
        rendered.append(piece)
        tokens += cost
    if buf:
        close(False)
    return spans
