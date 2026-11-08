"""
monitor_tail — print the last events from the monitor log.

django_monitor stores nothing: events are JSON lines in
<log dir>/djangocfg/monitor.log (when a log directory is configured; otherwise they
are on stdout, `docker logs`). This reads that file so an operator can check that
browser errors arrive without docker and grep. It reads both line shapes: the flat
record (event fields at the top level of the JSON line) and the older one with the
event as JSON inside "message".

Usage:
    python manage.py monitor_tail                  # last 20 events
    python manage.py monitor_tail -n 50 --frontend # last 50 browser events
    python manage.py monitor_tail --user 42        # what one signed-in user hit
    python manage.py monitor_tail --fingerprint 9f3a1c0b22d4e7aa
    python manage.py monitor_tail --session <session_id>   # one browser tab

Filters combine (all must match) and apply before the -n cut. ``--user`` matches
the primary key as text, so it works for integer and uuid user models alike.

In containers the events are on stdout only (no file), so read them from the pipe:
    docker logs reforms-django 2>&1 | python manage.py monitor_tail --stdin -n 50 --frontend

On stdin only JSON lines whose logger starts with ``django_cfg.monitor`` count;
banners, tracebacks and other loggers are skipped silently. ``--stdin`` (or ``-``)
is explicit: without it the command never reads stdin, so it cannot hang.
"""

from __future__ import annotations

import json
import sys
from collections import deque
from collections.abc import Iterable
from pathlib import Path

from django_cfg.management.utils import SafeCommand

FRONTEND_LOGGER = "django_cfg.monitor.frontend"


def parse_event(line: str) -> dict | None:
    """The event dict inside one monitor.log line, for every log shape.

    Flat JSON (current): {"ts": .., "logger": "django_cfg.monitor.*", "event_type": .., "message": ..}.
    Nested JSON (older): {"ts": .., "logger": .., "message": "<event json>"}.
    Text format prefixes it: "[ts] INFO in <logger> [file:n]: <event json>".
    """
    line = line.strip()
    if not line:
        return None
    try:
        outer = json.loads(line)
        if (
            isinstance(outer, dict)
            and "event_type" in outer
            and str(outer.get("logger", "")).startswith("django_cfg.monitor")
        ):
            flat = {k: v for k, v in outer.items() if k not in ("ts", "logger", "line")}
            flat["_logger"] = outer.get("logger", "")
            flat["_ts"] = outer.get("ts", "")
            return flat
        if isinstance(outer, dict) and isinstance(outer.get("message"), str):
            inner = json.loads(outer["message"])
            if isinstance(inner, dict):
                inner.setdefault("_logger", outer.get("logger", ""))
                inner.setdefault("_ts", outer.get("ts", ""))
                return inner
    except ValueError:
        pass
    start = line.find("{")
    if start < 0:
        return None
    try:
        event = json.loads(line[start:])
    except ValueError:
        return None
    if not isinstance(event, dict):
        return None
    event["_logger"] = FRONTEND_LOGGER if FRONTEND_LOGGER in line[:start] else ""
    event["_ts"] = line[1 : line.find("]")] if line.startswith("[") else ""
    return event


def parse_stream_event(line: str) -> dict | None:
    """Strict variant for piped container logs: only JSON lines of a ``django_cfg.monitor*`` logger.

    Everything else (startup banners, tracebacks, other loggers' JSON, text-format lines)
    is noise and returns None. Reads the flat shape and the nested one (event in "message").
    """
    line = line.strip()
    if not line.startswith("{"):
        return None
    try:
        outer = json.loads(line)
    except ValueError:
        return None
    if not isinstance(outer, dict) or not str(outer.get("logger", "")).startswith("django_cfg.monitor"):
        return None
    return parse_event(line)


def matches(event: dict, *, user: str = "", fingerprint: str = "", session: str = "") -> bool:
    """True when the event passes every filter that is set (exact match, pk compared as text)."""
    if user and str(event.get("user_id") or "") != user:
        return False
    if fingerprint and str(event.get("fingerprint") or "") != fingerprint:
        return False
    if session and str(event.get("session_id") or "") != session:
        return False
    return True


def filter_events(
    lines: Iterable[str],
    count: int,
    frontend_only: bool = False,
    *,
    user: str = "",
    fingerprint: str = "",
    session: str = "",
    strict: bool = False,
) -> list[dict]:
    """The last `count` events among `lines` that pass the filters (oldest first).

    `strict` is for piped container logs: see `parse_stream_event`.
    """
    parse = parse_stream_event if strict else parse_event
    keep: deque[dict] = deque(maxlen=max(count, 1))
    for line in lines:
        event = parse(line)
        if event is None:
            continue
        if frontend_only and event.get("_logger") != FRONTEND_LOGGER:
            continue
        if not matches(event, user=user, fingerprint=fingerprint, session=session):
            continue
        keep.append(event)
    return list(keep)


