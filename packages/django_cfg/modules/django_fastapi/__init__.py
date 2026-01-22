"""
Django FastAPI ORM Generator Module.

Generates FastAPI-ready SQLModel/Pydantic code from Django models.

Usage:
    python manage.py generate_fastapi [apps...]

Example:
    python manage.py generate_fastapi users products --output-dir=fastapi/
"""

from .config import FastAPIConfig
from .core.orchestrator import FastAPIOrchestrator

__all__ = [
    "FastAPIConfig",
    "FastAPIOrchestrator",
]
