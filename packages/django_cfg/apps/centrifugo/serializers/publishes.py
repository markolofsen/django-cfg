"""
Publishes serializers for Centrifugo monitoring API.
"""

from pydantic import BaseModel, Field


class RecentPublishesSerializer(BaseModel):
    """Recent publishes list."""

    publishes: list[dict] = Field(description="List of recent publishes")
    count: int = Field(description="Number of publishes returned")
    total_available: int = Field(description="Total publishes available")
    offset: int = Field(default=0, description="Current offset for pagination")
    has_more: bool = Field(default=False, description="Whether more results are available")


__all__ = ["RecentPublishesSerializer"]
