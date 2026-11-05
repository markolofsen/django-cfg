"""How one entry of the chain is asked. Transport is injected: ``call(path, payload)``
returns the decoded JSON body, or raises an exception carrying ``.status`` (int)."""

from __future__ import annotations

import base64
from typing import Any, Callable

from .classify import parse_chat, parse_stt, status_to_error
from .errors import TranscribeError
from .models import Answer, ChainEntry

Call = Callable[[str, dict], Any]
#: ``ask(entry, audio, context) -> Answer``; raises a ``TranscribeError``.
Ask = Callable[[ChainEntry, bytes, str], Answer]

INSTRUCTION = """Transcribe this audio exactly as spoken, in the language spoken.
- Leave out only sounds that are not speech. Write [inaudible] where words cannot be made out; never guess them.
- Start a new paragraph when the speaker or the subject changes. No speaker labels, no timestamps, no headings, no markdown, no remarks of your own.
- Output format: the first line is the ISO 639-1 code of the main spoken language (for example en, ru, de, es). Then one empty line. Then the transcript.
- If nothing is spoken, output only one line: none"""

MAX_TOKENS = 16000


def make_ask(call: Call, *, audio_format: str = "mp3", instruction: str = INSTRUCTION,
             max_tokens: int = MAX_TOKENS) -> Ask:
    """The default ``ask``: ``chat`` entries go to ``/chat/completions`` with an
    ``input_audio`` part; ``stt`` entries to ``/audio/transcriptions``.

    The ``stt`` payload follows OpenRouter's documented shape (``input_audio`` with
    base64 ``data`` and ``format``); whether a given gateway exposes the route is
    something to probe, not assume.
    """

    def ask(entry: ChainEntry, audio: bytes, context: str = "") -> Answer:
        data = base64.b64encode(audio).decode()
        try:
            if entry.engine == "stt":
                resp = call("/audio/transcriptions",
                            {"model": entry.model, "input_audio": {"data": data, "format": audio_format}})
                return parse_stt(entry.model, resp)
            text = instruction
            if context:
                text += (f'\n- This audio continues a talk whose text so far ends: "{context}". '
                         "Transcribe only the new audio; do not repeat those words.")
            content = [{"type": "text", "text": text},
                       {"type": "input_audio", "input_audio": {"data": data, "format": audio_format}}]
            resp = call("/chat/completions",
                        {"model": entry.model, "messages": [{"role": "user", "content": content}],
                         "max_tokens": max_tokens, "temperature": 0, "usage": {"include": True}})
            return parse_chat(entry.model, resp)
        except TranscribeError:
            raise
        except Exception as exc:  # a transport failure: classify by status
            status = getattr(exc, "status", None)
            if not isinstance(status, int):
                status = 0
            if status == 0 and isinstance(exc, (OSError, TimeoutError)):
                status = 599  # network: treated as transient
            raise status_to_error(entry.model, status, str(exc)) from exc

    return ask
