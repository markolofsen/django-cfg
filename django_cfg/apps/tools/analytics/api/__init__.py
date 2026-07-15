"""Analytics API layer. Views stay thin; logic lives in ../services/."""

from .views import CollectView

__all__ = ["CollectView"]
