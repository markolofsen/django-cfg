"""
Requests serializers for gRPC monitoring API.
"""

from pydantic import BaseModel, Field


class RecentRequestsSerializer(BaseModel):
    """Recent gRPC requests list."""

    requests: list[dict] = Field(description="List of recent requests")
    count: int = Field(description="Number of requests returned")
    total_available: int = Field(description="Total requests available")
    offset: int = Field(default=0, description="Current offset for pagination")
    has_more: bool = Field(default=False, description="Whether more results are available")


__all__ = ["RecentRequestsSerializer"]
