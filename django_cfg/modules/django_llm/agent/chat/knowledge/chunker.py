"""Markdown lines to chunks that know their line range and where in the file they sit. Pure: no I/O, no index.

A chunk is a run of lines of one section (H1-H3 start a section) of about `TARGET` characters, never above `HARD`. A code fence is
kept whole while it can be; a paragraph or fence longer than `HARD` is cut at a line. A heading with no body of its own joins the
chunk after it. Line numbers are absolute (1-based, as in the file), so a hit says `path:first-last`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TARGET = 900
HARD = 2400
_HEADING = re.compile(r"^(#{1,6})[ \t]+(.*\S)[ \t]*#*[ \t]*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


@dataclass(frozen=True)
class Chunk:
    start: int
    end: int
    crumb: tuple[str, ...]  # headings above and including the chunk's own, H1..H3 (H4+ only when they start a chunk)
    text: str


@dataclass(frozen=True)
class Heading:
    level: int
    text: str
    line: int
    end: int  # last line of the section, subsections included
    chars: int


def headings(lines: list[str] | tuple[str, ...], first_line: int = 1) -> list[Heading]:
    """Every heading outside code fences, with the line range of its section."""
    found: list[tuple[int, str, int]] = []
    fenced = False
    for offset, line in enumerate(lines):
        if _FENCE.match(line):
            fenced = not fenced
        elif not fenced and (m := _HEADING.match(line)):
            found.append((len(m.group(1)), m.group(2).strip(), first_line + offset))
    last = first_line + len(lines) - 1
    out = []
    for i, (level, text, line) in enumerate(found):
        end = last
        for later_level, _t, later_line in found[i + 1 :]:
            if later_level <= level:
                end = later_line - 1
                break
        out.append(Heading(level, text, line, end, sum(len(s) + 1 for s in lines[line - first_line : end - first_line + 1])))
    return out


def chunk(lines: list[str] | tuple[str, ...], first_line: int = 1) -> list[Chunk]:
    out: list[Chunk] = []
    stack: list[str] = ["", "", ""]
    buf: list[str] = []
    buf_start = first_line
    buf_crumb: tuple[str, ...] = ()
    body = False
    fenced = False
    size = 0

    def crumb() -> tuple[str, ...]:
        return tuple(h for h in stack if h)

    def flush(next_line: int) -> None:
        nonlocal buf, buf_start, body, size
        if buf and body:
            text = "\n".join(buf).rstrip("\n")
            last = buf_start + len(buf) - 1
            while last > buf_start and not buf[last - buf_start].strip():
                last -= 1
            out.append(Chunk(buf_start, last, buf_crumb, text))
            buf, body, size = [], False, 0
            buf_start = next_line
        elif not buf:
            buf_start = next_line

    for offset, line in enumerate(lines):
        number = first_line + offset
        is_fence = bool(_FENCE.match(line))
        heading = None if fenced or is_fence else _HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if level <= 3:
                flush(number)
                stack[level - 1 :] = [heading.group(2).strip()] + [""] * (3 - level)
            elif body and size >= TARGET:
                flush(number)
            if not buf:
                buf_start = number
            buf_crumb = crumb() if level <= 3 else (*crumb(), heading.group(2).strip())
            buf.append(line)
            size += len(line) + 1
            continue
        if not buf:
            buf_start, buf_crumb = number, crumb()
        buf.append(line)
        size += len(line) + 1
        if line.strip() and not is_fence:
            body = True
        elif is_fence:
            body = True
        if is_fence:
            fenced = not fenced
        # cut: at a blank line outside a fence once the target is reached, or at any line once the hard limit is
        if body and ((not fenced and not line.strip() and size >= TARGET) or size >= HARD):
            flush(number + 1)
            buf_crumb = crumb()
    flush(first_line + len(lines))
    return out
