"""Typed exceptions raised by the generator pipeline."""

from __future__ import annotations


class GeneratorError(Exception):
    """Base class for all django_generator errors."""


class SpecLoadError(GeneratorError):
    """drf-spectacular failed to produce a usable schema."""


class PostprocessError(GeneratorError):
    """Global spec failed validation (e.g. operation without tags)."""


class SliceError(GeneratorError):
    """Per-group slicing produced an invalid or empty spec."""


class ToolNotInstalledError(GeneratorError):
    """External CLI not on PATH. Message includes install hint."""


class ToolExecutionError(GeneratorError):
    """External CLI exited non-zero. Includes stderr in message."""


class WriteError(GeneratorError):
    """Filesystem operation (atomic move, mirror, …) failed."""
