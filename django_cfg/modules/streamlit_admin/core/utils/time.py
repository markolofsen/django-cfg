"""Time formatting helpers for Streamlit pages."""

from __future__ import annotations

from datetime import datetime, timezone


def time_ago(ts: str | None) -> str:
    """Convert ISO timestamp string to human-readable 'X ago' string."""
    if not ts:
        return ""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        diff = datetime.now(timezone.utc) - dt
        total = int(diff.total_seconds())
        if total < 60:
            return f"{total}s ago"
        if total < 3600:
            return f"{total // 60}m ago"
        if total < 86400:
            return f"{total // 3600}h ago"
        days = total // 86400
        if days < 30:
            return f"{days}d ago"
        return dt.strftime("%b %d")
    except Exception:
        return ts[:16] if len(ts) > 16 else ts


__all__ = ["time_ago"]
