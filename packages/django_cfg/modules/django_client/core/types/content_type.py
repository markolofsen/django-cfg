"""Content type constants for HTTP request/response handling."""
from enum import Enum


class ContentType(str, Enum):
    """Standard HTTP content types used in API generation."""
    JSON = "application/json"
    MULTIPART = "multipart/form-data"
    OCTET_STREAM = "application/octet-stream"
    FORM_URLENCODED = "application/x-www-form-urlencoded"
