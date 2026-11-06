"""Domain failures of the chat service. A surface maps each to a status and a `{code, message}`; nothing inspects a message."""

from __future__ import annotations

from django_cfg.modules.django_llm.agent.chat.turn import Busy, InvalidTurn, TurnError  # noqa: F401 - re-exported: one vocabulary for callers


class ChatError(Exception):
    pass


class NotFound(ChatError):
    """No such live thread of this user, or it is someone else's, or its kind is gone: one answer for all."""


class InvalidKind(ChatError):
    """A kind name no chat kind is registered under."""


class InvalidContext(ChatError):
    def __init__(self, errors: list[dict]):
        super().__init__("invalid context")
        self.errors = errors


class QuotaExceeded(ChatError):
    """A host's quota refused the message. `code` and `status` choose the answer (default: 429 `rate_limited`).

    A quota callable raises it for a refusal that is not "too many today", e.g. a ledger refusal as `QuotaExceeded("out of credit", code="invalid", status=402)`.
    """

    def __init__(self, detail: str = "", *, code: str = "rate_limited", status: int = 429, retry_after: int | None = None):
        super().__init__(detail or code)
        self.code = code
        self.status = status
        self.retry_after = retry_after


class RateLimited(QuotaExceeded):
    """The user has sent today's allowance of messages."""

    def __init__(self, detail: str = "", *, retry_after: int | None = None):
        super().__init__(detail, code="rate_limited", status=429, retry_after=retry_after)


class ServiceUnavailable(ChatError):
    """The chat is switched off or out of budget (a kill switch, a spent token budget): nothing is read or stored. 503 `unavailable`."""

    def __init__(self, retry_after: int | None = None):
        super().__init__("unavailable")
        self.retry_after = retry_after
