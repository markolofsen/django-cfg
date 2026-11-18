"""
log_noise - which log lines repeat the most.

Reads log lines from stdin (a pipe) and groups them by normalised message (ids, numbers,
hashes replaced), so ten thousand "Fetched 3 rows for <uuid>" lines read as one group. It
prints counts and a masked sample only; it never prints the raw line, so no ids or personal
data leave through it. Use it to decide what to collapse, quiet or fix at the call site.

    docker logs carapis-rq-worker --since 1h 2>&1 | python manage.py log_noise --stdin
    docker logs carapis-django 2>&1 | python manage.py log_noise --stdin -n 30

JSON lines (django-cfg's format) group by logger + level + message; uvicorn access lines by
method + path; other lines by their text. ``--stdin`` is explicit: without it nothing is read.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from typing import Iterable

from django.core.management.base import BaseCommand

_NOISE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"|\b0x[0-9a-f]+\b|\b[0-9a-f]{12,}\b|[\w.+-]+@[\w-]+\.[\w.]+|\d+",
    re.IGNORECASE,
)
_ACCESS = re.compile(r'"([A-Z]+) (\S+?)(?:\?\S*)? HTTP/[\d.]+" (\d{3})')


def normalise(text: str) -> str:
    return _NOISE.sub("#", text)[:200]


def group_key(line: str) -> tuple[str, str]:
    """(level, normalised text) for one raw line."""
    line = line.strip()
    if line.startswith("{"):
        try:
            d = json.loads(line)
            return str(d.get("level", "?")), f'{d.get("logger", "?")}: {normalise(str(d.get("message", "")))}'
        except ValueError:
            pass
    m = _ACCESS.search(line)
    if m:
        return "ACCESS", f"{m.group(1)} {normalise(m.group(2))} -> {m.group(3)}"
    return "TEXT", normalise(line)


def top_repeats(lines: Iterable[str], n: int = 20) -> tuple[int, int, list[tuple[int, str, str]]]:
    counts: Counter = Counter()
    total = 0
    for raw in lines:
        if not raw.strip():
            continue
        total += 1
        counts[group_key(raw)] += 1
    return total, len(counts), [(c, k[0], k[1]) for k, c in counts.most_common(n)]


class Command(BaseCommand):
    help = "Group piped log lines by normalised message and print the top repeats (masked)."

    def add_arguments(self, parser):
        parser.add_argument("--stdin", action="store_true", help="Read log lines from stdin")
        parser.add_argument("-n", type=int, default=20, help="Groups to print (default 20)")

    def handle(self, *args, **options):
        if not options["stdin"]:
            self.stderr.write("Pipe logs in and pass --stdin, e.g. docker logs <c> 2>&1 | manage.py log_noise --stdin")
            return
        total, groups, top = top_repeats(sys.stdin, options["n"])
        folded = sum(c - 1 for c, _, _ in top)
        self.stdout.write(f"{total} lines, {groups} distinct groups; top {len(top)} groups hold {sum(c for c, _, _ in top)} lines ({folded} repeats)")
        for count, level, text in top:
            self.stdout.write(f"{count:>7}  {level:<8} {text}")
