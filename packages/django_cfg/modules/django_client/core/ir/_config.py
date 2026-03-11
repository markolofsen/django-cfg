"""Shared Pydantic model configuration for IR models."""
from pydantic import ConfigDict

IR_MODEL_CONFIG = ConfigDict(
    validate_assignment=True,
    extra="forbid",
    frozen=False,
    validate_default=True,
    str_strip_whitespace=True,
)
