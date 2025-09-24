"""
Limits configuration models for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper validation and type safety
- Environment-aware defaults
- Simplified configuration with smart defaults
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, model_validator
from django_cfg.core.exceptions import ConfigurationError


class LimitsConfig(BaseModel):
    """
    Simplified limits configuration for Django applications.
    
    All file sizes are specified in megabytes for convenience.
    Django-cfg handles all the conversion and smart defaults.
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }
    
    # File upload limits (in MB)
    max_upload_mb: float = Field(
        default=10.0,
        description="Maximum file upload size in megabytes",
        ge=0.1,  # At least 100KB
        le=1024.0,  # Max 1GB
    )
    
    max_memory_mb: float = Field(
        default=2.0,
        description="Maximum size for in-memory file uploads in megabytes",
        ge=0.1,
        le=100.0,
    )
    
    # Request limits (in MB)
    max_request_mb: float = Field(
        default=50.0,
        description="Maximum HTTP request size in megabytes",
        ge=0.1,
        le=1024.0,
    )
    
    # Simple file security
    allowed_extensions: Optional[List[str]] = Field(
        default=None,
        description="List of allowed file extensions (without dots). If None, uses smart defaults.",
    )
    
    blocked_extensions: Optional[List[str]] = Field(
        default=None,
        description="List of blocked file extensions for security. If None, uses smart defaults.",
    )
    
    # Request timeout
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds",
        ge=1,
        le=3600,
    )
    
    # Global settings
    enabled: bool = Field(
        default=True,
        description="Whether limits are enforced",
    )
    
    strict_mode: bool = Field(
        default=False,
        description="Whether to use strict validation (fail on limit violations)",
    )
    
    @field_validator('allowed_extensions', 'blocked_extensions')
    @classmethod
    def validate_extensions(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate file extensions format."""
        if v is None:
            return v
        
        validated = []
        for ext in v:
            # Remove leading dots and convert to lowercase
            clean_ext = ext.lstrip('.').lower().strip()
            if not clean_ext:
                continue
            
            # Basic validation - only alphanumeric characters
            if not clean_ext.replace('_', '').replace('-', '').isalnum():
                raise ValueError(f"Invalid file extension: {ext}")
            
            validated.append(clean_ext)
        
        return validated
    
    @model_validator(mode='after')
    def validate_limits(self) -> 'LimitsConfig':
        """Validate limits consistency."""
        # Memory upload size should not exceed max upload size
        if self.max_memory_mb > self.max_upload_mb:
            raise ValueError(
                "max_memory_mb cannot be larger than max_upload_mb"
            )
        
        # Check for conflicts between allowed and blocked extensions
        if self.allowed_extensions and self.blocked_extensions:
            conflicts = set(self.allowed_extensions) & set(self.blocked_extensions)
            if conflicts:
                raise ValueError(
                    f"Extensions cannot be both allowed and blocked: {conflicts}"
                )
        
        return self
    
    def _get_smart_allowed_extensions(self) -> List[str]:
        """Get smart default allowed extensions."""
        return [
            # Images
            "jpg", "jpeg", "png", "gif", "webp", "svg",
            # Documents
            "pdf", "doc", "docx", "txt", "rtf", "odt",
            # Spreadsheets
            "xls", "xlsx", "csv", "ods",
            # Archives
            "zip", "rar", "7z", "tar", "gz",
            # Media
            "mp3", "mp4", "avi", "mov", "wav",
        ]
    
    def _get_smart_blocked_extensions(self) -> List[str]:
        """Get smart default blocked extensions for security."""
        return [
            # Executables
            "exe", "bat", "cmd", "com", "scr", "pif", "msi",
            # Scripts
            "vbs", "js", "jar", "php", "asp", "aspx", "jsp",
            "py", "rb", "pl", "sh", "bash", "ps1", "psm1",
            # System files
            "dll", "sys", "drv", "ocx",
            # Potentially dangerous
            "hta", "reg", "inf", "cab", "cpl",
        ]
    
    def to_django_settings(self) -> Dict[str, Any]:
        """
        Convert limits configuration to Django settings.
        
        Returns:
            Dictionary of Django settings for limits
        """
        if not self.enabled:
            return {}
        
        # Convert MB to bytes
        max_upload_bytes = int(self.max_upload_mb * 1024 * 1024)
        max_memory_bytes = int(self.max_memory_mb * 1024 * 1024)
        max_request_bytes = int(self.max_request_mb * 1024 * 1024)
        
        settings = {}
        
        # Core Django file upload settings
        settings.update({
            'FILE_UPLOAD_MAX_MEMORY_SIZE': max_memory_bytes,
            'DATA_UPLOAD_MAX_MEMORY_SIZE': min(max_memory_bytes, max_request_bytes),
            'DATA_UPLOAD_MAX_NUMBER_FIELDS': 1000,  # Reasonable default
        })
        
        # File extension security
        allowed_exts = self.allowed_extensions or self._get_smart_allowed_extensions()
        blocked_exts = self.blocked_extensions or self._get_smart_blocked_extensions()
        
        settings.update({
            'ALLOWED_FILE_EXTENSIONS': allowed_exts,
            'BLOCKED_FILE_EXTENSIONS': blocked_exts,
        })
        
        # Custom settings for middleware/validators
        settings.update({
            'LIMITS_CONFIG': {
                'max_upload_bytes': max_upload_bytes,
                'max_memory_bytes': max_memory_bytes,
                'max_request_bytes': max_request_bytes,
                'request_timeout': self.request_timeout,
                'allowed_extensions': allowed_exts,
                'blocked_extensions': blocked_exts,
                'enabled': self.enabled,
                'strict_mode': self.strict_mode,
            }
        })
        
        return settings
    
    def get_validator_config(self) -> Dict[str, Any]:
        """Get configuration for validation middleware."""
        allowed_exts = self.allowed_extensions or self._get_smart_allowed_extensions()
        blocked_exts = self.blocked_extensions or self._get_smart_blocked_extensions()
        
        return {
            'max_upload_bytes': int(self.max_upload_mb * 1024 * 1024),
            'max_memory_bytes': int(self.max_memory_mb * 1024 * 1024),
            'max_request_bytes': int(self.max_request_mb * 1024 * 1024),
            'request_timeout': self.request_timeout,
            'allowed_extensions': allowed_exts,
            'blocked_extensions': blocked_exts,
            'strict_mode': self.strict_mode,
        }


# Export the main model
__all__ = [
    "LimitsConfig",
]
