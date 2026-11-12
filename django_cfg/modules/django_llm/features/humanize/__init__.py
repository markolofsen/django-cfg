"""Humanize: rewrite text so it stops reading as generated. See ``humanizer.py``."""

from .fields import Humanize, apply as apply_humanize, has_marked_fields
from .guard import Facts, extract_facts, length_ok, missing
from .humanizer import HumanizeResult, humanize
from .metrics import Finding, Report, analyze, detect_lang

__all__ = [
    "Facts", "Finding", "Humanize", "HumanizeResult", "Report", "apply_humanize", "has_marked_fields",
    "analyze", "detect_lang", "extract_facts", "humanize", "length_ok", "missing",
]
