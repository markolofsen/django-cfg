"""
Key management for Django-CFG encryption.

Provides key derivation and management utilities.
"""

from .derivation import (
    derive_key_from_components,
    derive_key_pbkdf2,
    generate_salt,
)
from .manager import KeyManager, get_key_manager, reset_key_manager

__all__ = [
    # Derivation
    "derive_key_pbkdf2",
    "derive_key_from_components",
    "generate_salt",
    # Manager
    "KeyManager",
    "get_key_manager",
    "reset_key_manager",
]
