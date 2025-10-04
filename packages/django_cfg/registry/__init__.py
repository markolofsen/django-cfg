"""
Django-CFG Import Registry

Organized import system for django-cfg components.
"""

from .core import CORE_REGISTRY
from .services import SERVICES_REGISTRY  
from .third_party import THIRD_PARTY_REGISTRY
from .modules import MODULES_REGISTRY
from .exceptions import EXCEPTIONS_REGISTRY

# Combine all registries
DJANGO_CFG_REGISTRY = {
    **CORE_REGISTRY,
    **SERVICES_REGISTRY,
    **THIRD_PARTY_REGISTRY,
    **MODULES_REGISTRY,
    **EXCEPTIONS_REGISTRY,
}

# Export all available names
__all__ = list(DJANGO_CFG_REGISTRY.keys())
