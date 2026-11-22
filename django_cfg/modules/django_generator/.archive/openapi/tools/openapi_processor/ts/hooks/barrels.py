"""Barrel index renderers for hooks."""

from __future__ import annotations


def render_flat_index(entries: list[tuple[str, str]]) -> str:
    """`entries`: list of (filename, exported_hook_name) — flat hooks dir."""
    lines = [
        "// AUTO-GENERATED — barrel for all hooks.",
        "// DO NOT EDIT.",
        "",
    ]
    for filename, hook in sorted(entries):
        stem = filename.removesuffix(".ts")
        lines.append(f'export {{ {hook} }} from "./{stem}";')
    lines.append("")
    return "\n".join(lines)