def read_events(
    path: Path,
    count: int,
    frontend_only: bool = False,
    *,
    user: str = "",
    fingerprint: str = "",
    session: str = "",
) -> list[dict]:
    """The last `count` events of the file that pass the filters (oldest first)."""
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return filter_events(handle, count, frontend_only, user=user, fingerprint=fingerprint, session=session)


def docker_hint() -> str:
    return (
        "In a container the events are on stdout only. Read them from the container log:\n"
        "  docker logs <container> 2>&1 | python manage.py monitor_tail --stdin [-n N] [--frontend]"
    )


def stdin_lines() -> Iterable[str]:
    """Lines of stdin, decoded leniently (a container log can hold any bytes)."""
    buffer = getattr(sys.stdin, "buffer", None)
    if buffer is None:
        return sys.stdin
    return (raw.decode("utf-8", errors="replace") for raw in buffer)


def format_event(event: dict) -> str:
    logger = event.get("_logger")
    source = "frontend" if logger == FRONTEND_LOGGER else "repeat  " if logger == "django_cfg.monitor.repeat" else "server  "
    parts = [
        str(event.get("_ts", "")),
        source,
        str(event.get("level", "")).upper().ljust(7),
        str(event.get("event_type", "")),
        str(event.get("message", "")).replace("\n", " ")[:200],
    ]
    if event.get("url"):
        parts.append(f"({event['url']})")
    if event.get("user_id"):
        parts.append(f"user={event['user_id']}")
    return " ".join(p for p in parts if p)


class Command(SafeCommand):
    command_name = "monitor_tail"
    help = "Print the last events from the django_monitor log (use --frontend for browser events)"

    def add_arguments(self, parser):
        parser.add_argument("-n", type=int, default=20, help="How many events to show (default 20)")
        parser.add_argument("source", nargs="?", default=None, help="'-' reads stdin, same as --stdin")
        parser.add_argument(
            "--stdin",
            action="store_true",
            help="Read events from stdin (docker logs <container> 2>&1 | ... --stdin); never read unless given",
        )
        parser.add_argument("--frontend", action="store_true", help="Only browser events (POST /cfg/monitor/ingest/)")

        parser.add_argument("--user", default="", help="Only events of this user id (the primary key)")
        parser.add_argument("--fingerprint", default="", help="Only events with this fingerprint (hex)")
        parser.add_argument("--session", default="", help="Only events of this browser session id")

    def handle(self, *args, **options):
        n = options["n"]
        user = str(options["user"]).strip()
        fingerprint = str(options["fingerprint"]).strip()
        session = str(options["session"]).strip()
        kind = "browser events" if options["frontend"] else "events"

        source = options.get("source")
        if source not in (None, "-"):
            self.stdout.write(f"Unknown argument {source!r}: use --stdin (or -) to read a pipe.")
            return
        if options["stdin"] or source == "-":
            if sys.stdin is None or sys.stdin.isatty():
                self.stdout.write("--stdin needs a pipe, nothing is piped in.\n" + docker_hint())
                return
            events = filter_events(
                stdin_lines(), n, options["frontend"], user=user, fingerprint=fingerprint, session=session, strict=True
            )
            if not events:
                self.stdout.write(f"No {kind} on stdin (only JSON lines of a django_cfg.monitor* logger count).")
                return
            for event in events:
                self.stdout.write(format_event(event))
            return

        from django_cfg.core.utils.runtime_paths import resolve_monitor_log_dir

        log_dir = resolve_monitor_log_dir()
        if log_dir is None:
            self.stdout.write(
                "No writable event log directory was found, so there is no monitor.log: events go to stdout. "
                "Set logging.dir / DJANGO_CFG_LOG_DIR to write a file.\n" + docker_hint()
            )
            return
        path = Path(log_dir) / "djangocfg" / "monitor.log"
        if not path.exists():
            self.stdout.write(f"No log file: looked for {path}, it does not exist.\n" + docker_hint())
            return

        events = read_events(path, n, options["frontend"], user=user, fingerprint=fingerprint, session=session)
        if not events:
            self.stdout.write(f"No {kind} in {path}.")
            return
        for event in events:
            self.stdout.write(format_event(event))
