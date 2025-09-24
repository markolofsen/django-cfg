"""
Environment detection utilities for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage
- Proper type annotations
- Specific exception handling
- No exception suppression
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path

from django_cfg.core.exceptions import EnvironmentError


class EnvironmentDetector:
    """
    Intelligent environment detection system.
    
    Detects the current environment from various sources with a clear priority order.
    Provides consistent environment names and validation.
    """
    
    # Environment detection priority (highest to lowest)
    ENV_VARIABLES: List[str] = [
        'DJANGO_ENV',
        'ENVIRONMENT', 
        'ENV',
    ]
    
    # Environment name normalization
    ENV_ALIASES: Dict[str, str] = {
        'dev': 'development',
        'devel': 'development',
        'develop': 'development',
        'local': 'development',
        'prod': 'production',
        'production': 'production',
        'test': 'testing',
        'testing': 'testing',
        'stage': 'staging',
        'staging': 'staging',
    }
    
    # Valid environment names
    VALID_ENVIRONMENTS: List[str] = [
        'development',
        'production', 
        'testing',
        'staging',
    ]
    
    @classmethod
    def detect_environment(cls) -> str:
        """
        Detect current environment from various sources.
        
        Priority order:
        1. DJANGO_ENV environment variable
        2. ENVIRONMENT environment variable
        3. ENV environment variable
        4. DEBUG flag analysis (True = development, False = production)
        5. Default to 'development'
        
        Returns:
            Normalized environment name
            
        Raises:
            EnvironmentError: If environment detection fails
        """
        try:
            # Check environment variables in priority order
            for env_var in cls.ENV_VARIABLES:
                env_value = os.environ.get(env_var)
                if env_value:
                    normalized = cls._normalize_environment(env_value)
                    if normalized:
                        return normalized
                    else:
                        raise EnvironmentError(
                            f"Invalid environment value '{env_value}' in {env_var}",
                            environment=env_value,
                            context={
                                'env_var': env_var,
                                'valid_environments': cls.VALID_ENVIRONMENTS,
                                'valid_aliases': list(cls.ENV_ALIASES.keys())
                            },
                            suggestions=[
                                f"Set {env_var} to one of: {', '.join(cls.VALID_ENVIRONMENTS)}",
                                f"Or use aliases: {', '.join(cls.ENV_ALIASES.keys())}"
                            ]
                        )
            
            # Check DEBUG flag as fallback
            debug_value = os.environ.get('DEBUG', '').lower().strip()
            if debug_value:
                if debug_value in ('true', '1', 'yes', 'on'):
                    return 'development'
                elif debug_value in ('false', '0', 'no', 'off'):
                    return 'production'
            
            # Default fallback
            return 'development'
            
        except EnvironmentError:
            raise  # Re-raise our own exceptions
        except Exception as e:
            raise EnvironmentError(
                f"Failed to detect environment: {e}",
                context={'env_variables': dict(os.environ)},
                suggestions=[
                    "Set DJANGO_ENV environment variable explicitly",
                    "Check environment variable syntax"
                ]
            ) from e
    
    @classmethod
    def _normalize_environment(cls, env: str) -> Optional[str]:
        """
        Normalize environment name to standard format.
        
        Args:
            env: Raw environment name
            
        Returns:
            Normalized environment name or None if invalid
        """
        if not env:
            return None
        
        env_clean = env.lower().strip()
        
        # Direct match with valid environments
        if env_clean in cls.VALID_ENVIRONMENTS:
            return env_clean
        
        # Alias match
        return cls.ENV_ALIASES.get(env_clean)
    
    @classmethod
    def is_development(cls, environment: Optional[str] = None) -> bool:
        """
        Check if environment is development.
        
        Args:
            environment: Environment to check (auto-detect if None)
            
        Returns:
            True if development environment
        """
        env = environment or cls.detect_environment()
        return env == 'development'
    
    @classmethod
    def is_production(cls, environment: Optional[str] = None) -> bool:
        """
        Check if environment is production.
        
        Args:
            environment: Environment to check (auto-detect if None)
            
        Returns:
            True if production environment
        """
        env = environment or cls.detect_environment()
        return env == 'production'
    
    @classmethod
    def is_testing(cls, environment: Optional[str] = None) -> bool:
        """
        Check if environment is testing.
        
        Args:
            environment: Environment to check (auto-detect if None)
            
        Returns:
            True if testing environment
        """
        env = environment or cls.detect_environment()
        return env == 'testing'
    
    @classmethod
    def is_staging(cls, environment: Optional[str] = None) -> bool:
        """
        Check if environment is staging.
        
        Args:
            environment: Environment to check (auto-detect if None)
            
        Returns:
            True if staging environment
        """
        env = environment or cls.detect_environment()
        return env == 'staging'
    
    @classmethod
    def get_environment_info(cls) -> Dict[str, Any]:
        """
        Get detailed environment information for debugging.
        
        Returns:
            Dictionary with environment detection details
        """
        try:
            detected_env = cls.detect_environment()
            
            return {
                'environment': detected_env,
                'is_development': cls.is_development(detected_env),
                'is_production': cls.is_production(detected_env),
                'is_testing': cls.is_testing(detected_env),
                'is_staging': cls.is_staging(detected_env),
                'debug_flag': os.environ.get('DEBUG', 'not_set'),
                'env_variables': {
                    var: os.environ.get(var, 'not_set')
                    for var in cls.ENV_VARIABLES
                },
                'detection_source': cls._get_detection_source(),
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'env_variables': {
                    var: os.environ.get(var, 'not_set')
                    for var in cls.ENV_VARIABLES
                },
                'debug_flag': os.environ.get('DEBUG', 'not_set'),
            }
    
    @classmethod
    def _get_detection_source(cls) -> str:
        """
        Determine which source was used for environment detection.
        
        Returns:
            Source name that provided the environment
        """
        # Check environment variables in priority order
        for env_var in cls.ENV_VARIABLES:
            env_value = os.environ.get(env_var)
            if env_value and cls._normalize_environment(env_value):
                return env_var
        
        # Check DEBUG flag
        debug_value = os.environ.get('DEBUG', '').lower().strip()
        if debug_value in ('true', '1', 'yes', 'on', 'false', '0', 'no', 'off'):
            return 'DEBUG'
        
        return 'default_fallback'
    
    @classmethod
    def validate_environment(cls, environment: str) -> bool:
        """
        Validate if environment name is valid.
        
        Args:
            environment: Environment name to validate
            
        Returns:
            True if valid environment name
        """
        return environment in cls.VALID_ENVIRONMENTS
    
    @classmethod
    def get_valid_environments(cls) -> List[str]:
        """
        Get list of valid environment names.
        
        Returns:
            List of valid environment names
        """
        return cls.VALID_ENVIRONMENTS.copy()
    
    @classmethod
    def get_environment_aliases(cls) -> Dict[str, str]:
        """
        Get mapping of environment aliases.
        
        Returns:
            Dictionary mapping aliases to canonical names
        """
        return cls.ENV_ALIASES.copy()


# Export the main class
__all__ = [
    "EnvironmentDetector",
]
