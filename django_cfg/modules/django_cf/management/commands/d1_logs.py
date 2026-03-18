"""
d1_logs — Query D1 logs (server events, gRPC requests, RQ jobs, etc.)

Usage:
    python manage.py d1_logs server_events 50             # last 50 entries
    python manage.py d1_logs server_events --level error --since 1h --limit 50
    python manage.py d1_logs grpc_request_logs --method ConnectTerminal --status error
    python manage.py d1_logs rq_job_events --search "timeout" --since 24h
    python manage.py d1_logs --stats
    python manage.py d1_logs server_events --sql "occurrence_count > 100"
    python manage.py d1_logs server_events --format json
"""

from __future__ import annotations

import json

from django_cfg.management.utils import SafeCommand
from django_cfg.modules.django_cf.services.d1_logs import (
    D1LogQuery,
    D1LogResult,
    D1LogsService,
    KNOWN_TABLES,
)


class Command(SafeCommand):
    command_name = "d1_logs"
    help = "Query D1 logs (server events, gRPC requests, RQ jobs)"

    def add_arguments(self, parser):
        parser.add_argument(
            "table",
            nargs="?",
            choices=KNOWN_TABLES,
            help="D1 table to query",
        )
        parser.add_argument(
            "count",
            nargs="?",
            type=int,
            default=None,
            help="Number of last entries to show (shortcut for --limit)",
        )
        parser.add_argument("--limit", type=int, default=None, help="Max rows (1-500, default 50)")
        parser.add_argument("--level", type=str, help="Filter by level (error, warning, info)")
        parser.add_argument("--since", type=str, help="Time filter: 1h, 24h, 7d, or ISO datetime")
        parser.add_argument("--search", type=str, help="Text search in message/error columns")
        parser.add_argument("--method", type=str, help="gRPC method name filter")
        parser.add_argument("--status", type=str, help="Status filter (pending, success, error)")
        parser.add_argument("--sql", type=str, help="Raw SQL WHERE clause (advanced)")
        parser.add_argument("--format", type=str, default="table", choices=["table", "json", "compact"], dest="output_format", help="Output format")
        parser.add_argument("--stats", action="store_true", help="Show row counts for all tables")

    def handle(self, *args, **options):
        from django_cfg.modules.django_cf import is_ready

        if not is_ready():
            self.stderr.write(self.style.ERROR("Cloudflare D1 is not configured. Check CloudflareConfig."))
            return

        service = D1LogsService()

        if options["stats"]:
            self._handle_stats(service)
            return

        if not options["table"]:
            self.stderr.write(self.style.ERROR("Specify a table or use --stats. Available tables:"))
            for t in KNOWN_TABLES:
                self.stderr.write(f"  {t}")
            return

        # count (positional) > --limit > default 50
        limit = options["count"] or options["limit"] or 50

        query = D1LogQuery(
            table=options["table"],
            limit=limit,
            level=options.get("level"),
            since=options.get("since"),
            search=options.get("search"),
            method=options.get("method"),
            status=options.get("status"),
            sql=options.get("sql"),
            format=options["output_format"],
        )

        result = service.query(query)

        fmt = options["output_format"]
        if fmt == "json":
            self._render_json(result)
        elif fmt == "compact":
            self._render_compact(result)
        else:
            self._render_table(result)

    # ── Stats ─────────────────────────────────────────────────────────────────

    def _handle_stats(self, service: D1LogsService):
        self.stdout.write(self.style.SUCCESS("\nD1 Table Statistics"))
        self.stdout.write("=" * 40)
        stats = service.get_table_stats()
        for table_name, count in stats.items():
            if count < 0:
                label = self.style.WARNING("(not found)")
            elif count == 0:
                label = self.style.NOTICE("0")
            else:
                label = self.style.SUCCESS(str(count))
            self.stdout.write(f"  {table_name:<25} {label}")
        self.stdout.write("")

    # ── Renderers ─────────────────────────────────────────────────────────────

    def _render_json(self, result: D1LogResult):
        output = {
            "table": result.table,
            "total": result.total,
            "duration_ms": result.duration_ms,
            "query_sql": result.query_sql,
            "entries": result.entries,
        }
        self.stdout.write(json.dumps(output, indent=2, ensure_ascii=False, default=str))

    def _render_compact(self, result: D1LogResult):
        self.stdout.write(f"\n{result.table} ({result.total} results, {result.duration_ms}ms)")
        for row in result.entries:
            line = self._compact_line(result.table, row)
            self.stdout.write(line)
        self.stdout.write("")

    def _render_table(self, result: D1LogResult):
        header = f"\nD1 Logs: {result.table} ({result.total} results, {result.duration_ms}ms)"
        self.stdout.write(self.style.SUCCESS(header))
        self.stdout.write("\u2501" * 60)

        if not result.entries:
            self.stdout.write(self.style.WARNING("  (no results)"))
            self.stdout.write("")
            return

        for row in result.entries:
            self._render_row(result.table, row)

        self.stdout.write("")

    def _render_row(self, table: str, row: dict):
        """Render a single row in human-readable format, adapted per table."""
        if table == "server_events":
            level = row.get("level", "?")
            count = row.get("occurrence_count", 1)
            ts = _short_ts(row.get("last_seen", ""))
            event_type = row.get("event_type", "")
            msg = _truncate(row.get("message", ""), 120)
            resolved = " [resolved]" if str(row.get("is_resolved")) == "1" else ""
            self.stdout.write(f"[{level}] x{count} | {ts} | {event_type}{resolved}")
            self.stdout.write(f"  {msg}")
            self.stdout.write("")

        elif table == "frontend_events":
            level = row.get("level", "?")
            count = row.get("occurrence_count", 1)
            ts = _short_ts(row.get("last_seen", ""))
            event_type = row.get("event_type", "")
            msg = _truncate(row.get("message", ""), 120)
            self.stdout.write(f"[{level}] x{count} | {ts} | {event_type}")
            self.stdout.write(f"  {msg}")
            if row.get("url"):
                self.stdout.write(f"  url: {row['url']}")
            self.stdout.write("")

        elif table == "grpc_request_logs":
            status = row.get("status", "?")
            method = row.get("full_method", row.get("method_name", "?"))
            ts = _short_ts(row.get("created_at", ""))
            duration = row.get("duration_ms", "?")
            err = row.get("error_message", "")
            style = self.style.ERROR if status == "error" else self.style.SUCCESS
            self.stdout.write(style(f"[{status}] {method} | {ts} | {duration}ms"))
            if err:
                self.stdout.write(f"  {_truncate(err, 120)}")
            self.stdout.write("")

        elif table == "grpc_server_status":
            status = row.get("status", "?")
            host = row.get("hostname", "?")
            hb = _short_ts(row.get("last_heartbeat", ""))
            port = row.get("port", "?")
            self.stdout.write(f"[{status}] {host}:{port} | heartbeat: {hb}")
            if row.get("error_message"):
                self.stdout.write(f"  {row['error_message']}")
            self.stdout.write("")

        elif table == "rq_job_events":
            status = row.get("status", "?")
            func = row.get("func_name", "?")
            ts = _short_ts(row.get("created_at", ""))
            queue = row.get("queue", "?")
            duration = row.get("duration_seconds")
            dur_str = f" | {duration}s" if duration else ""
            style = self.style.ERROR if status == "failed" else self.style.SUCCESS
            self.stdout.write(style(f"[{status}] {func} | {queue} | {ts}{dur_str}"))
            if row.get("error_message"):
                self.stdout.write(f"  {_truncate(row['error_message'], 120)}")
            self.stdout.write("")

        elif table == "rq_worker_heartbeats":
            state = row.get("state", "?")
            name = row.get("worker_name", "?")
            hb = _short_ts(row.get("heartbeat_at", ""))
            ok = row.get("successful_job_count", 0)
            fail = row.get("failed_job_count", 0)
            self.stdout.write(f"[{state}] {name} | {hb} | ok:{ok} fail:{fail}")
            self.stdout.write("")

        else:
            # Generic fallback for any table
            parts = [f"{k}={_truncate(str(v), 40)}" for k, v in list(row.items())[:8]]
            self.stdout.write("  " + " | ".join(parts))
            self.stdout.write("")

    def _compact_line(self, table: str, row: dict) -> str:
        """One-line compact representation per row."""
        if table == "server_events":
            return f"  [{row.get('level', '?')}] x{row.get('occurrence_count', 1)} {_short_ts(row.get('last_seen', ''))} {_truncate(row.get('message', ''), 80)}"
        elif table == "grpc_request_logs":
            return f"  [{row.get('status', '?')}] {row.get('full_method', '?')} {_short_ts(row.get('created_at', ''))} {row.get('duration_ms', '?')}ms"
        elif table == "rq_job_events":
            return f"  [{row.get('status', '?')}] {row.get('func_name', '?')} {_short_ts(row.get('created_at', ''))}"
        else:
            vals = [f"{k}={_truncate(str(v), 30)}" for k, v in list(row.items())[:6]]
            return "  " + " | ".join(vals)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _short_ts(ts: str) -> str:
    """Shorten ISO timestamp to 'YYYY-MM-DD HH:MM'."""
    if not ts:
        return "?"
    return ts[:16].replace("T", " ")


def _truncate(s: str, maxlen: int = 120) -> str:
    """Truncate string with ellipsis."""
    if not s:
        return ""
    s = s.replace("\n", " ").strip()
    if len(s) > maxlen:
        return s[:maxlen - 3] + "..."
    return s
