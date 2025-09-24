"""
Configuration classes for ExternalDataMixin.
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator, ConfigDict

from ..models.external_data import ExternalDataType


class ExternalDataConfig(BaseModel):
    """Configuration for ExternalData creation with Pydantic2 validation."""
    
    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_default=True
    )
    
    # Basic information
    title: str = Field(
        ...,
        min_length=3,
        max_length=512,
        description="Human-readable title for the external data source"
    )
    
    description: Optional[str] = Field(
        default="",
        max_length=2000,
        description="Description of what this external data contains"
    )
    
    # Source configuration
    source_type: ExternalDataType = Field(
        default=ExternalDataType.MODEL,
        description="Type of external data source"
    )
    
    source_identifier: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique identifier for the data source"
    )
    
    # Content
    content: str = Field(
        default="",
        description="Extracted text content for vectorization"
    )
    
    # Search and processing settings
    similarity_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Similarity threshold for search (0.0-1.0)"
    )
    
    # Visibility settings
    is_active: bool = Field(
        default=True,
        description="Whether this data source is active for search"
    )
    
    is_public: bool = Field(
        default=False,
        description="Whether this data is publicly searchable"
    )
    
    # Additional data
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata from the source"
    )
    
    source_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration for data extraction"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Tags for categorization and filtering"
    )
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate tags are non-empty strings."""
        if not isinstance(v, list):
            raise ValueError('Tags must be a list of strings')
        
        for tag in v:
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError('Each tag must be a non-empty string')
        
        return [tag.strip() for tag in v]
    
    @field_validator('metadata', 'source_config')
    @classmethod
    def validate_json_fields(cls, v):
        """Validate JSON fields are serializable."""
        if not isinstance(v, dict):
            raise ValueError('Must be a dictionary')
        return v
