"""
Dependency injection classes for Django Orchestrator.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, TYPE_CHECKING
from django.http import HttpRequest

# Re-export RunContext from pydantic_ai for convenience
from pydantic_ai import RunContext

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

__all__ = ["DjangoDeps", "ContentDeps", "RunContext"]


@dataclass
class DjangoDeps:
    """Standard Django dependencies for agent execution."""
    
    user: "AbstractUser"
    request: Optional[HttpRequest] = None
    session_data: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    async def from_request(cls, request: HttpRequest) -> 'DjangoDeps':
        """Create dependencies from Django request."""
        return cls(
            user=request.user,
            request=request,
            session_data=dict(request.session) if request.session else {}
        )
    
    @classmethod
    async def from_user_id(cls, user_id: int) -> 'DjangoDeps':
        """Create dependencies from user ID."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = await User.objects.aget(id=user_id)
        return cls(user=user)
    
    @classmethod
    async def from_user(cls, user: "AbstractUser") -> 'DjangoDeps':
        """Create dependencies from user instance."""
        return cls(user=user)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'user_id': self.user.id,
            'username': self.user.username,
            'session_data': self.session_data,
            'has_request': self.request is not None
        }


@dataclass
class ContentDeps(DjangoDeps):
    """Content-specific dependencies."""
    
    content_id: Optional[int] = None
    content_type: str = "article"
    target_audience: str = "general"
    
    async def get_content(self):
        """Get content object if content_id is provided."""
        if not self.content_id:
            return None
        
        # Import here to avoid circular imports
        from django.apps import apps
        
        try:
            Content = apps.get_model('your_app', 'Content')  # Adjust app name
            return await Content.objects.aget(id=self.content_id)
        except Exception:
            return None


@dataclass
class DataProcessingDeps(DjangoDeps):
    """Dependencies for data processing agents."""
    
    dataset_id: Optional[int] = None
    processing_options: Dict[str, Any] = field(default_factory=dict)
    batch_size: int = 100
    
    async def get_dataset(self):
        """Get dataset object if dataset_id is provided."""
        if not self.dataset_id:
            return None
        
        # Import here to avoid circular imports
        from django.apps import apps
        
        try:
            Dataset = apps.get_model('your_app', 'Dataset')  # Adjust app name
            return await Dataset.objects.aget(id=self.dataset_id)
        except Exception:
            return None


@dataclass
class BusinessLogicDeps(DjangoDeps):
    """Dependencies for business logic agents."""
    
    business_context: Dict[str, Any] = field(default_factory=dict)
    rules_version: str = "latest"
    organization_id: Optional[int] = None
    
    async def get_organization(self):
        """Get organization object if organization_id is provided."""
        if not self.organization_id:
            return None
        
        # Import here to avoid circular imports
        from django.apps import apps
        
        try:
            Organization = apps.get_model('your_app', 'Organization')  # Adjust app name
            return await Organization.objects.aget(id=self.organization_id)
        except Exception:
            return None


@dataclass
class IntegrationDeps(DjangoDeps):
    """Dependencies for external integration agents."""
    
    api_credentials: Dict[str, str] = field(default_factory=dict)
    service_config: Dict[str, Any] = field(default_factory=dict)
    rate_limit_key: Optional[str] = None
    
    def get_api_key(self, service_name: str) -> Optional[str]:
        """Get API key for specific service."""
        return self.api_credentials.get(f"{service_name}_api_key")
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Get configuration for specific service."""
        return self.service_config.get(service_name, {})


@dataclass
class TestDeps:
    """Simple dependencies for testing."""
    
    user_id: int
    test_data: Dict[str, Any] = field(default_factory=dict)
    mock_responses: Dict[str, Any] = field(default_factory=dict)
    
    def get_mock_response(self, key: str) -> Any:
        """Get mock response for testing."""
        return self.mock_responses.get(key)
