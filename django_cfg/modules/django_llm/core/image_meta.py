"""Strip non-pixel metadata from image bytes (PNG, JPEG, WebP, GIF byte-level, then a second pass and AVIF/HEIF/TIFF through remove-ai-watermarks' metadata function).

``strip(data)`` removes EXIF (GPS, software), XMP, IPTC, comments, PNG text chunks
(where generators leave prompts), timestamps, thumbnails and C2PA / JUMBF manifests
(Content Credentials). Pixels are never re-encoded: containers are filtered at the
byte level, so the decoded image is identical before and after.

The one step that does change pixels is the visible-mark pass in ``apply()``: it
removes known visible AI marks (the Gemini sparkle, vendor text labels, badges). It
runs only when the optional ``visible`` extra of ``remove-ai-watermarks`` (OpenCV) is
installed, and only when a mark is actually found. Otherwise ``apply()`` is the
metadata strip alone.

Kept on purpose, because dropping them changes how the picture looks:
  * the colour profile (``keep_icc=True``; ``keep_icc=False`` drops it too),
  * EXIF **orientation**, reduced to a minimal EXIF holding that one tag (a JPEG or
    WebP with orientation != 1 would otherwise turn sideways),
  * JPEG ``APP0`` (JFIF) and ``APP14`` (Adobe colour transform), PNG gamma/palette/
    transparency/animation chunks.

Not removed, and not claimed to be: an invisible watermark inside the pixels
(for example SynthID). Removing a C2PA manifest also removes a disclosure label;
labelling AI imagery where a law or platform requires it stays with the host.

Never raises on bad input: unsupported or damaged bytes come back unchanged with
``MetadataReport.error`` set.
"""

from __future__ import annotations

import importlib.util
import logging
import os
import struct
from dataclasses import dataclass, field, replace
from typing import Final, Literal

logger = logging.getLogger(__name__)

Mode = Literal["strip", "keep"]

PNG_SIG: Final = b"\x89PNG\r\n\x1a\n"
MAX_BYTES: Final = 64 * 1024 * 1024

_PNG_KEEP: Final = frozenset({
    b"IHDR", b"IDAT", b"IEND", b"PLTE", b"tRNS", b"gAMA", b"cHRM", b"sRGB", b"iCCP", b"cICP",
    b"pHYs", b"bKGD", b"sBIT", b"sPLT", b"hIST", b"acTL", b"fcTL", b"fdAT",
})
_PNG_NOTE: Final = {
    b"caBX": "C2PA manifest (Content Credentials)", b"eXIf": "EXIF", b"tEXt": "text chunk",
    b"zTXt": "compressed text chunk", b"iTXt": "UTF-8 text chunk (XMP / prompts)", b"tIME": "timestamp",
}
_WEBP_KEEP: Final = frozenset({b"VP8X", b"VP8 ", b"VP8L", b"ALPH", b"ANIM", b"ANMF", b"ICCP"})
_WEBP_NOTE: Final = {b"EXIF": "EXIF", b"XMP ": "XMP", b"C2PA": "C2PA manifest (Content Credentials)"}
_JPEG_NOTE: Final = {
    0xE1: "APP1 EXIF / XMP", 0xEB: "APP11 JUMBF (C2PA manifest)", 0xED: "APP13 Photoshop / IPTC",
    0xFE: "COM comment", 0xE2: "APP2 (MPF / non-ICC)",
}


@dataclass(frozen=True)
class MetadataReport:
    format: str = ""                          # png | jpeg | webp | gif | "" (unsupported)
    removed: tuple[str, ...] = field(default_factory=tuple)
    kept: tuple[str, ...] = field(default_factory=tuple)
    c2pa: bool = False                        # a Content Credentials manifest was present
    bytes_before: int = 0
    bytes_after: int = 0
    error: str | None = None
    #: AI-provenance markers still found after both passes (library re-scan); empty when clean.
    survived: tuple[str, ...] = field(default_factory=tuple)
    #: Visible AI marks removed from the pixels by the optional pass in ``apply()``; empty when none.
    watermarks: tuple[str, ...] = field(default_factory=tuple)
    #: Invisible (SynthID) stage outcome. ``apply()`` never runs it (CUDA-only), so this is "not-run".
    invisible: str = ""

    @property
    def changed(self) -> bool:
        return self.bytes_after != self.bytes_before


