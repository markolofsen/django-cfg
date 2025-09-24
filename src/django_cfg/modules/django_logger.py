"""
Auto-configuring Django Logger for django_cfg.

This logger automatically configures itself based on the DjangoConfig instance
without requiring manual parameter passing.
"""

import logging
from typing import Optional, Dict, Any, Union
from pathlib import Path

from . import BaseCfgModule


class DjangoLogger(BaseCfgModule):
    """
    Auto-configuring logger that gets settings from DjangoConfig.
    
    Usage:
        from django_cfg.modules import DjangoLogger
        
        logger = DjangoLogger.get_logger("myapp")
        logger.info("This works automatically!")
    """
    
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def get_logger(cls, name: str = "django_cfg") -> logging.Logger:
        """
        Get a configured logger instance.
        
        Args:
            name: Logger name (default: "django_cfg")
            
        Returns:
            Configured logger instance
        """
        if name not in cls._loggers:
            cls._loggers[name] = cls._create_logger(name)
        return cls._loggers[name]
    
    @classmethod
    def _create_logger(cls, name: str) -> logging.Logger:
        """Create and configure a logger based on DjangoConfig."""
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
        except Exception:
            config = None
        
        # Create logger
        logger = logging.getLogger(name)
        
        # Get logging configuration from config
        log_level = logging.INFO
        console_output = True
        file_path = None
        
        # Try to get logging config from DjangoConfig
        if hasattr(config, 'logging') and config.logging:
            logging_config = config.logging
            log_level = getattr(logging, logging_config.level.upper(), logging.INFO)
            console_output = logging_config.console_output
            file_path = logging_config.file_path
        
        # Set logger level
        logger.setLevel(log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Add console handler if enabled
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(log_level)
            
            # Create formatter
            formatter = cls._create_formatter(config)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(console_handler)
        
        # Add file handler if file path is specified
        if file_path:
            file_path_obj = Path(file_path)
            file_path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(file_path_obj)
            file_handler.setLevel(log_level)
            
            # Create formatter for file
            file_formatter = cls._create_file_formatter(config)
            file_handler.setFormatter(file_formatter)
            
            logger.addHandler(file_handler)
        
        return logger
    
    @classmethod
    def _create_formatter(cls, config) -> logging.Formatter:
        """Create console formatter based on config."""
        if config.debug:
            # Detailed format for development
            format_str = '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
        else:
            # Simple format for production
            format_str = '%(levelname)s: %(message)s'
        
        return logging.Formatter(format_str)
    
    @classmethod
    def _create_file_formatter(cls, config) -> logging.Formatter:
        """Create file formatter based on config."""
        # Always detailed format for file logging
        format_str = '[%(asctime)s] %(levelname)s in %(name)s [%(filename)s:%(lineno)d]: %(message)s'
        return logging.Formatter(format_str)
    
    @classmethod
    def configure_django_logging(cls) -> Dict[str, Any]:
        """
        Generate Django LOGGING configuration automatically.
        
        Returns:
            Django LOGGING configuration dict
        """
        try:
            from django_cfg.core.config import get_current_config
            config = get_current_config()
        except Exception:
            config = None
        
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '[{asctime}] {levelname} in {name}: {message}',
                    'style': '{',
                },
                'simple': {
                    'format': '{levelname}: {message}',
                    'style': '{',
                },
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose' if config.debug else 'simple',
                },
            },
            'root': {
                'handlers': ['console'],
                'level': 'DEBUG' if config.debug else 'INFO',
            },
            'loggers': {
                'django_cfg': {
                    'handlers': ['console'],
                    'level': 'DEBUG' if config.debug else 'INFO',
                    'propagate': False,
                },
            },
        }
        
        # Add file handler if logging config exists
        if hasattr(config, 'logging') and config.logging and config.logging.file_path:
            logging_config['handlers']['file'] = {
                'class': 'logging.FileHandler',
                'filename': config.logging.file_path,
                'formatter': 'verbose',
            }
            
            # Add file handler to root and django_cfg loggers
            logging_config['root']['handlers'].append('file')
            logging_config['loggers']['django_cfg']['handlers'].append('file')
        
        return logging_config


# Convenience function for quick access
def get_logger(name: str = "django_cfg") -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (default: "django_cfg")
        
    Returns:
        Configured logger instance
    """
    return DjangoLogger.get_logger(name)


# Export public API
__all__ = ['DjangoLogger', 'get_logger']
