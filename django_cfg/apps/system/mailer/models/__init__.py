"""Email models: the copy a project sends, and the record of sending it."""

from .content import EmailContent
from .log import EmailLog

__all__ = [
    "EmailContent",
    "EmailLog",
]
