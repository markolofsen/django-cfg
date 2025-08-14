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
    
    @computed_field
    @property
    def css_classes(self) -> Dict[str, str]:
        """Get CSS classes for different states."""
        return {
            "positive": "text-emerald-600 bg-emerald-100 dark:bg-emerald-900/20 dark:text-emerald-400",
            "negative": "text-red-600 bg-red-100 dark:bg-red-900/20 dark:text-red-400",
            "neutral": "text-slate-600 bg-slate-100 dark:bg-slate-700 dark:text-slate-400"
        }


class SystemHealthItem(BaseModel):
    """System health status item."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    component: str = Field(..., description="Component name")
    status: Literal["healthy", "warning", "error", "unknown"] = Field(..., description="Health status")
    description: Optional[str] = Field(None, description="Status description")
    last_check: Optional[str] = Field(None, description="Last check time")
    
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
    description: Optional[str] = Field(None, description="Action description")
    icon: str = Field(..., description="Material icon name")
    link: str = Field(..., description="Action URL")
    color: Literal["primary", "success", "warning", "danger", "secondary"] = Field(default="primary", description="Button color theme")
    category: Optional[str] = Field(None, description="Action category (admin, user, system)")


class DashboardData(BaseModel):
    """Complete dashboard data model."""
    model_config = ConfigDict(validate_assignment=True, extra="forbid")
    
    # Statistics cards
    stat_cards: List[StatCard] = Field(default_factory=list, description="Dashboard statistics cards")
    
    # System health
    system_health: List[SystemHealthItem] = Field(default_factory=list, description="System health items")
    
    # Quick actions
    quick_actions: List[QuickAction] = Field(default_factory=list, description="Quick action buttons")
    
    # Additional data
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    environment: Optional[str] = Field(None, description="Current environment")
    
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