def sniff(data: bytes) -> str:
    if data.startswith(PNG_SIG):
        return "png"
    if data[:2] == b"\xff\xd8":
        return "jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis", b"heic", b"heix", b"mif1", b"msf1", b"hevc"):
        return "avif" if data[8:12] in (b"avif", b"avis") else "heif"
    if data[:4] in (b"II*\x00", b"MM\x00*"):
        return "tiff"
    return ""


# -- orientation -----------------------------------------------------------------

def _orientation(tiff: bytes) -> int:
    """EXIF orientation (1-8) from a TIFF block, 1 when absent or unreadable."""
    try:
        end = "<" if tiff[:2] == b"II" else ">" if tiff[:2] == b"MM" else ""
        if not end:
            return 1
        (off,) = struct.unpack(end + "I", tiff[4:8])
        (count,) = struct.unpack(end + "H", tiff[off:off + 2])
        for i in range(min(count, 256)):
            entry = tiff[off + 2 + i * 12: off + 14 + i * 12]
            tag, typ, n = struct.unpack(end + "HHI", entry[:8])
            if tag == 0x0112 and typ == 3 and n == 1:
                v = struct.unpack(end + "H", entry[8:10])[0]
                return v if 1 <= v <= 8 else 1
    except Exception:  # noqa: BLE001 - damaged EXIF: treat as upright
        return 1
    return 1


def _minimal_tiff(orientation: int) -> bytes:
    return (b"MM\x00\x2a\x00\x00\x00\x08" + struct.pack(">H", 1)
            + struct.pack(">HHI", 0x0112, 3, 1) + struct.pack(">H", orientation) + b"\x00\x00"
            + b"\x00\x00\x00\x00")


def _tiff_of(payload: bytes) -> bytes:
    return payload[6:] if payload.startswith(b"Exif\x00\x00") else payload


# -- PNG -------------------------------------------------------------------------

def _strip_png(data: bytes, keep_icc: bool) -> tuple[bytes, list[str], list[str]]:
    out, removed, kept = [PNG_SIG], [], []
    pos, saw_end = len(PNG_SIG), False
    while pos + 12 <= len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        end = pos + 12 + length
        if end > len(data):
            raise ValueError("truncated PNG chunk")
        keep = ctype in _PNG_KEEP and (ctype != b"iCCP" or keep_icc)
        if keep:
            out.append(data[pos:end])
            if ctype == b"iCCP":
                kept.append("ICC profile")
        else:
            removed.append(_PNG_NOTE.get(ctype, f"chunk {ctype.decode('latin-1')}"))
        pos = end
        if ctype == b"IEND":
            saw_end = True
            break
    if not saw_end:
        raise ValueError("PNG has no IEND")
    return b"".join(out), removed, kept


# -- JPEG ------------------------------------------------------------------------

def _strip_jpeg(data: bytes, keep_icc: bool) -> tuple[bytes, list[str], list[str]]:
    out, removed, kept = [data[:2]], [], []
    orientation = 1
    minimal_at = None
    pos = 2
    scanned = False
    while pos + 2 <= len(data):
        if data[pos] != 0xFF:
            raise ValueError("bad JPEG marker")
        marker = data[pos + 1]
        if marker == 0xFF:                       # fill byte
            pos += 1
            continue
        if marker == 0xDA or marker == 0xD9:     # scan data / EOI: copy the rest
            out.append(data[pos:])
            scanned = True
            break
        if pos + 4 > len(data):
            raise ValueError("truncated JPEG")
        (length,) = struct.unpack(">H", data[pos + 2:pos + 4])
        end = pos + 2 + length
        if length < 2 or end > len(data):
            raise ValueError("truncated JPEG segment")
        seg, payload = data[pos:end], data[pos + 4:end]
        if marker == 0xE1:
            if payload.startswith(b"Exif\x00\x00"):
                orientation = max(orientation, _orientation(_tiff_of(payload)))
                if minimal_at is None:
                    minimal_at = len(out)
                    out.append(b"")              # placeholder for the minimal EXIF
            removed.append(_JPEG_NOTE[0xE1])
        elif marker == 0xE2 and payload.startswith(b"ICC_PROFILE\x00") and keep_icc:
            out.append(seg)
            if "ICC profile" not in kept:
                kept.append("ICC profile")
        elif marker in (0xE2, 0xEB, 0xED, 0xFE) or 0xE3 <= marker <= 0xEF and marker != 0xEE:
            removed.append(_JPEG_NOTE.get(marker, f"APP{marker - 0xE0}"))
        else:
            out.append(seg)                      # JFIF, Adobe APP14, tables, frame header
        pos = end
    if not scanned:
        raise ValueError("JPEG has no scan data")
    if minimal_at is not None and orientation != 1:
        payload = b"Exif\x00\x00" + _minimal_tiff(orientation)
        out[minimal_at] = b"\xff\xe1" + struct.pack(">H", len(payload) + 2) + payload
        kept.append(f"EXIF orientation={orientation}")
    return b"".join(out), removed, kept


