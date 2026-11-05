"""Transcribe a recording through a chain of models without dying on a block.

Per piece, in this order:

1. Ask each entry of the chain. A **block** (``ContentBlocked``) marks that entry
   done for *this audio*: it is never asked again. A **transient** fault leaves
   the entry in play for the next round. A ``ModelUnavailable`` drops it. A
   ``Fatal`` (no key, no credit) stops everything.
2. If every entry blocked, **halve** the piece (bounded) and run the halves.
3. A piece that stays blocked at the floor becomes a **gap**; the rest goes on.
   A piece whose transient faults outlast the rounds becomes a *retryable* gap.

Money: a refused call is often billed. Every attempt's cost is summed into the
piece, and into ``Result.cost_usd``; the segment names the model that answered.

The I/O is injected (``cut``, ``ask``, ``sleep``), so the whole policy runs in a
test with no network and no ffmpeg.
"""

from __future__ import annotations

import random
import time
from decimal import Decimal
from typing import Callable, Optional, Sequence

from .engines import Ask
from .errors import ContentBlocked, Fatal, ModelUnavailable, NothingTranscribed, Transient
from .models import Answer, ChainEntry, Gap, Policy, Result, Segment

#: ``cut(offset_s, seconds) -> audio bytes`` for one piece of the recording.
Cut = Callable[[float, float], bytes]
Progress = Callable[[float, float], None]  # (seconds covered so far, total)


def plan(duration_s: float, chunk_s: float, min_tail_s: float = 30.0) -> list[tuple[float, float]]:
    """``[(start, end)]`` covering the recording; a tail shorter than ``min_tail_s`` joins the last piece."""
    count = max(1, -(-int(duration_s * 100) // int(chunk_s * 100)))
    if count > 1 and duration_s - (count - 1) * chunk_s < min_tail_s:
        count -= 1
    return [(i * chunk_s, duration_s if i == count - 1 else (i + 1) * chunk_s) for i in range(count)]


def transcribe(
    duration_s: float,
    cut: Cut,
    ask: Ask,
    chain: Sequence[ChainEntry],
    *,
    policy: Policy = Policy(),
    done: Optional[Sequence[Segment]] = None,
    on_progress: Optional[Progress] = None,
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
) -> Result:
    """Transcribe ``duration_s`` seconds. ``done``: segments from an earlier run, kept
    as they are; only the ranges they do not cover are asked again (cost is not charged twice).

    Raises ``Fatal`` (no key / no credit) and ``NothingTranscribed`` (every piece a gap).
    """
    if not chain:
        raise ValueError("the chain is empty")
    result = Result(segments=sorted(done or [], key=lambda s: s.start_s))
    covered = {(s.start_s, s.end_s) for s in result.segments}
    ctx = _Ctx(cut, ask, tuple(chain), policy, sleep, rng, result)
    for start, end in plan(duration_s, policy.chunk_s):
        if (start, end) in covered:
            _progress(on_progress, end, duration_s)
            continue
        ctx.piece(start, end, 0)
        _progress(on_progress, end, duration_s)
    result.segments.sort(key=lambda s: s.start_s)
    result.gaps.sort(key=lambda g: g.start_s)
    if not result.segments:
        raise NothingTranscribed(
            "; ".join(dict.fromkeys(g.detail for g in result.gaps if g.detail))[:300] or "no text produced"
        )
    return result


def transcribe_range(
    start_s: float,
    end_s: float,
    cut: Cut,
    ask: Ask,
    chain: Sequence[ChainEntry],
    *,
    policy: Policy = Policy(),
    context: str = "",
    sleep: Callable[[float], None] = time.sleep,
    rng: Callable[[], float] = random.random,
) -> Result:
    """One piece of the recording, with the whole policy (chain, backoff, halving, gap).

    For a caller that stores each piece as it is done (a job queue that may be
    killed between pieces): call this per piece and persist the returned
    ``Result``. Never raises ``NothingTranscribed``: a piece that gave no text is
    a ``Gap`` in the result. ``Fatal`` still raises.
    """
    if not chain:
        raise ValueError("the chain is empty")
    result = Result()
    _Ctx(cut, ask, tuple(chain), policy, sleep, rng, result, context).piece(start_s, end_s, 0)
    result.segments.sort(key=lambda s: s.start_s)
    result.gaps.sort(key=lambda g: g.start_s)
    return result


def _progress(cb: Optional[Progress], covered: float, total: float) -> None:
    if cb:
        cb(min(covered, total), total)


class _Ctx:
    def __init__(self, cut, ask, chain, policy, sleep, rng, result, context=""):
        self.cut, self.ask, self.chain, self.policy = cut, ask, chain, policy
        self.sleep, self.rng, self.result, self.seed = sleep, rng, result, context

    def piece(self, start: float, end: float, depth: int) -> None:
        audio = self.cut(start, end - start)
        spent = Decimal("0")
        blocked: dict[str, str] = {}
        gone: set[str] = set()
        transient: list[str] = []
        answer: Optional[tuple[ChainEntry, Answer]] = None
        for round_ in range(self.policy.rounds):
            transient = []
            for entry in self.chain:
                if entry.model in blocked or entry.model in gone:
                    continue
                try:
                    got = self.ask(entry, audio, self._context())
                except ContentBlocked as err:
                    spent += err.cost_usd
                    blocked[entry.model] = str(err)
                    continue
                except ModelUnavailable as err:
                    spent += err.cost_usd
                    gone.add(entry.model)
                    continue
                except Transient as err:
                    spent += err.cost_usd
                    transient.append(str(err))
                    continue
                except Fatal as err:
                    self.result.cost_usd += spent + err.cost_usd
                    raise
                spent += got.cost_usd
                answer = (entry, got)
                if not got.truncated:  # a cut-short answer tries the next entry and keeps the last
                    break
            if answer is not None:
                break
            if not transient:  # nothing time can mend: every entry blocked or gone
                break
            if round_ + 1 < self.policy.rounds:
                self.sleep(self.policy.pause_s * 2**round_ * (0.5 + self.rng()))
        self.result.cost_usd += spent
        if answer is not None:
            entry, got = answer
            self.result.segments.append(
                Segment(start, end, got.text, got.language, entry.model, spent)
            )
            return
        if transient:  # time may mend it: report it, do not lie that it was refused
            self.result.gaps.append(Gap(start, end, "failed", "; ".join(dict.fromkeys(transient))[:300], True, spent))
            return
        if depth < self.policy.max_depth and (end - start) / 2 >= self.policy.floor_s:
            # What the refused attempts cost is already in the total; the halves add their own.
            mid = round(start + (end - start) / 2, 2)
            self.piece(start, mid, depth + 1)
            self.piece(mid, end, depth + 1)
            return
        detail = "; ".join(dict.fromkeys(blocked.values()))[:300] or "no model could take it"
        self.result.gaps.append(Gap(start, end, "blocked", detail, False, spent))

    def _context(self) -> str:
        segs = self.result.segments
        text = segs[-1].text if segs else self.seed
        return text[-self.policy.context_chars:] if self.policy.context_chars else ""
