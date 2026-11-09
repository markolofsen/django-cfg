"""`AttachmentPolicy`: what one chat kind accepts as a file, and how it is kept. Mechanics live in this package, product rules here.

    ChatKind(..., attachments=AttachmentPolicy(kinds=frozenset({"image", "document"}), max_files=4))

A kind without a policy accepts no file: its routes answer 404 and its history carries none.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

MB = 1024 * 1024
MEDIA_KINDS = frozenset({"image", "audio", "video", "text", "document"})
SUPPORTED_KINDS = frozenset({"image", "audio", "text", "document"})  # video is sniffed and refused in v1
CEILING_BYTES = 50 * MB  # one request body; a larger file waits for a presigned upload

DEFAULT_AUDIO_MODELS = ("qwen/qwen3.8-omni-flash", "google/gemini-3.1-flash-lite")

Delivery = Literal["signed", "presigned", "public"]
Unreadable = Literal["describe", "refuse", "note"]


@dataclass(frozen=True)
class AttachmentPolicy:
    kinds: frozenset[str] = frozenset({"image", "text", "document"})
    max_files: int = 4  # per message
    max_bytes: int = 10 * MB  # per file
    max_total_bytes: int = 25 * MB  # per message
    accept: tuple[str, ...] = ()  # narrows the sniffed mime types further (`"image/png"`, `"image/*"`); empty = every type of `kinds`
    daily_bytes: int | None = None  # staged bytes per user per UTC day; None = no cap
    keep_days: int | None = 30  # bytes of a sent file are deleted this many days after the upload; the row, name and read text stay. 0 = as soon as the turn that carried it is answered; None = keep
    staged_ttl_hours: int = 24  # an upload never sent is deleted after this
    url_ttl_s: int = 3600  # life of a signed or presigned link; every history read mints a fresh one
    storage: str = "default"  # Django `STORAGES` alias
    delivery: Delivery = "signed"  # signed: the API serves it behind a token; presigned: the store's own expiring URL; public: storage.url()
    on_unreadable: Unreadable = "describe"  # a file the model chain cannot read: read it through the OCR/vision model, refuse the turn, or pass a note
    replay_of: int = 2  # the latest N file-carrying user turns (this one included) send their files; earlier ones keep a one-line stub and the derived text
    text_chars: int = 40_000  # decoded text is cut to this before the model reads it
    image_max_px: int = 1568  # longest side after downscaling for the model
    vision: bool | None = None  # True: the kind's chain reads images and PDFs itself; False: always read them through `ocr_models`; None: ask the model catalogue (unknown = False)
    ocr_models: tuple[str, ...] | None = None  # cheap vision chain that reads an image for a text-only model; None = django_llm's own OCR model (`aread_image_text`)
    audio_models: tuple[str, ...] | None = None  # audio-capable chain that transcribes audio; None = `DEFAULT_AUDIO_MODELS`
    scan: Callable[[Any, str], None] | None = None  # (file-like at 0, mime) -> None; raise `InvalidTurn("file", "rejected")` to refuse

    def __post_init__(self) -> None:
        unknown = set(self.kinds) - MEDIA_KINDS
        if unknown:
            raise ValueError(f"unknown attachment kinds {sorted(unknown)}; known: {sorted(MEDIA_KINDS)}")
        if not 1 <= self.max_bytes <= CEILING_BYTES:
            raise ValueError(f"max_bytes must be 1..{CEILING_BYTES}")
        if self.max_total_bytes < self.max_bytes:
            raise ValueError("max_total_bytes must be at least max_bytes")
        if self.max_files < 1:
            raise ValueError("max_files must be at least 1")
        if self.delivery not in ("signed", "presigned", "public"):
            raise ValueError("delivery must be signed, presigned or public")
        if self.keep_days is not None and self.keep_days < 0:
            raise ValueError("keep_days must be 0, a number of days, or None")
        if self.on_unreadable not in ("describe", "refuse", "note"):
            raise ValueError("on_unreadable must be describe, refuse or note")

    def accepts(self, mime: str, media_kind: str) -> bool:
        if media_kind not in self.kinds:
            return False
        if not self.accept:
            return True
        return any(a == mime or (a.endswith("/*") and mime.startswith(a[:-1])) for a in self.accept)

    def accept_list(self) -> list[str]:
        """The mime types a client may offer, for the file picker."""
        if self.accept:
            return list(self.accept)
        every = {"image": ["image/png", "image/jpeg", "image/webp", "image/gif"], "document": ["application/pdf"],
                 "text": ["text/plain", "text/markdown", "text/csv", "application/json"], "audio": ["audio/mpeg", "audio/wav", "audio/ogg", "audio/flac", "audio/mp4"]}
        return [m for k in sorted(self.kinds) for m in every.get(k, [])]
