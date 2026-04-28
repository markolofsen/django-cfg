"""Barrel index renderer for hooks."""

from __future__ import annotations


def render_flat_index(entries: list[tuple[str, str]]) -> str:
    """Single barrel for all hooks in the group's `hooks/` dir.

    `entries`: list of (filename, exported_hook_name).
    """
    lines = [
        "// AUTO-GENERATED — barrel for hooks.",
        "// DO NOT EDIT.",
        "",
    ]
    for filename, hook in sorted(entries):
        stem = filename.removesuffix(".ts")
        if stem == "index":
            continue
        lines.append(f'export {{ {hook} }} from "./{stem}";')
    lines.append("")
    return "\n".join(lines)
