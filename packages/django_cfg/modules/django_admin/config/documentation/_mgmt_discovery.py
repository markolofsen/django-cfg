"""Management command discovery utilities."""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import Any, Dict, List, Optional


def discover_management_commands(app_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Discover management commands in app's management/commands directory.

    Returns list of command dicts with name, help text, and arguments.
    """
    if not app_path:
        return []

    commands_dir = app_path / "management" / "commands"
    if not commands_dir.exists() or not commands_dir.is_dir():
        return []

    commands: List[Dict[str, Any]] = []

    for cmd_file in commands_dir.glob("*.py"):
        if cmd_file.stem.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(f"command_{cmd_file.stem}", cmd_file)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore[union-attr]

            if not hasattr(module, "Command"):
                continue

            cmd_class = module.Command
            cmd_instance = cmd_class()
            command_info: Dict[str, Any] = {
                "name": cmd_file.stem,
                "help": getattr(cmd_instance, "help", "No description available"),
                "arguments": [],
            }

            if hasattr(cmd_instance, "add_arguments"):
                parser = argparse.ArgumentParser()
                try:
                    cmd_instance.add_arguments(parser)
                    for action in parser._actions:
                        if action.dest != "help":
                            command_info["arguments"].append({
                                "name": "/".join(action.option_strings) if action.option_strings else action.dest,
                                "help": action.help or "",
                                "required": getattr(action, "required", False),
                                "default": action.default if action.default != argparse.SUPPRESS else None,
                            })
                except Exception:
                    pass

            commands.append(command_info)
        except Exception:
            continue

    commands.sort(key=lambda c: c["name"])
    return commands
