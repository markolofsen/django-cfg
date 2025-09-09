from enum import Enum


class StatusEnum(str, Enum):
    OPEN = "open"
    WAITING_FOR_USER = "waiting_for_user"
    WAITING_FOR_ADMIN = "waiting_for_admin"
    RESOLVED = "resolved"
    CLOSED = "closed"
