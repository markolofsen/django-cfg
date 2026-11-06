"""The folder on disk: walk it under the security rules, read front matter, and turn a file into a `Doc`.

Rules (plan decision 6): only `.md` / `.mdx` / `.txt`; no dotfiles or dot-directories; symlinks are neither followed nor listed;
every path stays under the root (`resolve()` + `relative_to`); a file that is not UTF-8 or is too big is skipped with a reason
(`kb_check` shows them). Nothing here raises for a bad file.
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from django_cfg.modules.django_llm.agent.chat.knowledge.text import estimate_tokens, sanitize

EXTENSIONS = (".md", ".mdx", ".txt")
MAX_FILES = 5000
MAX_FILE_BYTES = 2_000_000
DESCRIPTION_CHARS = 120
INDEX_NAME = "_index.md"
_FENCE = re.compile(r"^\s*(```|~~~)")
_SENTENCE = re.compile(r"(?<=[.!?])\s")


class PathRejected(ValueError):
    """The path is not a legal knowledge-base path (absolute, `..`, dotfile, wrong extension ...)."""


@dataclass(frozen=True)
class Doc:
    path: str  # posix, relative to the root
    title: str
    description: str
    aliases: tuple[str, ...]
    lines: tuple[str, ...]  # the sanitized file, one string per line (line n is lines[n - 1])
    body_start: int  # first line after the front matter (1-based)
    sha: str
    size: int
    tokens: int
    stripped: int = 0  # comments / invisible characters removed
    has_front_matter: bool = False
    has_description: bool = False  # the description came from front matter
    problems: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()  # front matter that was read leniently: it works, but a strict YAML parser would refuse it

    @property
    def is_index(self) -> bool:
        return self.path.rsplit("/", 1)[-1] == INDEX_NAME

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


@dataclass(frozen=True)
class Skipped:
    path: str
    reason: str


@dataclass
class Scan:
    docs: list[Doc] = field(default_factory=list)
    skipped: list[Skipped] = field(default_factory=list)


def clean_path(path: str) -> str:
    """A caller's path as a legal relative posix path, or `PathRejected`."""
    if not isinstance(path, str) or not path.strip():
        raise PathRejected("empty path")
    raw = path.strip().replace("\\", "/")
    if "\x00" in raw or raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
        raise PathRejected("path must be relative to the knowledge base")
    parts = [p for p in raw.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        raise PathRejected("path must stay inside the knowledge base")
    if any(p.startswith(".") for p in parts):
        raise PathRejected("hidden files are not part of the knowledge base")
    return "/".join(parts)


def clean_doc_path(path: str) -> str:
    out = clean_path(path)
    if not out.lower().endswith(EXTENSIONS):
        raise PathRejected(f"only {', '.join(EXTENSIONS)} files are in the knowledge base")
    return out


def safe_join(root: Path, rel: str) -> Path:
    """`root / rel` if it is a regular, non-symlink path that really lies under `root`; else `PathRejected`."""
    rel = clean_doc_path(rel)
    base = root.resolve()
    cur = base
    for part in rel.split("/"):
        cur = cur / part
        if cur.is_symlink():
            raise PathRejected("symlinks are not followed")
    target = cur.resolve()
    try:
        target.relative_to(base)
    except ValueError:
        raise PathRejected("path escapes the knowledge base") from None
    return target


def walk(root: Path, *, max_files: int = MAX_FILES) -> Iterator[tuple[str, Path, os.stat_result | None, str | None]]:
    """`(relative path, absolute path, stat, skip reason)` for every candidate file, in a deterministic order.
    Directories are walked depth-first, names sorted; hidden entries and symlinks are not yielded at all."""
    count = 0

    def visit(directory: Path, prefix: str) -> Iterator[tuple[str, Path, os.stat_result | None, str | None]]:
        nonlocal count
        try:
            entries = sorted(os.scandir(directory), key=lambda e: e.name)
        except OSError:
            return
        for entry in entries:
            if entry.name.startswith(".") or entry.is_symlink():
                continue
            rel = f"{prefix}{entry.name}"
            if entry.is_dir(follow_symlinks=False):
                yield from visit(Path(entry.path), rel + "/")
            elif entry.is_file(follow_symlinks=False) and entry.name.lower().endswith(EXTENSIONS):
                count += 1
                if count > max_files:
                    yield rel, Path(entry.path), None, f"more than {max_files} files: the rest are not indexed"
                    continue
                st = entry.stat(follow_symlinks=False)
                yield rel, Path(entry.path), st, None

    yield from visit(root, "")


def fingerprint(root: Path, *, max_files: int = MAX_FILES) -> str:
    """Cheap change detector: names, sizes and mtimes only (no file is read)."""
    h = hashlib.sha1()
    for rel, _path, st, _ in walk(root, max_files=max_files):
        h.update(f"{rel}\0{st.st_size if st else 0}\0{st.st_mtime_ns if st else 0}\n".encode())
    return h.hexdigest()


def scan(root: Path, *, max_files: int = MAX_FILES, max_file_bytes: int = MAX_FILE_BYTES) -> Scan:
    out = Scan()
    base = root.resolve()
    for rel, path, st, reason in walk(root, max_files=max_files):
        if reason or st is None:
            out.skipped.append(Skipped(rel, reason or "unreadable"))
            continue
        if st.st_size > max_file_bytes:
            out.skipped.append(Skipped(rel, f"larger than {max_file_bytes} bytes"))
            continue
        try:
            if not path.resolve().is_relative_to(base):
                out.skipped.append(Skipped(rel, "resolves outside the root"))
                continue
            raw = path.read_bytes()
        except OSError as exc:
            out.skipped.append(Skipped(rel, f"unreadable: {exc.__class__.__name__}"))
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            out.skipped.append(Skipped(rel, "not UTF-8"))
            continue
        out.docs.append(make_doc(rel, text, sha=hashlib.sha256(raw).hexdigest()))
    return out


def make_doc(path: str, text: str, *, sha: str | None = None) -> Doc:
    """A `Doc` from a path and its raw text (disk and the in-memory stub both come through here)."""
    clean, stripped = sanitize(text)
    lines = clean.split("\n")
    if lines and lines[-1] == "":
        lines.pop()  # the final newline is not a line
    meta, body_index, problem, notes = _front_matter(lines)
    problems = [problem] if problem else []
    body = lines[body_index:]
    title = _text(meta.get("title")) or _first_heading(body) or Path(path).stem.replace("_", " ").replace("-", " ").strip() or path
    description = _text(meta.get("description"))
    aliases = _aliases(meta.get("aliases"))
    return Doc(
        path=path, title=title, description=description or _first_sentence(body), aliases=aliases, lines=tuple(lines),
        body_start=body_index + 1, sha=sha or hashlib.sha256(text.encode("utf-8")).hexdigest(), size=len(text.encode("utf-8")),
        tokens=estimate_tokens(clean), stripped=stripped, has_front_matter=bool(meta), has_description=bool(description),
        problems=tuple(problems), notes=tuple(notes),
    )


def _text(value: object) -> str:
    return " ".join(str(value).split()) if isinstance(value, str | int | float) and not isinstance(value, bool) else ""


def _aliases(value: object) -> tuple[str, ...]:
    items = value.split(",") if isinstance(value, str) else value if isinstance(value, list) else []
    return tuple(dict.fromkeys(a for a in (_text(i) for i in items) if a))


_KEY_LINE = re.compile(r"^([A-Za-z_][\w-]*):(?:\s+(.*))?$")
_QUOTE_HINT = 'quote values that contain a colon, e.g. description: "Team: calls and notes"'


def _front_matter(lines: list[str]) -> tuple[dict, int, str, list[str]]:
    """`(meta, index of the first body line, problem, notes)`. Strict YAML first; when that fails (usually an unquoted `: ` in a
    value) the block is read as plain `key: value` lines and a note says which line to quote. A block neither way can read is a
    problem (no meta); the file still works."""
    if not lines or lines[0].strip() != "---":
        return {}, 0, "", []
    for i in range(1, min(len(lines), 80)):
        if lines[i].strip() == "---":
            block = lines[1:i]
            try:
                import yaml

                meta = yaml.safe_load("\n".join(block)) or {}
            except Exception as exc:  # noqa: BLE001 - a bad block is a lint finding, not a crash
                if "mapping values" in str(getattr(exc, "problem", "")):  # the unquoted `: ` in a value; any other YAML error is a real one
                    return _lenient(block, i + 1, exc)
                return {}, i + 1, _yaml_problem(block, exc), []
            if not isinstance(meta, dict):
                return {}, i + 1, "front matter is not a mapping", []
            return meta, i + 1, "", []
    return {}, 0, "front matter is not closed with ---", []


def _yaml_problem(block: list[str], exc: Exception) -> str:
    mark = getattr(exc, "problem_mark", None)
    at = (mark.line + 2) if mark is not None else 0
    reason = (getattr(exc, "problem", None) or exc.__class__.__name__).strip()
    key = ""
    if 2 <= at <= len(block) + 1:
        m = _KEY_LINE.match(block[at - 2].strip())
        key = m.group(1) if m else ""
    place = (f"line {at}" + (f", key {key!r}" if key else "")) if at else "an unknown line"
    return f"front matter is not valid YAML at {place}: {reason}. {_QUOTE_HINT}"


def _lenient(block: list[str], body_index: int, exc: Exception) -> tuple[dict, int, str, list[str]]:
    problem = _yaml_problem(block, exc)
    place = problem.split(" at ", 1)[1].split(":", 1)[0]
    reason = (getattr(exc, "problem", None) or exc.__class__.__name__).strip()
    meta: dict = {}
    for line in block:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = _KEY_LINE.match(line.rstrip())
        if not m:  # a continuation / list item / nested value: not plain; report the YAML error
            return {}, body_index, problem, []
        value = (m.group(2) or "").strip()
        if value[:1] == "[" and value[-1:] == "]":
            meta[m.group(1)] = [v.strip().strip("'\"") for v in value[1:-1].split(",") if v.strip()]
        else:
            meta[m.group(1)] = value[1:-1] if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"" else value
    note = f"front matter is not valid YAML at {place} ({reason}); it was read as plain `key: value` lines. {_QUOTE_HINT}"
    return meta, body_index, "", [note]


def _first_heading(body: list[str]) -> str:
    fenced = False
    for line in body:
        if _FENCE.match(line):
            fenced = not fenced
        elif not fenced and line.startswith("# "):
            return " ".join(line[2:].split())
    return ""


def _first_sentence(body: list[str]) -> str:
    fenced = False
    para: list[str] = []
    for line in body:
        if _FENCE.match(line):
            fenced = not fenced
            continue
        stripped = line.strip()
        if fenced or stripped.startswith(("#", "|", "<", "---", "===")):
            if para:
                break
            continue
        if not stripped:
            if para:
                break
            continue
        para.append(stripped)
    text = " ".join(para)
    first = _SENTENCE.split(text, maxsplit=1)[0] if text else ""
    return first[:DESCRIPTION_CHARS]
