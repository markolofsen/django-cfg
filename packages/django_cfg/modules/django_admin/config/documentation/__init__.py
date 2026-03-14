"""Documentation configuration package for Django Admin."""
from ._models import DocumentationSection
from .config import DocumentationConfig

__all__ = ["DocumentationConfig", "DocumentationSection"]
