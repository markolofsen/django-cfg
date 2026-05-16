"""Repair primitives and orchestration."""

from .engine import RepairEngine
from .fake_detector import (
    OpDetector,
    detector_count,
    matches_any_detector,
    register_fake_detector,
    reset_detectors_for_tests,
)
from .primitives import fake_apply, fake_rewind

__all__ = [
    "RepairEngine",
    "OpDetector",
    "register_fake_detector",
    "matches_any_detector",
    "detector_count",
    "reset_detectors_for_tests",
    "fake_apply",
    "fake_rewind",
]
