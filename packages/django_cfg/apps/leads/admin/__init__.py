"""
Admin configuration for Leads app using Django-CFG admin system.
"""

from .leads_admin import LeadAdmin
from .resources import LeadResource

__all__ = [
    'LeadAdmin',
    'LeadResource',
]
