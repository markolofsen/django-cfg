"""
API Configuration Model

Django REST Framework and API settings with Pydantic 2.
"""

from typing import Dict, Any, List
from pydantic import Field, field_validator
from .base import BaseConfig


class APIConfig(BaseConfig):
    """
    🌐 API Configuration - REST Framework and API settings
    
    Configures Django REST Framework, pagination, throttling,
    and API documentation settings.
    """
    
    # Pagination settings
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Default API pagination page size"
    )
    
    max_page_size: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum API pagination page size"
    )
    
    # Throttling settings
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable API rate limiting"
    )
    
    rate_limit_anon: str = Field(
        default="100/hour",
        description="Rate limit for anonymous users"
    )
    
    rate_limit_user: str = Field(
        default="1000/hour", 
        description="Rate limit for authenticated users"
    )
    
    # Documentation settings
    docs_enabled: bool = Field(
        default=True,
        description="Enable API documentation"
    )
    
    docs_title: str = Field(
        default="API Documentation",
        description="API documentation title"
    )
    
    docs_version: str = Field(
        default="v1",
        description="API version"
    )
    
    # CORS settings for API
    api_cors_origins: List[str] = Field(
        default_factory=list,
        description="CORS origins specifically for API endpoints"
    )
    
    @field_validator('page_size', 'max_page_size')
    @classmethod
    def validate_page_sizes(cls, v: int) -> int:
        """Validate pagination sizes."""
        if v <= 0:
            raise ValueError("Page size must be positive")
        return v
    
    @field_validator('rate_limit_anon', 'rate_limit_user')
    @classmethod
    def validate_rate_limits(cls, v: str) -> str:
        """Validate rate limit format."""
        import re
        pattern = r'^\d+/(second|minute|hour|day)$'
        if not re.match(pattern, v):
            raise ValueError("Rate limit must be in format: number/(second|minute|hour|day)")
        return v
    
    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django REST Framework settings."""
        settings = {
            'REST_FRAMEWORK': {
                'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
                'PAGE_SIZE': self.page_size,
                'MAX_PAGE_SIZE': self.max_page_size,
                
                'DEFAULT_AUTHENTICATION_CLASSES': [
                    'rest_framework.authentication.SessionAuthentication',
                    'rest_framework.authentication.TokenAuthentication',
                    'rest_framework_simplejwt.authentication.JWTAuthentication',
                ],
                
                'DEFAULT_PERMISSION_CLASSES': [
                    'rest_framework.permissions.IsAuthenticated',
                ],
                
                'DEFAULT_RENDERER_CLASSES': [
                    'rest_framework.renderers.JSONRenderer',
                    'rest_framework.renderers.BrowsableAPIRenderer',
                ],
                
                'DEFAULT_FILTER_BACKENDS': [
                    'django_filters.rest_framework.DjangoFilterBackend',
                    'rest_framework.filters.OrderingFilter',
                    'rest_framework.filters.SearchFilter',
                ],
            }
        }
        
        # Add throttling if enabled
        if self.rate_limit_enabled:
            settings['REST_FRAMEWORK']['DEFAULT_THROTTLE_CLASSES'] = [
                'rest_framework.throttling.AnonRateThrottle',
                'rest_framework.throttling.UserRateThrottle',
            ]
            settings['REST_FRAMEWORK']['DEFAULT_THROTTLE_RATES'] = {
                'anon': self.rate_limit_anon,
                'user': self.rate_limit_user,
            }
        
        # API documentation settings
        if self.docs_enabled:
            settings.update({
                'SPECTACULAR_SETTINGS': {
                    'TITLE': self.docs_title,
                    'DESCRIPTION': 'API for Django application',
                    'VERSION': self.docs_version,
                    'SERVE_INCLUDE_SCHEMA': False,
                    'SCHEMA_PATH_PREFIX': '/api/',
                }
            })
        
        return settings