# -- WebP ------------------------------------------------------------------------

def _strip_webp(data: bytes, keep_icc: bool) -> tuple[bytes, list[str], list[str]]:
    (size,) = struct.unpack("<I", data[4:8])
    body_end = min(len(data), 8 + size)
    pos, chunks, removed, kept = 12, [], [], []
    orientation = 1
    while pos + 8 <= body_end:
        cid, (clen,) = data[pos:pos + 4], struct.unpack("<I", data[pos + 4:pos + 8])
        end = pos + 8 + clen + (clen & 1)
        if pos + 8 + clen > body_end:
            raise ValueError("truncated WebP chunk")
        payload = data[pos + 8:pos + 8 + clen]
        if cid == b"EXIF":
            orientation = max(orientation, _orientation(_tiff_of(payload)))
            removed.append("EXIF")
        elif cid in _WEBP_KEEP and (cid != b"ICCP" or keep_icc):
            chunks.append([cid, payload])
            if cid == b"ICCP":
                kept.append("ICC profile")
        else:
            removed.append(_WEBP_NOTE.get(cid, f"chunk {cid.decode('latin-1')}"))
        pos = end
    if orientation != 1:
        chunks.append([b"EXIF", _minimal_tiff(orientation)])
        kept.append(f"EXIF orientation={orientation}")
    present = {c[0] for c in chunks}
    for c in chunks:
        if c[0] == b"VP8X" and len(c[1]) >= 10:
            flags = c[1][0] & ~(0x08 | 0x04 | 0x20)          # EXIF, XMP, ICC off, then back on if present
            flags |= (0x08 if b"EXIF" in present else 0) | (0x20 if b"ICCP" in present else 0)
            c[1] = bytes([flags]) + c[1][1:]
    # VP8X must come first, then ICCP; EXIF goes after the image data.
    order = {b"VP8X": 0, b"ICCP": 1, b"ANIM": 2}
    chunks.sort(key=lambda c: (c[0] == b"EXIF", order.get(c[0], 3)) if c[0] != b"EXIF" else (True, 9))
    body = b"".join(c[0] + struct.pack("<I", len(c[1])) + c[1] + (b"\x00" if len(c[1]) & 1 else b"") for c in chunks)
    return b"RIFF" + struct.pack("<I", 4 + len(body)) + b"WEBP" + body, removed, kept


# -- GIF -------------------------------------------------------------------------

def _skip_subblocks(data: bytes, pos: int) -> int:
    while True:
        if pos >= len(data):
            raise ValueError("truncated GIF")
        n = data[pos]
        pos += 1 + n
        if n == 0:
            return pos


