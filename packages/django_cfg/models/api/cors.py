"""
CORS Configuration Models

Handles CORS settings with smart defaults and custom header support.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class CORSConfig(BaseModel):
    """CORS configuration with smart defaults"""
    
    # Custom headers (user-defined)
    custom_headers: List[str] = Field(
        default_factory=list,
        description="Custom headers to allow (e.g., ['x-api-key'])"
    )
    
    # Origins
    allowed_origins: Optional[List[str]] = Field(
        default=None,
        description="Allowed origins (None = all origins allowed)"
    )
    
    # Credentials
    allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests"
    )
    
    # Methods
    allowed_methods: List[str] = Field(
        default_factory=lambda: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        description="Allowed HTTP methods"
    )
    
    # Max age
    max_age: int = Field(
        default=86400,  # 24 hours
        description="Max age for preflight requests in seconds"
    )
    
    def get_all_headers(self) -> List[str]:
        """Get all headers (standard + custom)"""
        # Standard headers that are always needed
        standard_headers = [
            "accept",
            "accept-encoding", 
            "authorization",
            "content-type",
            "dnt",
            "origin",
            "user-agent",
            "x-csrftoken",
            "x-requested-with",
        ]
        
        # Combine with custom headers
        all_headers = standard_headers + self.custom_headers
        
        # Remove duplicates while preserving order
        seen = set()
        unique_headers = []
        for header in all_headers:
            if header.lower() not in seen:
                seen.add(header.lower())
                unique_headers.append(header)
        
        return unique_headers


# ===== AUTO-CONFIGURATION MODULE =====

try:
    from .cfg import BaseCfgAutoModule
    
    class DjangoCORSModule(BaseCfgAutoModule):
        """Django CORS auto-configuration module"""
        
        def get_smart_defaults(self) -> CORSConfig:
            """Get smart default CORS configuration"""
            return CORSConfig(
                custom_headers=["x-api-key"],
                allowed_origins=None,  # Allow all origins by default
                allow_credentials=True,
                allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                max_age=86400,  # 24 hours
            )
        
        def get_module_config(self) -> CORSConfig:
            """Get CORS configuration with project overrides"""
            if self.has_config_field('cors'):
                return self.get_config_field('cors')
            return self.get_smart_defaults()
        
        def get_cors_config(self, custom_headers: Optional[List[str]] = None) -> CORSConfig:
            """Get CORS configuration with custom headers support"""
            # Get base config (project or defaults)
            cors_config = self.get_module_config()
            
            # Override custom headers if provided
            if custom_headers:
                cors_config = cors_config.model_copy()
                cors_config.custom_headers = custom_headers
            
            return cors_config

except ImportError:
    # BaseCfgAutoModule not available - auto-configuration disabled
    DjangoCORSModule = None


# Export all models
__all__ = [
    "CORSConfig",
    "DjangoCORSModule",
]
