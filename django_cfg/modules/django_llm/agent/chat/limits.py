"""A site-wide token breaker: a UTC-day token budget in the shared cache, open when spent.

    breaker = TokenBreaker(budget=lambda: settings.CHAT_DAILY_TOKENS)
    service = ChatService(Thread, policy, on_answer=breaker.on_answer)
    # policy: ChatPolicy(available=breaker.available)  -> the send is refused with `ServiceUnavailable` (503) once the day's budget is spent

It counts tokens of every user together (the per-user dial is `ChatPolicy.check_quota`). `budget` may be a callable read on every
use. `None` or 0 means no budget (never open). The key shape is the host's (`key="chat:tokens:{day}"`), so a count that already
runs under another name survives the switch.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any

from django.core.cache import cache as default_cache
from django.utils import timezone

from django_cfg.modules.django_llm.agent.chat.errors import ServiceUnavailable


class TokenBreaker:
    def __init__(
        self,
        budget: int | None | Callable[[], int | None],
        *,
        cache: Any = None,
        key: str = "chat:tokens:{day}",
        clock: Callable[[], datetime] = timezone.now,
    ):
        self._budget = budget
        self._cache = cache
        self.key = key
        self.clock = clock

    @property
    def cache(self) -> Any:
        return self._cache or default_cache

    @property
    def budget(self) -> int | None:
        return self._budget() if callable(self._budget) else self._budget

    def _key(self) -> str:
        return self.key.format(day=self.clock().astimezone(dt_timezone.utc).strftime("%Y%m%d"))

    def spent(self) -> int:
        return int(self.cache.get(self._key(), 0) or 0)

    def spend(self, tokens: int) -> int:
        """Add tokens to today's count; returns the new count. Never raises: a cache outage must not fail an answer."""
        tokens = int(tokens or 0)
        if tokens <= 0:
            return self.spent()
        key = self._key()
        try:
            self.cache.add(key, 0, timeout=int(timedelta(days=2).total_seconds()))
            return int(self.cache.incr(key, tokens))
        except Exception:  # noqa: BLE001
            return 0

    def is_open(self) -> bool:
        budget = self.budget
        return bool(budget) and self.spent() >= budget

    def available(self) -> bool:
        """For `ChatPolicy.available`."""
        return not self.is_open()

    def check(self) -> None:
        """For a view gate: raise `ServiceUnavailable` (retry-after: the next UTC midnight) while open."""
        if self.is_open():
            now = self.clock().astimezone(dt_timezone.utc)
            midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=dt_timezone.utc)
            raise ServiceUnavailable(retry_after=int((midnight - now).total_seconds()) + 1)

    def on_answer(self, message: Any, outcome: Any) -> None:
        """For `ChatService(on_answer=...)`: spend the answer's tokens."""
        self.spend((message.tokens_in or 0) + (message.tokens_out or 0))