def _strip_gif(data: bytes, keep_icc: bool) -> tuple[bytes, list[str], list[str]]:
    flags = data[10]
    pos = 13 + (3 * (2 << (flags & 7)) if flags & 0x80 else 0)
    out, removed = [data[:pos]], []
    while pos < len(data):
        block = data[pos]
        if block == 0x3B:
            out.append(data[pos:pos + 1])
            return b"".join(out), removed, []
        if block == 0x21:
            label = data[pos + 1]
            end = _skip_subblocks(data, pos + 2 + 1 + data[pos + 2]) if label in (0xFF,) else _skip_subblocks(data, pos + 2)
            if label == 0xFE:
                removed.append("comment extension")
            elif label == 0xFF:
                app = data[pos + 3:pos + 3 + data[pos + 2]]
                if app.startswith((b"NETSCAPE", b"ANIMEXTS")):
                    out.append(data[pos:end])
                else:
                    removed.append(f"application extension {app[:11].decode('latin-1').strip()}")
            else:
                out.append(data[pos:end])
            pos = end
        elif block == 0x2C:
            lflags = data[pos + 9]
            hdr = 10 + (3 * (2 << (lflags & 7)) if lflags & 0x80 else 0)
            end = _skip_subblocks(data, pos + hdr + 1)
            out.append(data[pos:end])
            pos = end
        else:
            raise ValueError("bad GIF block")
    raise ValueError("GIF has no trailer")


_LIB_SUFFIX = {"avif": ".avif", "heif": ".heic", "tiff": ".tif"}


def _strip_with_library(data: bytes, fmt: str, keep_icc: bool) -> tuple[bytes, list[str], list[str]]:
    """Containers this module does not parse go through ``remove-ai-watermarks``' METADATA function only.

    Imported lazily; no pixel or watermark module of that package is touched. Works on files, so a temp dir is used.
    """
    import tempfile
    from pathlib import Path

    from remove_ai_watermarks.metadata import remove_ai_metadata  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / f"in{_LIB_SUFFIX[fmt]}"
        dst = Path(tmp) / f"out{_LIB_SUFFIX[fmt]}"
        src.write_bytes(data)
        remove_ai_metadata(src, dst, keep_standard=True)
        clean = dst.read_bytes()
    removed = ["AI-provenance metadata (remove-ai-watermarks)"] if clean != data else []
    return clean, removed, []


def _library_pass(data: bytes, fmt: str) -> tuple[bytes, list[str], tuple[str, ...]]:
    """Second pass over bytes our own filter already cleaned: ``remove-ai-watermarks``' metadata strip + re-scan.

    It knows vendor-specific AI markers we do not parse (China TC260 labels, Samsung/xAI signatures, IPTC AI notes) and reports
    what it could not remove. ``keep_standard=True`` on purpose: with False it drops orientation and the colour profile.
    Returns ``(bytes, removed_notes, survivors)``; any failure returns the input unchanged.
    """
    import tempfile
    from pathlib import Path

    survivors: dict = {}
    try:
        from remove_ai_watermarks.metadata import strip_and_verify  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            suffix = {"jpeg": ".jpg", "png": ".png", "webp": ".webp", "gif": ".gif"}.get(fmt, f".{fmt}")
            src, dst = Path(tmp) / f"in{suffix}", Path(tmp) / f"out{suffix}"
            src.write_bytes(data)
            out_path, survivors = strip_and_verify(src, dst, keep_standard=True)
            out = Path(out_path).read_bytes()
    except Exception:  # noqa: BLE001 - the second pass is additive, never blocks the result
        return data, [], ()
    if not out or sniff(out) != fmt:
        return data, [], tuple(f"{k}: {v}" for k, v in (survivors or {}).items())
    note = ["vendor AI markers (remove-ai-watermarks)"] if out != data else []
    return out, note, tuple(f"{k}: {v}" for k, v in (survivors or {}).items())


_STRIPPERS = {"png": _strip_png, "jpeg": _strip_jpeg, "webp": _strip_webp, "gif": _strip_gif}


