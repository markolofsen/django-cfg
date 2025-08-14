"""
Base Configuration Model

Foundation for all Django configuration models using Pydantic 2.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import DotEnvSettingsSource


class ConfigValidationError(Exception):
    """Configuration validation error with helpful developer messages."""
    
    def __init__(self, field: str, value: Any, message: str):
        self.field = field
        self.value = value
        self.message = message
        super().__init__(f"❌ Config error in '{field}': {message} (got: {value})")


class BaseConfig(BaseSettings):
    """
    🔥 Base configuration model with amazing developer experience
    
    Features:
    - Automatic .env file detection (.env.dev, .env.prod, etc.)
    - Nested environment variables with __ delimiter  
    - Type-safe validation with Pydantic 2
    - Helpful error messages for developers
    - Environment-specific configuration
    """
    
    model_config = SettingsConfigDict(
        # Environment file settings
        env_file='.env',
        env_file_encoding='utf-8',
        env_nested_delimiter='__',
        case_sensitive=False,
        
        # Validation settings
        validate_assignment=True,
        validate_default=True,
        extra='ignore',
        
        # Performance settings
        frozen=False,
        arbitrary_types_allowed=False,
        use_enum_values=True,
    )
    
    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Custom settings sources with automatic env file detection."""
        env_file = cls._detect_env_file()
        if env_file:
            dotenv_settings = DotEnvSettingsSource(
                settings_cls, 
                env_file=env_file,
                env_file_encoding='utf-8'
            )
        
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    def __init__(self, **kwargs):
        """Initialize with smart .env file detection."""
        try:
            super().__init__(**kwargs)
        except Exception as e:
            self._handle_validation_error(e)
            raise
    
    @classmethod
    def _detect_env_file(cls) -> Optional[str]:
        """
        🔍 Smart environment file detection
        
        Priority order:
        1. .env.local (local overrides, should be git-ignored)
        2. .env.dev / .env.development (development)
        3. .env.prod / .env.production (production)
        4. config.env.dev / config.env.prod (project-specific)
        5. .env (fallback)
        """
        env_files = [
            '.env.local',
            '.env.dev',
            '.env.development', 
            '.env.prod',
            '.env.production',
            'config.env.dev',
            'config.env.prod',
            '.env'
        ]
        
        for env_file in env_files:
            if Path(env_file).exists():
                return env_file
        
        return None
    
    def _show_debug(self) -> bool:
        """Check if we should show debug info."""
        return os.getenv('DEBUG', 'false').lower() in ('true', '1', 'yes')
    
    def _handle_validation_error(self, error: Exception):
        """Provide helpful validation error messages for developers."""
        if hasattr(error, 'errors'):
            print("❌ Django Configuration Validation Errors:")
            print("=" * 50)
            
            for err in error.errors():
                field = '.'.join(str(x) for x in err['loc'])
                message = err['msg']
                input_val = err.get('input', 'N/A')
                
                print(f"🔴 Field: {field}")
                print(f"   Error: {message}")
                print(f"   Value: {input_val}")
                print(f"   💡 Fix: Check your .env file or environment variables")
                print()
            
            print("📚 Documentation: https://django-config-toolkit.readthedocs.io/")
            print("=" * 50)
    
    def to_django_settings(self) -> Dict[str, Any]:
        """Convert configuration to Django-compatible settings dictionary."""
        return self.model_dump(exclude_none=True, by_alias=True)
    
    def get_field_info(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed field information for developers."""
        field_info = {}
        
        for field_name, field in self.model_fields.items():
            field_info[field_name] = {
                'description': field.description or f"Configuration for {field_name}",
                'type': str(field.annotation) if hasattr(field, 'annotation') else 'Any',
                'default': field.default if field.default is not ... else None,
                'required': field.is_required(),
                'env_var': field_name.upper(),
            }
        
        return field_info
    
    def print_field_help(self):
        """Print helpful field information for developers."""
        print(f"📋 {self.__class__.__name__} Configuration Fields:")
        print("=" * 60)
        
        for field_name, info in self.get_field_info().items():
            current_value = getattr(self, field_name, None)
            
            # Hide sensitive values
            if any(word in field_name.lower() for word in ['secret', 'password', 'key', 'token']):
                display_value = "***HIDDEN***" if current_value else "Not set"
            else:
                display_value = current_value
            
            print(f"🔧 {field_name}:")
            print(f"   📝 {info['description']}")
            print(f"   🏷️  Type: {info['type']}")
            print(f"   🌍 Env: {info['env_var']}")
            print(f"   💾 Current: {display_value}")
            if info['default'] is not None:
                print(f"   🎯 Default: {info['default']}")
            if info['required']:
                print(f"   ⚠️  Required: Yes")
            print()
    
    @classmethod
    def create_env_example(cls, filename: str = ".env.example") -> None:
        """
        🚀 Create example .env file for developers
        
        This generates a complete .env.example file with all fields,
        descriptions, and example values.
        """
        lines = [
            "# 🚀 Django Configuration Environment Variables",
            "# Generated by Django Config Toolkit",
            "# Copy this file to .env and customize your settings",
            "",
            f"# === {cls.__name__} Configuration ===",
            "",
        ]
        
        # Create temporary instance to get field info
        try:
            temp_instance = cls()
            field_info = temp_instance.get_field_info()
        except:
            # Fallback if instance creation fails
            field_info = {}
            for field_name, field in cls.model_fields.items():
                field_info[field_name] = {
                    'description': field.description or f"Configure {field_name}",
                    'default': field.default if field.default is not ... else None,
                    'env_var': field_name.upper(),
                }
        
        for field_name, info in field_info.items():
            # Add description
            lines.append(f"# {info['description']}")
            
            # Generate example value
            default_val = info.get('default')
            if default_val is not None:
                example_value = default_val
            elif 'secret' in field_name.lower() or 'key' in field_name.lower():
                example_value = "your-secret-key-change-this-to-something-secure"
            elif 'password' in field_name.lower():
                example_value = "your-secure-password"
            elif 'url' in field_name.lower():
                if 'database' in field_name.lower():
                    example_value = "postgresql://user:password@localhost:5432/dbname"
                elif 'redis' in field_name.lower():
                    example_value = "redis://localhost:6379/0"
                else:
                    example_value = "https://example.com"
            elif 'debug' in field_name.lower():
                example_value = "true"
            elif 'port' in field_name.lower():
                example_value = "5432"
            elif 'timeout' in field_name.lower():
                example_value = "30"
            else:
                example_value = "change-me"
            
            # Add environment variable
            lines.append(f"{info['env_var']}={example_value}")
            lines.append("")
        
        # Write file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ Created example environment file: {filename}")
        print(f"💡 Copy it to .env and customize your settings!")
        print(f"📚 More info: https://django-config-toolkit.readthedocs.io/")
    
    def validate_for_environment(self, environment: str = "development") -> bool:
        """
        🧪 Validate configuration for specific environment
        
        Args:
            environment: Target environment (development/production/testing)
            
        Returns:
            True if configuration is valid for the environment
        """
        try:
            # Perform environment-specific validation
            if environment == "production":
                return self._validate_production()
            elif environment == "development":
                return self._validate_development()
            else:
                return True
        except Exception as e:
            print(f"❌ Validation failed for {environment}: {e}")
            return False
    
    def _validate_production(self) -> bool:
        """Validate production-specific requirements."""
        # Override in subclasses for specific validation
        return True
    
    def _validate_development(self) -> bool:
        """Validate development-specific requirements."""
        # Override in subclasses for specific validation  
        return True
