"""django_monitor services — business logic behind the API views."""

from .ingest import ingest_frontend_events

__all__ = ["ingest_frontend_events"]
