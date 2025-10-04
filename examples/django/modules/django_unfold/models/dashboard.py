"""
Dashboard Components Models for Unfold

Pydantic models for dashboard components like stat cards, health items, etc.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict, computed_field


class StatCard(BaseModel):
    """Dashboard statistics card model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., description="Card title")
    value: str = Field(..., description="Main value to display")
    icon: str = Field(..., description="Material icon name")
    change: Optional[str] = Field(None, description="Change indicator (e.g., '+12%')")
    change_type: Literal["positive", "negative", "neutral"] = Field(default="neutral", description="Change type")
    description: Optional[str] = Field(None, description="Additional description")
    color: str = Field("primary", description="Card color theme")
    
    @computed_field
    @property
    def css_classes(self) -> Dict[str, str]:
        """Get CSS classes for different states."""
        return {
            "positive": "text-emerald-600 bg-emerald-100 dark:bg-emerald-900/20 dark:text-emerald-400",
            "negative": "text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400",
            "neutral": "text-slate-600 bg-slate-100 dark:bg-slate-700 dark:text-slate-400"
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Unfold dashboard widgets."""
        return {
            "title": self.title,
            "value_template": self.value,
            "icon": self.icon,
            "color": self.color,
            "change": self.change,
            "change_type": self.change_type,
            "description": self.description,
        }


class SystemHealthItem(BaseModel):
    """System health status item."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    component: str = Field(..., description="Component name")
    status: Literal["healthy", "warning", "error", "unknown"] = Field(..., description="Health status")
    description: str = Field(..., description="Status description")
    last_check: str = Field(..., description="Last check time")
    health_percentage: Optional[int] = Field(None, description="Health percentage (0-100)")
    
    @computed_field
    @property
    def icon(self) -> str:
        """Get icon based on component type."""
        icons = {
            "database": "storage",
            "cache": "memory", 
            "queue": "queue",
            "storage": "folder",
            "api": "api",
        }
        return icons.get(self.component.lower(), "info")
    
    @computed_field
    @property
    def status_icon(self) -> str:
        """Get status icon."""
        icons = {
            "healthy": "check_circle",
            "warning": "warning", 
            "error": "error",
            "unknown": "help"
        }
        return icons.get(self.status, "help")


class QuickAction(BaseModel):
    """Quick action button model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Action description")
    icon: str = Field(..., description="Material icon name")
    link: str = Field(..., description="Action URL or URL name")
    color: Literal["primary", "success", "warning", "danger", "secondary"] = Field(default="primary", description="Button color theme")
    category: str = Field("general", description="Action category (admin, user, system)")

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


class DashboardWidget(BaseModel):
    """Dashboard widget configuration."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    title: str = Field(..., description="Widget title")
    template: Optional[str] = Field(None, description="Custom template path")
    callback: Optional[str] = Field(None, description="Callback function path")
    width: int = Field(12, description="Widget width (1-12)")
    order: int = Field(0, description="Widget order")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Unfold dashboard widgets."""
        return {
            "title": self.title,
            "template": self.template,
            "callback": self.callback,
            "width": self.width,
            "order": self.order,
        }


class StatsCardsWidget(BaseModel):
    """Stats cards widget for dashboard."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    type: Literal["stats_cards"] = Field(default="stats_cards", description="Widget type")
    title: str = Field(..., description="Widget title")
    cards: List[StatCard] = Field(default_factory=list, description="Statistics cards")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Unfold dashboard widgets."""
        return {
            "type": self.type,
            "title": self.title,
            "cards": [card.to_dict() for card in self.cards],
        }


class ChartDataset(BaseModel):
    """Chart dataset for dashboard charts."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    label: str = Field(..., description="Dataset label")
    data: List[int] = Field(default_factory=list, description="Data points")
    backgroundColor: str = Field(..., description="Background color")
    borderColor: str = Field(..., description="Border color")
    tension: float = Field(0.4, description="Line tension")


class ChartData(BaseModel):
    """Chart data structure."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    labels: List[str] = Field(default_factory=list, description="Chart labels")
    datasets: List[ChartDataset] = Field(default_factory=list, description="Chart datasets")


class DashboardData(BaseModel):
    """Main dashboard data container."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Statistics cards
    stat_cards: List[StatCard] = Field(default_factory=list, description="Dashboard statistics cards")
    
    # System health
    system_health: List[SystemHealthItem] = Field(default_factory=list, description="System health items")
    
    # Quick actions
    quick_actions: List[QuickAction] = Field(default_factory=list, description="Quick action buttons")
    
    # Additional data
    last_updated: str = Field(..., description="Last update timestamp")
    environment: str = Field("development", description="Current environment")
    
    @computed_field
    @property
    def total_users(self) -> int:
        """Get total users from stat cards."""
        for card in self.stat_cards:
            if "user" in card.title.lower():
                try:
                    return int(card.value.replace(",", ""))
                except (ValueError, AttributeError):
                    pass
        return 0
