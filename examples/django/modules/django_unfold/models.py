"""
Dashboard Pydantic Models for Django CFG Unfold Module

All dashboard data models with type safety.
Following CRITICAL_REQUIREMENTS.md - NO raw dicts, ALL type-safe.
"""

from typing import List, Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from django.urls import reverse


class StatCard(BaseModel):
    """Statistics card model for dashboard."""

    title: str = Field(..., description="Card title")
    value: str = Field(..., description="Main value to display")
    icon: str = Field(..., description="Material icon name")
    change: Optional[str] = Field(None, description="Change indicator (e.g., '+5', '-2%')")
    change_type: str = Field("neutral", description="Change type: positive, negative, neutral")
    description: Optional[str] = Field(None, description="Additional description")
    color: str = Field("primary", description="Card color theme")


class SystemHealthItem(BaseModel):
    """System health status item."""

    component: str = Field(..., description="Component name (database, cache, etc.)")
    status: str = Field(..., description="Status: healthy, warning, error, unknown")
    description: str = Field(..., description="Status description")
    last_check: str = Field(..., description="Last check time")
    health_percentage: Optional[int] = Field(None, description="Health percentage (0-100)")


class QuickAction(BaseModel):
    """Quick action button for dashboard."""

    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Action description")
    icon: str = Field(..., description="Material icon name")
    link: str = Field(..., description="Action URL or URL name")
    color: str = Field("primary", description="Button color")
    category: str = Field("general", description="Action category")

    def get_resolved_url(self) -> str:
        """
        Resolve URL name to full URL if needed.

        Returns:
            Full URL string - either the original link if it's already a URL,
            or the resolved URL if it's a URL name.
        """
        # If link starts with '/' or 'http', it's already a full URL
        if self.link.startswith(("/", "http")):
            return self.link

        # Try to resolve as URL name
        try:
            from django.urls import reverse
            from django.urls.exceptions import NoReverseMatch
            return reverse(self.link)
        except (NoReverseMatch, ImportError, Exception):
            # If reverse fails, return the original link
            return self.link

    def model_dump(self, **kwargs) -> dict:
        """Override model_dump to include resolved URL."""
        data = super().model_dump(**kwargs)
        # Replace link with resolved URL
        data["link"] = self.get_resolved_url()
        return data


class DashboardData(BaseModel):
    """Main dashboard data container."""

    stat_cards: List[StatCard] = Field(default_factory=list, description="Statistics cards")
    system_health: List[SystemHealthItem] = Field(default_factory=list, description="System health items")
    quick_actions: List[QuickAction] = Field(default_factory=list, description="Quick action buttons")
    last_updated: str = Field(..., description="Last update timestamp")
    environment: str = Field("development", description="Current environment")


class ChartDataset(BaseModel):
    """Chart dataset for dashboard charts."""

    label: str = Field(..., description="Dataset label")
    data: List[int] = Field(default_factory=list, description="Data points")
    backgroundColor: str = Field(..., description="Background color")
    borderColor: str = Field(..., description="Border color")
    tension: float = Field(0.4, description="Line tension")


class ChartData(BaseModel):
    """Chart data structure."""

    labels: List[str] = Field(default_factory=list, description="Chart labels")
    datasets: List[ChartDataset] = Field(default_factory=list, description="Chart datasets")
