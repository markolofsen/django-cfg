"""
monitor_tail — print the last events from the monitor log.

django_monitor stores nothing: events are JSON lines in
<log dir>/djangocfg/monitor.log. This reads that file so an operator can check
that browser errors arrive without docker and grep.

Usage:
    python manage.py monitor_tail                  # last 20 events
    python manage.py monitor_tail -n 50 --frontend # last 50 browser events
"""

from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from django_cfg.management.utils import SafeCommand

FRONTEND_LOGGER = "django_cfg.monitor.frontend"


def parse_event(line: str) -> dict | None:
    """The event dict inside one monitor.log line, for either log format.

    JSON format wraps it: {"ts": .., "logger": .., "message": "<event json>"}.
    Text format prefixes it: "[ts] INFO in <logger> [file:n]: <event json>".
    """
    line = line.strip()
    if not line:
        return None
    try:
        outer = json.loads(line)
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


def read_events(path: Path, count: int, frontend_only: bool = False) -> list[dict]:
    """The last `count` events of the file (oldest first)."""
    keep: deque[dict] = deque(maxlen=max(count, 1))
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            event = parse_event(line)
            if event is None:
                continue
            if frontend_only and event.get("_logger") != FRONTEND_LOGGER:
                continue
            keep.append(event)
    return list(keep)


def format_event(event: dict) -> str:
    source = "frontend" if event.get("_logger") == FRONTEND_LOGGER else "server  "
    parts = [
        str(event.get("_ts", "")),
        source,
        str(event.get("level", "")).upper().ljust(7),
        str(event.get("event_type", "")),
        str(event.get("message", "")).replace("\n", " ")[:200],
    ]
    if event.get("url"):
        parts.append(f"({event['url']})")
    return " ".join(p for p in parts if p)


class Command(SafeCommand):
    command_name = "monitor_tail"
    help = "Print the last events from the django_monitor log (use --frontend for browser events)"

    def add_arguments(self, parser):
        parser.add_argument("-n", type=int, default=20, help="How many events to show (default 20)")
        parser.add_argument("--frontend", action="store_true", help="Only browser events (POST /cfg/monitor/ingest/)")

    def handle(self, *args, **options):
        from django_cfg.core.utils.runtime_paths import resolve_log_dir

        log_dir = resolve_log_dir()
        if log_dir is None:
            self.stdout.write(
                "No event log file: logs go to stdout. Set DJANGO_CFG_LOG_DIR to write "
                "<dir>/djangocfg/monitor.log, or read the container log."
            )
            return
        path = Path(log_dir) / "djangocfg" / "monitor.log"
        if not path.exists():
            self.stdout.write(f"No events yet: {path} does not exist.")
            return

        events = read_events(path, options["n"], options["frontend"])
        if not events:
            kind = "browser events" if options["frontend"] else "events"
            self.stdout.write(f"No {kind} in {path}.")
            return
        for event in events:
            self.stdout.write(format_event(event))
