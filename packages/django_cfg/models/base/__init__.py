"""
Base configuration models for django_cfg.

Provides foundation classes for all configuration models.
"""

from .config import BaseConfig, BaseSettings
from .module import BaseCfgAutoModule

__all__ = [
    "BaseConfig",
    "BaseSettings",
    "BaseCfgAutoModule",
]
