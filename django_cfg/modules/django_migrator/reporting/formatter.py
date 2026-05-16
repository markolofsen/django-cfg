"""Render ``MigrationReport`` as human-readable text.

Kept separate from the dataclasses themselves so multiple sinks (text,
JSON, structured logging) can share the same source-of-truth records.
"""

from __future__ import annotations

from ..types import DbReport, MigrationReport


class TextReportFormatter:
    """Pretty-print a ``MigrationReport`` for the terminal."""

    def __init__(self, *, use_color: bool = True) -> None:
        self._use_color = use_color

    # --- Public ---

    def render(self, report: MigrationReport) -> str:
        chunks: list[str] = ["", "═══ Migration Report ═══"]
        for db in report.db_reports:
            chunks.append(self._render_db(db))
        chunks.append(self._render_summary(report))
        return "\n".join(chunks)

    # --- Per-DB block ---

    def _render_db(self, db: DbReport) -> str:
        lines: list[str] = []
        status = self._db_status_line(db)
        lines.append(f"\n• {db.alias} — {status}")

        if db.aborted:
            lines.append("  ⛔ aborted before migrate")

        if db.drift is not None:
            drift = db.drift
            if drift.has_issues():
                lines.append(
                    f"  Drift: "
                    f"{len(drift.recorded_missing)} recorded-missing, "
                    f"{len(drift.unrecorded_present)} unrecorded-present, "
                    f"{len(drift.half_applied)} half-applied"
                )
                for inc in drift.half_applied[:5]:
                    lines.append(
                        f"    - half_applied      {inc.app_label}.{inc.migration_name}"
                        + (f"  ({inc.detail})" if inc.detail else "")
                    )
                if len(drift.half_applied) > 5:
                    lines.append(f"    … and {len(drift.half_applied) - 5} more")
                for inc in drift.recorded_missing[:5]:
                    lines.append(
                        f"    - recorded_missing  {inc.app_label}.{inc.migration_name}"
                        + (f"  ({inc.detail})" if inc.detail else "")
                    )
                if len(drift.recorded_missing) > 5:
                    lines.append(
                        f"    … and {len(drift.recorded_missing) - 5} more"
                    )
                for inc in drift.unrecorded_present[:5]:
                    lines.append(
                        f"    - unrecorded_present {inc.app_label}.{inc.migration_name}"
                        + (f"  ({inc.detail})" if inc.detail else "")
                    )
                if len(drift.unrecorded_present) > 5:
                    lines.append(
                        f"    … and {len(drift.unrecorded_present) - 5} more"
                    )
            if drift.foreign_tables:
                preview = ", ".join(drift.foreign_tables[:5])
                more = (
                    f" (+{len(drift.foreign_tables) - 5} more)"
                    if len(drift.foreign_tables) > 5 else ""
                )
                lines.append(
                    f"  Foreign tables (not owned by this DB): {preview}{more}"
                )

        if db.repairs_applied:
            lines.append("  Repairs:")
            for r in db.repairs_applied:
                lines.append(f"    ✓ {r}")

        for w in db.warnings:
            lines.append(f"  ⚠️  {w}")
        for e in db.errors:
            lines.append(f"  ❌ {e}")

        if db.migration_executed:
            lines.append(f"  Executed: migrate --database={db.alias}")
        if db.pending_after_migrate:
            lines.append(
                f"  Still pending: {db.pending_after_migrate} migration(s)"
            )

        return "\n".join(lines)

    def _db_status_line(self, db: DbReport) -> str:
        if db.aborted:
            return "ABORTED"
        if db.errors:
            return "FAILED"
        if db.warnings or (db.drift and db.drift.has_issues()):
            return "WARNINGS"
        return "in sync ✅"

    # --- Footer ---

    def _render_summary(self, report: MigrationReport) -> str:
        total = len(report.db_reports)
        clean = sum(1 for d in report.db_reports if d.is_clean)
        if total == 0:
            return "\nNo databases configured."
        if clean == total:
            return f"\n✅ All {total} database(s) in sync."
        return (
            f"\n⚠️  {clean}/{total} database(s) clean. "
            f"See per-DB section above for details."
        )
