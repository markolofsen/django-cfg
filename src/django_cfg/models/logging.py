"""
Logging Configuration Model

Django logging settings with Pydantic 2.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from pydantic import Field, field_validator
from .base import BaseConfig


class LoggerConfig(BaseConfig):
    """Configuration for a single logger."""
    
    name: str = Field(
        description="Logger name"
    )
    
    level: str = Field(
        default="INFO",
        description="Log level"
    )
    
    handlers: List[str] = Field(
        default_factory=list,
        description="Handler names for this logger"
    )
    
    propagate: bool = Field(
        default=True,
        description="Whether to propagate to parent loggers"
    )
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


class HandlerConfig(BaseConfig):
    """Configuration for a log handler."""
    
    name: str = Field(
        description="Handler name"
    )
    
    class_name: str = Field(
        description="Handler class"
    )
    
    level: str = Field(
        default="INFO", 
        description="Handler log level"
    )
    
    formatter: str = Field(
        default="verbose",
        description="Formatter name"
    )
    
    filename: Optional[str] = Field(
        default=None,
        description="Log file path (for file handlers)"
    )
    
    max_bytes: int = Field(
        default=10485760,  # 10MB
        description="Max bytes for rotating file handler"
    )
    
    backup_count: int = Field(
        default=5,
        description="Backup count for rotating file handler"
    )
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


class FormatterConfig(BaseConfig):
    """Configuration for a log formatter."""
    
    name: str = Field(
        description="Formatter name"
    )
    
    format_string: str = Field(
        description="Log format string"
    )
    
    date_format: Optional[str] = Field(
        default=None,
        description="Date format string"
    )


class LoggingConfig(BaseConfig):
    """
    📝 Logging Configuration - Structured Logging
    
    Complete logging configuration with formatters, handlers,
    and loggers for Django applications.
    """
    
    # Global settings
    version: int = Field(
        default=1,
        description="Logging config version"
    )
    
    disable_existing_loggers: bool = Field(
        default=False,
        description="Disable existing loggers"
    )
    
    # Log level settings
    root_level: str = Field(
        default="INFO",
        description="Root logger level"
    )
    
    django_level: str = Field(
        default="INFO",
        description="Django logger level"
    )
    
    # File settings
    log_dir: Optional[str] = Field(
        default=None,
        description="Directory for log files"
    )
    
    # Console settings
    console_enabled: bool = Field(
        default=True,
        description="Enable console logging"
    )
    
    # File logging settings
    file_enabled: bool = Field(
        default=True,
        description="Enable file logging"
    )
    
    # Rotating file settings
    rotating_enabled: bool = Field(
        default=True,
        description="Enable rotating file logging"
    )
    
    max_file_size: int = Field(
        default=10485760,  # 10MB
        description="Maximum log file size in bytes"
    )
    
    backup_count: int = Field(
        default=5,
        description="Number of backup log files to keep"
    )
    
    # Custom loggers, handlers, formatters
    custom_loggers: List[LoggerConfig] = Field(
        default_factory=list,
        description="Custom logger configurations"
    )
    
    custom_handlers: List[HandlerConfig] = Field(
        default_factory=list,
        description="Custom handler configurations"
    )
    
    custom_formatters: List[FormatterConfig] = Field(
        default_factory=list,
        description="Custom formatter configurations"
    )
    
    @field_validator('root_level', 'django_level')
    @classmethod
    def validate_levels(cls, v: str) -> str:
        """Validate log levels."""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    def get_log_directory(self) -> Path:
        """Get log directory path."""
        if self.log_dir:
            return Path(self.log_dir)
        
        # Default to logs/ in current directory
        return Path.cwd() / "logs"
    
    def get_default_formatters(self) -> Dict[str, Any]:
        """Get default log formatters."""
        formatters = {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'django.server': {
                'format': '{asctime} {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        }
        
        # Add custom formatters
        for formatter in self.custom_formatters:
            formatters[formatter.name] = {
                'format': formatter.format_string,
                'style': '{',
            }
            if formatter.date_format:
                formatters[formatter.name]['datefmt'] = formatter.date_format
        
        return formatters
    
    def get_default_handlers(self) -> Dict[str, Any]:
        """Get default log handlers."""
        handlers = {}
        
        # Console handler
        if self.console_enabled:
            handlers['console'] = {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            }
        
        # File handler
        if self.file_enabled:
            log_dir = self.get_log_directory()
            log_dir.mkdir(exist_ok=True)
            
            handlers['file'] = {
                'level': 'INFO',
                'class': 'logging.FileHandler',
                'filename': str(log_dir / 'django.log'),
                'formatter': 'verbose',
            }
        
        # Rotating file handler
        if self.rotating_enabled:
            log_dir = self.get_log_directory()
            log_dir.mkdir(exist_ok=True)
            
            handlers['rotating_file'] = {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': str(log_dir / 'django_rotating.log'),
                'maxBytes': self.max_file_size,
                'backupCount': self.backup_count,
                'formatter': 'verbose',
            }
        
        # Error file handler
        if self.file_enabled:
            log_dir = self.get_log_directory()
            log_dir.mkdir(exist_ok=True)
            
            handlers['error_file'] = {
                'level': 'ERROR',
                'class': 'logging.FileHandler',
                'filename': str(log_dir / 'django_errors.log'),
                'formatter': 'verbose',
            }
        
        # Add custom handlers
        for handler in self.custom_handlers:
            handler_config = {
                'level': handler.level,
                'class': handler.class_name,
                'formatter': handler.formatter,
            }
            
            if handler.filename:
                handler_config['filename'] = handler.filename
            
            if 'RotatingFileHandler' in handler.class_name:
                handler_config['maxBytes'] = handler.max_bytes
                handler_config['backupCount'] = handler.backup_count
            
            handlers[handler.name] = handler_config
        
        return handlers
    
    def get_default_loggers(self) -> Dict[str, Any]:
        """Get default logger configurations."""
        # Determine available handlers
        available_handlers = []
        if self.console_enabled:
            available_handlers.append('console')
        if self.file_enabled:
            available_handlers.extend(['file', 'error_file'])
        if self.rotating_enabled:
            available_handlers.append('rotating_file')
        
        loggers = {
            'django': {
                'handlers': available_handlers,
                'level': self.django_level,
                'propagate': False,
            },
            'django.request': {
                'handlers': available_handlers,
                'level': 'ERROR',
                'propagate': False,
            },
            'django.server': {
                'handlers': ['console'] if self.console_enabled else [],
                'level': 'INFO',
                'propagate': False,
            },
        }
        
        # Add custom loggers
        for logger in self.custom_loggers:
            loggers[logger.name] = {
                'handlers': logger.handlers,
                'level': logger.level,
                'propagate': logger.propagate,
            }
        
        return loggers
    
    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django LOGGING setting."""
        # Determine root handlers
        root_handlers = []
        if self.console_enabled:
            root_handlers.append('console')
        if self.file_enabled:
            root_handlers.append('file')
        
        logging_config = {
            'version': self.version,
            'disable_existing_loggers': self.disable_existing_loggers,
            'formatters': self.get_default_formatters(),
            'handlers': self.get_default_handlers(),
            'root': {
                'level': self.root_level,
                'handlers': root_handlers,
            },
            'loggers': self.get_default_loggers(),
        }
        
        return {
            'LOGGING': logging_config
        }
