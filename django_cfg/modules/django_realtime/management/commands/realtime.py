"""`manage.py realtime topics | publish <topic> '<json>' | tail <topic> [...]`.

    realtime topics                          declared patterns, event model, anonymous, history, backend
    realtime publish demo.ping '{}'          validate and append now (no transaction), print the offset
    realtime tail orders:42 demo.ping        print every new entry until Ctrl-C
"""

from __future__ import annotations

import asyncio
import json

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Realtime topics: list them, publish to one, tail new messages"

    def add_arguments(self, parser):
        sub = parser.add_subparsers(dest="action", required=True)
        sub.add_parser("topics", help="List declared topics")
        pub = sub.add_parser("publish", help="Publish one event now")
        pub.add_argument("topic", help="Concrete topic name, e.g. orders:42")
        pub.add_argument("data", nargs="?", default="{}", help="Event as JSON (default {})")
        tail = sub.add_parser("tail", help="Print new messages of topics until interrupted")
        tail.add_argument("topics", nargs="+")
        tail.add_argument("--count", type=int, default=0, help="Stop after this many messages (0: never)")

    def handle(self, *args, **options):
        action = options["action"]
        if action == "topics":
            return self._topics()
        if action == "publish":
            return self._publish(options["topic"], options["data"])
        return self._tail(options["topics"], options["count"])

    def _topics(self):
        from ...backends import get_backend, get_realtime_config
        from ...registry import registry

        config = get_realtime_config()
        self.stdout.write(f"backend: {get_backend().name}   path: {config.path}   enabled: {config.enabled}")
        topics = registry.all()
        if not topics:
            self.stdout.write("no topics declared (add a realtime.py to an installed app)")
            return
        for t in topics:
            flags = "anonymous" if t.anonymous else "users"
            history = t.history or config.default_history
            self.stdout.write(f"{t.pattern:<40} {t.event.__name__:<28} {flags:<10} history={history} group={t.group}")

    def _publish(self, name, raw):
        from ...publishing import publish
        from ...registry import RealtimeError

        try:
            data = json.loads(raw)
        except ValueError as exc:
            raise CommandError(f"data is not JSON: {exc}") from exc
        try:
            offset = publish(name, data, on_commit=False)
        except RealtimeError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(f"{name} {offset}")

    def _tail(self, names, count):
        from ...backends import get_backend
        from ...registry import UnknownTopic, registry

        for name in names:
            try:
                registry.resolve(name)
            except UnknownTopic as exc:
                raise CommandError(str(exc)) from exc
        backend = get_backend()

        wanted = set(names)

        async def run():
            seen = 0
            after = await backend.bus_head()
            try:
                while True:
                    items, gap = await backend.read_bus(after, 5.0)
                    if gap:
                        self.stderr.write("bus trimmed past the reader: some messages were not shown")
                    for item in items:
                        after = item.id
                        entry = item.entry
                        if entry is None or entry.topic not in wanted:
                            continue
                        data = json.dumps(entry.data, ensure_ascii=False)
                        self.stdout.write(f"{entry.topic} {entry.offset} {data} origin_cid={entry.origin_cid}")
                        seen += 1
                        if count and seen >= count:
                            return
            finally:
                await backend.aclose()

        try:
            asyncio.run(run())
        except KeyboardInterrupt:
            pass
