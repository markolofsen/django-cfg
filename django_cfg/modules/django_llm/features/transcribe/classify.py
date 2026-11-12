"""Tell a block from a fault in what a provider sent back.

A content filter is not an HTTP error. Gemini, through OpenRouter, answers
``200`` with the refusal in the body; others set ``finish_reason`` or send an
``error`` object. Each shape is recognised here and nowhere else.
"""

from __future__ import annotations

import re
from decimal import Decimal
from typing import Any, Mapping

from .errors import ContentBlocked, Fatal, ModelUnavailable, Transient
from .models import Answer

_BLOCK_WORDS = re.compile(
    r"PROHIBITED_CONTENT|content[_ ]policy|content[_ ]filter|blockReason|"
    r"\bSAFETY\b|\bBLOCKLIST\b|\bRECITATION\b|responsible ai|violat\w* .*polic",
    re.IGNORECASE,
)
_BLOCK_FINISH = {"content_filter", "safety", "prohibited_content", "blocklist"}
_LANG_LINE = re.compile(r"^(none|[a-z]{2,3}(-[a-z]{2,4})?)$")


def status_to_error(model: str, status: int, message: str) -> Exception:
    """A failed call by HTTP status. ``status`` 0 means the network or an unreadable body."""
    text = f"{model}: {message[:200]}"
    if status in (401, 402):
        return Fatal(text)
    if status == 404:
        return ModelUnavailable(text)
    if status == 403 and _BLOCK_WORDS.search(message):
        return ContentBlocked(text)
    if status == 429 or status >= 500:
        return Transient(text)
    return ModelUnavailable(text)


def _error_body(model: str, err: Mapping[str, Any], cost: Decimal = Decimal("0")) -> Exception:
    message = str(err.get("message") or err)
    meta = err.get("metadata") or {}
    blob = f"{message} {meta}"
    if meta.get("error_type") == "content_policy_violation" or _BLOCK_WORDS.search(blob):
        return ContentBlocked(f"{model}: {message[:200]}", cost)
    code = err.get("code")
    out = status_to_error(model, code if isinstance(code, int) else 0, message)
    out.cost_usd = cost
    return out


def parse_chat(model: str, resp: Any) -> Answer:
    """An ``/chat/completions`` body as an ``Answer``, or the right exception.

    Order: an ``error`` object, then a refusal field or a blocking
    ``finish_reason``, then the text. A body with none of them is
    ``ModelUnavailable`` (a shape we do not know), never a block.
    """
    if not isinstance(resp, Mapping):
        raise ModelUnavailable(f"{model}: unreadable answer")
    if not resp.get("choices"):
        err = resp.get("error")
        if isinstance(err, Mapping):
            raise _error_body(model, err, _cost(resp))
        feedback = resp.get("promptFeedback")
        if isinstance(feedback, Mapping) and feedback.get("blockReason"):
            raise ContentBlocked(f"{model}: {feedback['blockReason']}", _cost(resp))
        raise ModelUnavailable(f"{model}: answer without choices: {str(resp)[:200]}")
    choice = resp["choices"][0] or {}
    message = choice.get("message") or {}
    finish = str(choice.get("finish_reason") or "").lower()
    if message.get("refusal") or finish in _BLOCK_FINISH:
        reason = message.get("refusal") or finish
        raise ContentBlocked(f"{model}: {str(reason)[:200]}", _cost(resp))
    text = message.get("content")
    if not isinstance(text, str):
        # An empty content with a native finish reason that names a filter is a block too.
        native = str(choice.get("native_finish_reason") or "")
        if _BLOCK_WORDS.search(native):
            raise ContentBlocked(f"{model}: {native}", _cost(resp))
        raise ModelUnavailable(f"{model}: no text in the answer")
    language, body = split_language(text)
    return Answer(body, language, _cost(resp), truncated=finish == "length")


def parse_stt(model: str, resp: Any) -> Answer:
    """An ``/audio/transcriptions`` body: ``{"text": ..., "usage": {...}}``; with ``segments`` that carry a
    ``speaker`` and more than one voice, the text reads ``Speaker 1: ...`` one turn per paragraph."""
    if not isinstance(resp, Mapping):
        raise ModelUnavailable(f"{model}: unreadable answer")
    if isinstance(resp.get("error"), Mapping):
        raise _error_body(model, resp["error"], _cost(resp))
    text = resp.get("text")
    if not isinstance(text, str):
        raise ModelUnavailable(f"{model}: no text in the answer")
    return Answer(_turns(resp.get("segments")) or text.strip(), _language(resp.get("language")), _cost(resp))


def _language(value: Any) -> str:
    code = str(value or "").strip().lower().split("-")[0]
    return code if re.fullmatch(r"[a-z]{2,3}", code) else ""


def _turns(segments: Any) -> str:
    """Segments with speaker ids as turns, numbered from 1 in order of first appearance; ``""`` when there is
    nothing to label (no ids, or one voice): a monologue stays plain text."""
    if not isinstance(segments, list):
        return ""
    rows = [(s.get("speaker"), str(s.get("text") or "").strip()) for s in segments if isinstance(s, Mapping)]
    rows = [(who, text) for who, text in rows if text]
    voices = list(dict.fromkeys(who for who, _ in rows))
    if len(voices) < 2 or None in voices:
        return ""
    number = {who: i + 1 for i, who in enumerate(voices)}
    turns: list[list] = []
    for who, text in rows:
        if turns and turns[-1][0] == who:
            turns[-1][1] += " " + text
        else:
            turns.append([who, text])
    return "\n\n".join(f"Speaker {number[who]}: {text}" for who, text in turns)


def split_language(text: str) -> tuple[str, str]:
    """``(language, transcript)``: the model's first line is an ISO 639-1 code, or ``none``."""
    body = (text or "").strip()
    first, _, rest = body.partition("\n")
    code = first.strip().lower().rstrip(".")
    if _LANG_LINE.match(code):
        return ("" if code == "none" else code), ("" if code == "none" else rest.strip())
    return "", body


def _cost(resp: Mapping[str, Any]) -> Decimal:
    usage = resp.get("usage")
    value = usage.get("cost") if isinstance(usage, Mapping) else None
    try:
        return Decimal(str(value)) if value is not None else Decimal("0")
    except Exception:
        return Decimal("0")
