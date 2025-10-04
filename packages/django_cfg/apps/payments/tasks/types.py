"""
Pydantic types for background tasks.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class TaskResult(BaseModel):
    """Base result type for all background tasks."""
    model_config = ConfigDict(validate_assignment=True)
    
    status: str = Field(description="Task execution status")
    message: Optional[str] = Field(None, description="Human-readable message")
    error: Optional[str] = Field(None, description="Error message if failed")
    processing_time_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Task completion timestamp")


class UsageUpdateRequest(BaseModel):
    """Request for updating usage counters."""
    model_config = ConfigDict(validate_assignment=True)
    
    resource_id: str = Field(description="Resource ID (API key or subscription)")
    increment: int = Field(default=1, description="Amount to increment")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UsageUpdateResult(TaskResult):
    """Result of usage update operation."""
    
    resource_id: str = Field(description="Updated resource ID")
    total_requests: Optional[int] = Field(None, description="Total requests after update")
    increment: int = Field(description="Amount incremented")
    user_id: Optional[int] = Field(None, description="Associated user ID")


class BatchUpdateRequest(BaseModel):
    """Request for batch usage updates."""
    model_config = ConfigDict(validate_assignment=True)
    
    api_key_updates: List[UsageUpdateRequest] = Field(default_factory=list, description="API key updates")
    subscription_updates: List[UsageUpdateRequest] = Field(default_factory=list, description="Subscription updates")
    force_flush: bool = Field(default=False, description="Force immediate processing")


class BatchUpdateResult(TaskResult):
    """Result of batch update operation."""
    
    api_keys_updated: int = Field(default=0, description="Number of API keys updated")
    subscriptions_updated: int = Field(default=0, description="Number of subscriptions updated")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Processing errors")
    total_items: int = Field(description="Total items processed")


class CleanupResult(TaskResult):
    """Result of cleanup operation."""
    
    cleaned_entries: int = Field(default=0, description="Number of entries cleaned")
    cleanup_type: str = Field(description="Type of cleanup performed")
    cutoff_date: Optional[datetime] = Field(None, description="Cleanup cutoff date")


class CacheStats(BaseModel):
    """Cache statistics."""
    model_config = ConfigDict(validate_assignment=True)
    
    total_keys: int = Field(description="Total cache keys")
    expired_keys: int = Field(description="Expired cache keys")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    hit_rate: Optional[float] = Field(None, description="Cache hit rate percentage")
