"""Static + templated TS sources emitted by the wrapper generator."""

from .storage import STORAGE_TS
from .errors import ERRORS_TS
from .logger import LOGGER_TS
from .validation_events import VALIDATION_EVENTS_TS
from .api import (
    GroupSpec,
    render_group_api_ts,
    render_group_index_ts,
    render_target_index_ts,
)

__all__ = [
    "STORAGE_TS",
    "ERRORS_TS",
    "LOGGER_TS",
    "VALIDATION_EVENTS_TS",
    "GroupSpec",
    "render_group_api_ts",
    "render_group_index_ts",
    "render_target_index_ts",
]
