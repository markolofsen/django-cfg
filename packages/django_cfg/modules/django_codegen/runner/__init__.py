"""
Generation runner package.

v6.0: Typed GeneratorOptions, ORM support.
v6.1: Rich logging integration.
"""

from django_cfg.modules.django_codegen.runner.logger import (
    GenerationLogger,
    GenerationStats,
    get_generation_logger,
    reset_generation_logger,
)
from django_cfg.modules.django_codegen.runner.main import run, run_with_options

__all__ = [
    "run",
    "run_with_options",
    "GenerationLogger",
    "GenerationStats",
    "get_generation_logger",
    "reset_generation_logger",
]
