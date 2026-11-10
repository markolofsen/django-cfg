"""Cut a text to a character budget and say so: `[cut: kept N of M chars]`.

One helper for the stored tool output (`streaming._clamp`) and the tool result the model reads
(`chat.compaction`), so a reader of either sees how much is missing instead of a text that just ends.
"""

from __future__ import annotations


def cut_marker(kept: int, total: int) -> str:
    return f"\n[cut: kept {kept} of {total} chars]"


def clamp_text(text: str, limit: int) -> str:
    """`text` as is when it fits; otherwise its first `limit` characters and the marker."""
    return text if len(text) <= limit else text[:limit] + cut_marker(limit, len(text))
