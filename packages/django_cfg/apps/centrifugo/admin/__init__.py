"""
Django Admin for Centrifugo models.

Uses PydanticAdmin with declarative configuration.
"""

from .centrifugo_log import CentrifugoLogAdmin
from .config import centrifugolog_config

__all__ = [
    "centrifugolog_config",
    "CentrifugoLogAdmin",
]