def strip(data: bytes, *, keep_icc: bool = True) -> tuple[bytes, MetadataReport]:
    """Return ``(clean_bytes, report)``. On unsupported or damaged input: ``(data, report-with-error)``."""
    fmt = sniff(data)
    base = MetadataReport(format=fmt, bytes_before=len(data), bytes_after=len(data))
    if not fmt:
        return data, MetadataReport(bytes_before=len(data), bytes_after=len(data), error="unsupported format")
    if len(data) > MAX_BYTES:
        return data, MetadataReport(fmt, bytes_before=len(data), bytes_after=len(data), error="file too large")
    try:
        if fmt in _STRIPPERS:
            clean, removed, kept = _STRIPPERS[fmt](data, keep_icc)
        else:
            clean, removed, kept = _strip_with_library(data, fmt, keep_icc)
    except Exception as exc:  # noqa: BLE001 - never raise on hostile or damaged bytes
        return data, MetadataReport(base.format, bytes_before=len(data), bytes_after=len(data), error=str(exc))
    survived: tuple[str, ...] = ()
    if fmt in _STRIPPERS:
        clean, extra, survived = _library_pass(clean, fmt)
        removed = removed + extra
    return clean, MetadataReport(
        fmt, tuple(dict.fromkeys(removed)), tuple(dict.fromkeys(kept)),
        c2pa=any("C2PA" in r for r in removed), bytes_before=len(data), bytes_after=len(clean), survived=survived,
    )


def inspect(data: bytes) -> MetadataReport:
    """What ``strip`` would remove, without returning bytes."""
    return strip(data)[1]


# -- default mode ----------------------------------------------------------------

def resolve_mode(explicit: str | None = None) -> Mode:
    """``explicit`` > ``settings.DJANGO_LLM_IMAGE_METADATA`` > env of the same name > ``"strip"``."""
    value = explicit
    if value is None:
        try:
            from django.conf import settings  # noqa: PLC0415

            value = getattr(settings, "DJANGO_LLM_IMAGE_METADATA", None)
        except Exception:  # noqa: BLE001 - Django absent or not configured
            value = None
    if value is None:
        value = os.environ.get("DJANGO_LLM_IMAGE_METADATA")
    value = (value or "strip").strip().lower()
    if value not in ("strip", "keep"):
        raise ValueError(f"image metadata mode must be 'strip' or 'keep', got {value!r}")
    return value  # type: ignore[return-value]


# -- visible AI marks (optional pixel pass) ------------------------------------------

_VISIBLE_SUFFIX: Final = {"png": ".png", "jpeg": ".jpg", "webp": ".webp"}


def _remove_visible_marks(data: bytes, fmt: str) -> tuple[bytes, tuple[str, ...]]:
    """Remove known visible AI marks from the pixels. Returns ``(bytes, labels_removed)``.

    Needs OpenCV (the ``visible`` extra of ``remove-ai-watermarks``); without it the input
    comes back unchanged and quietly. It reads the original file, before any metadata is
    touched, because the library finds a moved mark through the provenance in that metadata.
    GIF is not handled: the library reads one frame and would drop the animation.
    """
    suffix = _VISIBLE_SUFFIX.get(fmt)
    if suffix is None or importlib.util.find_spec("cv2") is None:
        return data, ()
    import tempfile
    from pathlib import Path

    try:
        from remove_ai_watermarks.api import remove_visible_detailed  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            src, dst = Path(tmp) / f"in{suffix}", Path(tmp) / f"out{suffix}"
            src.write_bytes(data)
            # write_noop=False: when nothing is found no file is written, and the original bytes stay.
            result = remove_visible_detailed(src, dst, strip_metadata=False, write_noop=False)
            if not result.labels or not dst.exists():
                return data, ()
            out = dst.read_bytes()
    except Exception as exc:  # noqa: BLE001 - a failed pixel pass must not fail the image
        logger.warning("visible AI-mark removal failed; the metadata strip still applies: %s", exc)
        return data, ()
    if sniff(out) != fmt:
        return data, ()
    return out, tuple(result.labels)


def apply(data: bytes, mode: str | None = None) -> tuple[bytes, MetadataReport | None]:
    """Clean generated image bytes unless the resolved mode is ``keep`` (then ``(data, None)``).

    ``strip`` runs the visible-mark pass first (on the original bytes, see
    ``_remove_visible_marks``), then the metadata strip on its result.
    """
    if resolve_mode(mode) == "keep":
        return data, None
    pixels, marks = _remove_visible_marks(data, sniff(data))
    clean, report = strip(pixels)
    return clean, replace(report, bytes_before=len(data), watermarks=marks, invisible="not-run")
