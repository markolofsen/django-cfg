"""Shared bits of the kb_* commands."""

from __future__ import annotations

from pathlib import Path

from django.core.management.base import CommandError

from django_cfg.modules.django_llm.agent.chat.knowledge import DiskKnowledgeBase
from django_cfg.modules.django_llm.agent.chat.knowledge.settings import knowledge_dir


def add_dir_argument(parser) -> None:
    parser.add_argument("--dir", help="the knowledge folder (default: CHAT__KNOWLEDGE_DIR, else <BASE_DIR>/knowledge)")


def open_base(options) -> DiskKnowledgeBase:
    root = Path(options["dir"]).expanduser() if options.get("dir") else knowledge_dir()
    if root is None or not Path(root).is_dir():
        raise CommandError("no knowledge folder: pass --dir or set CHAT__KNOWLEDGE_DIR (default <BASE_DIR>/knowledge)")
    return DiskKnowledgeBase(root, refresh_s=0)
