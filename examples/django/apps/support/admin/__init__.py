"""
Support admin interfaces using Django-CFG admin system.

Refactored admin interfaces with Material Icons and optimized queries.
"""

from .support_admin import TicketAdmin, MessageAdmin
from .filters import TicketUserEmailFilter, TicketUserNameFilter, MessageSenderEmailFilter
from .resources import TicketResource, MessageResource

__all__ = [
    'TicketAdmin',
    'MessageAdmin',
    'TicketUserEmailFilter',
    'TicketUserNameFilter',
    'MessageSenderEmailFilter',
    'TicketResource',
    'MessageResource',
]
