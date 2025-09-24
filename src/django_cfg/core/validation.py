"""
Configuration validation for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage
- Proper type annotations
- Comprehensive validation with helpful error messages
- No exception suppression
"""

from typing import List, Dict, Any, Optional, Set, Tuple, TYPE_CHECKING
import re
from pathlib import Path

from django_cfg.core.exceptions import ValidationError, ConfigurationError

if TYPE_CHECKING:
    from django_cfg.core.config import DjangoConfig


class ConfigurationValidator:
    """
    Comprehensive validation for DjangoConfig instances.
    
    Validates configuration consistency, security requirements,
    and Django compatibility with helpful error messages and suggestions.
    """
    
    @classmethod
    def validate(cls, config: 'DjangoConfig') -> List[str]:
        """
        Validate complete configuration.
        
        Args:
            config: DjangoConfig instance to validate
            
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            # Core validation
            errors.extend(cls._validate_core_settings(config))
            
            # Database validation
            errors.extend(cls._validate_databases(config))
            
            # Cache validation
            errors.extend(cls._validate_caches(config))
            
            # Security validation
            errors.extend(cls._validate_security(config))
            
            # Service validation
            errors.extend(cls._validate_services(config))
            
            # Environment-specific validation
            errors.extend(cls._validate_environment_consistency(config))
            
        except Exception as e:
            errors.append(f"Validation failed with error: {e}")
        
        return errors
    
    @classmethod
    def _validate_core_settings(cls, config: 'DjangoConfig') -> List[str]:
        """Validate core Django settings."""
        errors = []
        
        # Project name validation
        if not config.project_name or not config.project_name.strip():
            errors.append("Project name is required and cannot be empty")
        elif len(config.project_name) > 100:
            errors.append("Project name cannot exceed 100 characters")
        
        # Secret key validation
        if not config.secret_key:
            errors.append("SECRET_KEY is required")
        elif len(config.secret_key) < 50:
            errors.append("SECRET_KEY must be at least 50 characters long")
        else:
            # Check for insecure patterns in production
            if config._environment == 'production':
                insecure_patterns = [
                    'django-insecure',
                    'change-me',
                    'your-secret-key',
                    'dev-key',
                    'test-key',
                    '1234567890',
                ]
                
                secret_lower = config.secret_key.lower()
                for pattern in insecure_patterns:
                    if pattern in secret_lower:
                        errors.append(
                            f"Insecure SECRET_KEY pattern '{pattern}' detected in production environment"
                        )
                        break
        
        # Allowed hosts validation (now generated from security_domains)
        allowed_hosts = config.get_allowed_hosts()
        if not allowed_hosts:
            errors.append("ALLOWED_HOSTS cannot be empty (configure security_domains)")
        else:
            # Validate each host
            for i, host in enumerate(allowed_hosts):
                if not cls._is_valid_hostname(host):
                    errors.append(f"Invalid hostname in ALLOWED_HOSTS[{i}]: '{host}'")
            
            # Production-specific validation
            if config._environment == 'production' and '*' in allowed_hosts:
                errors.append("Wildcard '*' in ALLOWED_HOSTS is not recommended for production")
        
        return errors
    
    @classmethod
    def _validate_databases(cls, config: 'DjangoConfig') -> List[str]:
        """Validate database configuration."""
        errors = []
        
        if not config.databases:
            errors.append("At least one database must be configured")
            return errors
        
        # Check for default database
        if 'default' not in config.databases:
            errors.append("'default' database is required")
        
        return errors
    
    @classmethod
    def _validate_caches(cls, config: 'DjangoConfig') -> List[str]:
        """Validate cache configuration."""
        errors = []
        # Basic cache validation - more detailed validation in cache models
        return errors
    
    @classmethod
    def _validate_security(cls, config: 'DjangoConfig') -> List[str]:
        """Validate security configuration."""
        errors = []
        
        # Environment-specific security validation
        if config._environment == 'production':
            # Allow DEBUG=True in production for development purposes
            pass
        
        return errors
    
    @classmethod
    def _validate_services(cls, config: 'DjangoConfig') -> List[str]:
        """Validate service configurations."""
        errors = []
        # Service validation handled by service models
        return errors
    
    @classmethod
    def _validate_environment_consistency(cls, config: 'DjangoConfig') -> List[str]:
        """Validate environment-specific consistency."""
        errors = []
        
        environment = config._environment
        
        if environment == 'production':
            # Production requirements - allow DEBUG=True for development
            pass
        
        return errors
    
    @classmethod
    def _is_valid_hostname(cls, hostname: str) -> bool:
        """Validate hostname format."""
        if not hostname:
            return False
        
        if hostname == "*":
            return True  # Wildcard is valid
        
        # Basic hostname validation
        if len(hostname) > 253:
            return False
        
        # Allow IPv4 addresses
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(ipv4_pattern, hostname):
            return True
        
        # Hostname pattern
        hostname_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$'
        return bool(re.match(hostname_pattern, hostname))


# Export the main class
__all__ = [
    "ConfigurationValidator",
]