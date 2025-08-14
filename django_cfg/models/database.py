"""
Database Configuration Model

Django database settings with Pydantic 2.
Fully compliant with CRITICAL_REQUIREMENTS.md standards.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

import dj_database_url
from pydantic import Field, field_validator, computed_field

from .base import BaseConfig


class DatabaseConfig(BaseConfig):
    """
    🗄️ Database Configuration - Type-safe database settings
    
    Supports PostgreSQL, MySQL, SQLite with connection pooling,
    SSL, and multiple database configurations.
    """
    
    # Primary database
    database_url: str = Field(
        default="sqlite:///db.sqlite3",
        description="Primary database URL (postgresql://user:pass@host:port/db)"
    )
    
    # Connection settings
    max_connections: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum database connections in pool"
    )
    
    conn_max_age: int = Field(
        default=600,
        ge=0,
        description="Database connection max age in seconds (0 = new connection per request)"
    )
    
    conn_health_checks: bool = Field(
        default=True,
        description="Enable database connection health checks"
    )
    
    # SSL settings
    ssl_require: bool = Field(
        default=False,
        description="Require SSL for database connections"
    )
    
    ssl_mode: str = Field(
        default="prefer",
        description="SSL mode (disable/allow/prefer/require/verify-ca/verify-full)"
    )
    
    # Query settings
    query_timeout: int = Field(
        default=30,
        ge=1,
        le=300,
        description="Database query timeout in seconds"
    )
    
    # Multiple databases (universal approach)
    read_replica_url: Optional[str] = Field(
        default=None,
        description="Read replica database URL (optional)"
    )
    
    cache_db_url: Optional[str] = Field(
        default=None,
        description="Cache database URL (optional, for database-based caching)"
    )
    
    analytics_db_url: Optional[str] = Field(
        default=None,
        description="Analytics database URL (optional)"
    )
    
    @field_validator('database_url')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        # Basic URL validation
        url_pattern = r'^(sqlite|postgresql|mysql)://.*'
        if not re.match(url_pattern, v, re.IGNORECASE):
            raise ValueError(
                "Database URL must start with sqlite://, postgresql://, or mysql://"
            )
        
        return v
    
    @field_validator('ssl_mode')
    @classmethod
    def validate_ssl_mode(cls, v: str) -> str:
        """Validate SSL mode."""
        valid_modes = ['disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full']
        if v not in valid_modes:
            raise ValueError(f"SSL mode must be one of: {valid_modes}")
        return v
    
    def _get_additional_databases(self) -> Dict[str, str]:
        """
        🔍 Universal auto-detection of additional databases
        
        Reads directly from environment file to find DATABASE_URL_* patterns
        and automatically configures additional databases.
        """
        additional_dbs: Dict[str, str] = {}
        
        # Check environment variables first
        for key, value in os.environ.items():
            if key.startswith('DATABASE_URL_') and key != 'DATABASE_URL' and value:
                db_name = key[len('DATABASE_URL_'):].lower()
                additional_dbs[db_name] = value
        
        # Also read from the detected env file to catch variables not in os.environ
        env_file = self._detect_env_file()
        if env_file and Path(env_file).exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        if key.startswith('DATABASE_URL_') and key != 'DATABASE_URL' and value:
                            db_name = key[len('DATABASE_URL_'):].lower()
                            if db_name not in additional_dbs:  # Don't override os.environ
                                additional_dbs[db_name] = value
        
        return additional_dbs
    
    # Computed properties
    @computed_field
    @property
    def database_engine(self) -> str:
        """Database engine type (postgresql/mysql/sqlite)."""
        if self.database_url.startswith('postgresql'):
            return 'postgresql'
        elif self.database_url.startswith('mysql'):
            return 'mysql'
        elif self.database_url.startswith('sqlite'):
            return 'sqlite'
        else:
            return 'unknown'
    
    @computed_field
    @property
    def is_sqlite(self) -> bool:
        """True if using SQLite database."""
        return self.database_engine == 'sqlite'
    
    @computed_field
    @property
    def is_postgresql(self) -> bool:
        """True if using PostgreSQL database."""
        return self.database_engine == 'postgresql'
    
    @computed_field
    @property
    def is_mysql(self) -> bool:
        """True if using MySQL database."""
        return self.database_engine == 'mysql'
    
    @computed_field
    @property
    def has_multiple_databases(self) -> bool:
        """True if multiple databases are configured."""
        return any([
            self.read_replica_url,
            self.cache_db_url,
            self.analytics_db_url,
        ]) or len(self._get_additional_databases()) > 0
    
    def _parse_database_url(self, url: str) -> Dict[str, Any]:
        """Parse database URL into Django database configuration."""
        try:
            config: Dict[str, Any] = dj_database_url.parse(url)
            
            # Add our custom settings
            config.update({
                'CONN_MAX_AGE': self.conn_max_age,
                'CONN_HEALTH_CHECKS': self.conn_health_checks,
            })
            
            # Add SSL settings for PostgreSQL/MySQL
            if not self.is_sqlite:
                options: Dict[str, Any] = config.get('OPTIONS', {})
                
                if self.ssl_require:
                    options['sslmode'] = self.ssl_mode
                
                if options:
                    config['OPTIONS'] = options
            
            # SQLite-specific settings
            if self.is_sqlite:
                options = config.get('OPTIONS', {})
                options.update({
                    'timeout': self.query_timeout,
                    'isolation_level': None,  # Autocommit mode
                })
                config['OPTIONS'] = options
            
            return config
            
        except Exception as e:
            raise ValueError(f"Invalid database URL: {e}") from e
    
    def _validate_production(self) -> bool:
        """Validate production database requirements."""
        errors: List[str] = []
        
        # SQLite not recommended for production
        if self.is_sqlite:
            errors.append("SQLite is not recommended for production use")
        
        # SSL should be enabled for production
        if not self.is_sqlite and not self.ssl_require:
            errors.append("SSL should be enabled for production databases")
        
        # Connection limits
        if self.max_connections < 10:
            errors.append("Connection pool should be at least 10 for production")
        
        if errors:
            print("❌ Database production validation errors:")
            for error in errors:
                print(f"   - {error}")
            return False
        
        return True
    
    def get_database_routing_rules(self) -> Dict[str, str]:
        """Get database routing rules for apps."""
        routing_rules: Dict[str, str] = {}
        
        # Add routing rules for predefined databases
        if self.read_replica_url:
            routing_rules.update({
                'analytics': 'read_replica',
                'reports': 'read_replica',
            })
        
        if self.cache_db_url:
            routing_rules.update({
                'cache': 'cache_db',
                'sessions': 'cache_db',
            })
        
        if self.analytics_db_url:
            routing_rules.update({
                'data_analytics': 'analytics',
                'metrics': 'analytics',
            })
        
        # 🔥 Universal routing rules based on detected databases
        additional_dbs = self._get_additional_databases()
        for db_name in additional_dbs.keys():
            # Smart app mapping based on database names
            if 'cars' in db_name:
                routing_rules.update({
                    'data_cars': db_name,
                    'data_encar': db_name,
                    'data_parsers': db_name,
                })
            elif 'analytics' in db_name:
                routing_rules.update({
                    'analytics': db_name,
                    'metrics': db_name,
                })
            elif 'cache' in db_name:
                routing_rules.update({
                    'cache': db_name,
                    'sessions': db_name,
                })
        
        return routing_rules
    
    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django DATABASES setting with routing."""
        databases: Dict[str, Dict[str, Any]] = {
            'default': self._parse_database_url(self.database_url)
        }
        
        # Add predefined optional databases
        if self.read_replica_url:
            databases['read_replica'] = self._parse_database_url(self.read_replica_url)
        
        if self.cache_db_url:
            databases['cache_db'] = self._parse_database_url(self.cache_db_url)
        
        if self.analytics_db_url:
            databases['analytics'] = self._parse_database_url(self.analytics_db_url)
        
        # 🔥 Universal addition of all DATABASE_URL_* from environment
        additional_dbs = self._get_additional_databases()
        for db_name, db_url in additional_dbs.items():
            databases[db_name] = self._parse_database_url(db_url)
        
        settings: Dict[str, Any] = {'DATABASES': databases}
        
        # Add database routing if multiple databases
        if self.has_multiple_databases:
            settings['DATABASE_ROUTERS'] = ['django_cfg.routers.DatabaseRouter']
            settings['DATABASE_ROUTING_RULES'] = self.get_database_routing_rules()
        
        return settings
    
    def test_connection(self, database_name: str = 'default') -> bool:
        """Test database connection."""
        # This method should only be used in Django context
        # Import kept here as it's Django-specific functionality
        try:
            from django.db import connections
            conn = connections[database_name]
            
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None and result[0] == 1
                
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
