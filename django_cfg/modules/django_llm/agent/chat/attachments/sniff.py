"""What a file is, from its bytes. The client's content type and file extension are never trusted for the decision."""

from __future__ import annotations

_TEXT_BY_EXT = {"md": "text/markdown", "markdown": "text/markdown", "csv": "text/csv", "json": "application/json"}
_ACTIVE = (b"<svg", b"<!doctype", b"<html", b"<?xml", b"<script", b"<body", b"<iframe")
_SNIFF_BYTES = 8192


def sniff(head: bytes, name: str = "") -> tuple[str, str] | None:
    """`(mime, media_kind)` of a file given its first bytes, or None for a type the library does not serve.

    Active content (SVG, HTML, XML) is None on purpose: it would run in the viewer's origin.
    """
    h = head[:_SNIFF_BYTES]
    if h.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png", "image"
    if h.startswith(b"\xff\xd8\xff"):
        return "image/jpeg", "image"
    if h[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif", "image"
    if h[:4] == b"RIFF" and h[8:12] == b"WEBP":
        return "image/webp", "image"
    if h.startswith(b"%PDF-"):
        return "application/pdf", "document"
    if h[:4] == b"RIFF" and h[8:12] == b"WAVE":
        return "audio/wav", "audio"
    if h.startswith(b"OggS"):
        return "audio/ogg", "audio"
    if h.startswith(b"fLaC"):
        return "audio/flac", "audio"
    if h.startswith(b"ID3") or (len(h) > 1 and h[0] == 0xFF and h[1] & 0xE0 == 0xE0):
        return "audio/mpeg", "audio"
    if h[4:8] == b"ftyp":
        return ("audio/mp4", "audio") if h[8:12] in (b"M4A ", b"M4B ") else ("video/mp4", "video")
    if h.startswith(b"\x1aE\xdf\xa3"):
        return "video/webm", "video"
    if not h or b"\x00" in h:
        return None
    if h.lstrip(b"\xef\xbb\xbf \t\r\n").lower().startswith(_ACTIVE):
        return None
    try:
        h.decode("utf-8")
    except UnicodeDecodeError as err:
        if err.start < len(h) - 4:  # a multi-byte character cut by the window is not an error
            return None
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    return _TEXT_BY_EXT.get(ext, "text/plain"), "text"
