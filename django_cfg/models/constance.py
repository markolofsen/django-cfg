"""
Django Constance Configuration Model

Django Constance dynamic settings with Pydantic 2.
"""

from typing import Dict, Any, List, Union, Optional
from pydantic import Field, field_validator
from .base import BaseConfig


class ConstanceFieldConfig(BaseConfig):
    """Configuration for a single Constance field."""
    
    name: str = Field(
        description="Field name"
    )
    
    default: Union[str, int, float, bool] = Field(
        description="Default value"
    )
    
    help_text: str = Field(
        default="",
        description="Help text for the field"
    )
    
    field_type: str = Field(
        default="str",
        description="Field type (str, int, float, bool)"
    )
    
    @field_validator('field_type')
    @classmethod
    def validate_field_type(cls, v: str) -> str:
        """Validate field type."""
        allowed = ['str', 'int', 'float', 'bool']
        if v not in allowed:
            raise ValueError(f"Field type must be one of: {allowed}")
        return v


class ConstanceConfig(BaseConfig):
    """
    ⚙️ Constance Configuration - Dynamic Settings
    
    Django Constance configuration for dynamic settings that can be
    changed at runtime through the admin interface.
    """
    
    # Backend settings
    backend: str = Field(
        default="constance.backends.database.DatabaseBackend",
        description="Constance backend"
    )
    
    # Redis backend settings (if using Redis)
    redis_connection: Optional[str] = Field(
        default=None,
        description="Redis connection string for Constance"
    )
    
    # Database backend settings
    database_cache_backend: str = Field(
        default="default",
        description="Database cache backend for Constance"
    )
    
    # Additional config
    additional_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Constance configuration"
    )
    
    # Predefined config fields
    config_fields: List[ConstanceFieldConfig] = Field(
        default_factory=list,
        description="Predefined configuration fields"
    )
    
    # Admin settings
    admin_interface_enabled: bool = Field(
        default=True,
        description="Enable Constance admin interface"
    )
    
    @field_validator('backend')
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate Constance backend."""
        valid_backends = [
            'constance.backends.database.DatabaseBackend',
            'constance.backends.redis.RedisBackend',
            'constance.backends.memory.MemoryBackend',
        ]
        if v not in valid_backends:
            raise ValueError(f"Backend must be one of: {valid_backends}")
        return v
    
    def add_config_field(self, name: str, default: Union[str, int, float, bool],
                        help_text: str = "", field_type: str = "str") -> None:
        """Add a configuration field."""
        self.config_fields.append(ConstanceFieldConfig(
            name=name,
            default=default,
            help_text=help_text,
            field_type=field_type
        ))
    
    def get_default_config_fields(self) -> List[ConstanceFieldConfig]:
        """Get default configuration fields."""
        return [
            ConstanceFieldConfig(
                name="SITE_NAME",
                default="My Site",
                help_text="The name of your site",
                field_type="str"
            ),
            ConstanceFieldConfig(
                name="SITE_DESCRIPTION", 
                default="Welcome to my site",
                help_text="Description of your site",
                field_type="str"
            ),
            ConstanceFieldConfig(
                name="MAINTENANCE_MODE",
                default=False,
                help_text="Enable maintenance mode",
                field_type="bool"
            ),
            ConstanceFieldConfig(
                name="MAX_UPLOAD_SIZE",
                default=10485760,  # 10MB
                help_text="Maximum upload size in bytes",
                field_type="int"
            ),
            ConstanceFieldConfig(
                name="API_RATE_LIMIT",
                default=1000,
                help_text="API rate limit per hour",
                field_type="int"
            ),
            ConstanceFieldConfig(
                name="EMAIL_NOTIFICATIONS",
                default=True,
                help_text="Enable email notifications",
                field_type="bool"
            ),
        ]
    
    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django Constance settings."""
        # Use default fields if none configured
        fields = self.config_fields if self.config_fields else self.get_default_config_fields()
        
        # Build CONSTANCE_CONFIG
        constance_config = {}
        constance_config_fieldsets = {}
        
        for field in fields:
            # Add to config with tuple format: (default_value, help_text, field_type)
            if field.field_type == 'str':
                field_class = str
            elif field.field_type == 'int':
                field_class = int
            elif field.field_type == 'float':
                field_class = float
            elif field.field_type == 'bool':
                field_class = bool
            else:
                field_class = str
            
            constance_config[field.name] = (
                field.default,
                field.help_text,
                field_class
            )
        
        # Build settings
        settings = {
            'CONSTANCE_BACKEND': self.backend,
            'CONSTANCE_CONFIG': constance_config,
        }
        
        # Add additional config
        settings.update(self.additional_config)
        
        # Redis-specific settings
        if self.backend == 'constance.backends.redis.RedisBackend':
            if self.redis_connection:
                settings['CONSTANCE_REDIS_CONNECTION'] = self.redis_connection
            else:
                settings['CONSTANCE_REDIS_CONNECTION'] = {
                    'host': 'localhost',
                    'port': 6379,
                    'db': 0,
                }
        
        # Database-specific settings
        elif self.backend == 'constance.backends.database.DatabaseBackend':
            settings['CONSTANCE_DATABASE_CACHE_BACKEND'] = self.database_cache_backend
        
        # Fieldsets for better admin organization
        if len(fields) > 0:
            # Group fields by category
            general_fields = []
            api_fields = []
            system_fields = []
            
            for field in fields:
                if 'API' in field.name or 'RATE' in field.name:
                    api_fields.append(field.name)
                elif 'MAINTENANCE' in field.name or 'UPLOAD' in field.name:
                    system_fields.append(field.name)
                else:
                    general_fields.append(field.name)
            
            fieldsets = {}
            if general_fields:
                fieldsets['General'] = general_fields
            if api_fields:
                fieldsets['API Settings'] = api_fields
            if system_fields:
                fieldsets['System'] = system_fields
            
            if fieldsets:
                settings['CONSTANCE_CONFIG_FIELDSETS'] = fieldsets
        
        return {
            **settings,
            # Add Constance to INSTALLED_APPS
            "_CONSTANCE_APPS": [
                "constance",
                "constance.backends.database",
            ]
        }
