# 💡 Django-CFG Usage Examples

## 🎯 Quick Summary
Comprehensive collection of real-world usage examples for the `django_cfg` module, demonstrating how to configure Django projects from simple setups to complex enterprise applications.

## 📋 Table of Contents
1. [Basic Project Setup](#basic-project-setup)
2. [Multi-Database Configuration](#multi-database-configuration)
3. [API-First Project](#api-first-project)
4. [Enterprise Application](#enterprise-application)
5. [Microservice Configuration](#microservice-configuration)
6. [Multi-Environment Setup](#multi-environment-setup)
7. [Migration Examples](#migration-examples)
8. [Advanced Patterns](#advanced-patterns)

## 🔑 Key Examples at a Glance
- **Simple Blog**: Basic Django project with minimal configuration
- **E-commerce Platform**: Multi-database with caching and APIs
- **Enterprise System**: Complex integrations with dashboard and monitoring
- **Microservice**: Lightweight configuration for service-oriented architecture
- **Multi-tenant SaaS**: Advanced routing and environment management

---

## 🚀 Basic Project Setup

### Simple Blog Application
```python
# config.py
from django_cfg import DjangoConfig, DatabaseConnection, CacheBackend

class BlogConfig(DjangoConfig):
    """Simple blog configuration"""
    
    # Project info
    project_name: str = "My Blog"
    project_version: str = "1.0.0"
    
    # Core settings
    secret_key: str = "${SECRET_KEY:django-insecure-change-me}"
    debug: bool = "${DEBUG:True}"
    allowed_hosts: List[str] = ["localhost", "127.0.0.1", "myblog.com"]
    
    # Project apps
    project_apps: List[str] = [
        "blog",
        "accounts",
        "comments",
    ]
    
    # Database
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_URL:blog_db}",
            user="${DB_USER:postgres}",
            password="${DB_PASSWORD:}",
            host="${DB_HOST:localhost}",
            port="${DB_PORT:5432}",
        )
    }
    
    # Cache
    cache_default: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://localhost:6379/1}",
        timeout=300,
    )

# Initialize configuration
config = BlogConfig()
```

```python
# settings.py
"""
Django settings for blog project
"""
from blog.config import config

# Apply ALL Django settings from pre-initialized config
globals().update(config.get_all_settings())
```

### Result: Generated Django Settings
```python
# What django_cfg generates automatically:
SECRET_KEY = 'your-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'myblog.com']

INSTALLED_APPS = [
    # Django core apps (added automatically)
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Project apps
    'blog',
    'accounts', 
    'comments',
]

MIDDLEWARE = [
    # Standard middleware (added automatically)
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'blog_db',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 5432,
        'OPTIONS': {
            'connect_timeout': 10,
            'sslmode': 'prefer',
        }
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',  # or locmem for dev
        'LOCATION': 'redis://localhost:6379/1',
        'TIMEOUT': 300,
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
            }
        }
    }
}
```

---

## 🗄️ Multi-Database Configuration

### E-commerce Platform
```python
# config.py
from django_cfg import (
    DjangoConfig, DatabaseConnection, DatabaseRoutingRule,
    CacheBackend, EmailConfig, RevolutionConfig, APIZone
)

class EcommerceConfig(DjangoConfig):
    """E-commerce platform with multiple databases"""
    
    # Project info
    project_name: str = "EcommercePlatform"
    project_apps: List[str] = [
        "products",
        "orders", 
        "payments",
        "inventory",
        "analytics",
        "accounts",
    ]
    
    # Multi-database setup
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_URL:ecommerce_main}",
            user="${DB_USER:postgres}",
            password="${DB_PASSWORD:}",
            host="${DB_HOST:localhost}",
            port="${DB_PORT:5432}",
        ),
        "products": DatabaseConnection(
            engine="django.db.backends.postgresql", 
            name="${DATABASE_URL_PRODUCTS:ecommerce_products}",
            user="${DB_USER:postgres}",
            password="${DB_PASSWORD:}",
            host="${DB_HOST:localhost}",
            port="${DB_PORT:5432}",
        ),
        "analytics": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_URL_ANALYTICS:ecommerce_analytics}",
            user="${DB_USER:postgres}",
            password="${DB_PASSWORD:}",
            host="${DB_HOST:localhost}",
            port="${DB_PORT:5432}",
        ),
    }
    
    # Database routing rules
    database_routing: List[DatabaseRoutingRule] = [
        DatabaseRoutingRule(
            apps=["products", "inventory"],
            database="products",
            operations=["read", "write", "migrate"],
            description="Product catalog and inventory management",
        ),
        DatabaseRoutingRule(
            apps=["analytics"],
            database="analytics", 
            operations=["read", "write"],
            migrate_to="default",
            description="Analytics data (migrations on main DB)",
        ),
        DatabaseRoutingRule(
            apps=["accounts", "auth", "contenttypes", "sessions", "admin"],
            database="default",
            operations=["read", "write", "migrate"],
            description="Core Django and user management",
        ),
        DatabaseRoutingRule(
            apps=["orders", "payments"],
            database="default",
            operations=["read", "write", "migrate"],
            description="Transaction and order data",
        ),
    ]
    
    # Multi-cache setup
    cache_default: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://localhost:6379/1}",
        timeout=300,
        max_connections=100,
    )
    
    cache_sessions: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://localhost:6379/2}",
        timeout=86400,  # 24 hours
    )
    
    cache_products: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://localhost:6379/3}",
        timeout=3600,  # 1 hour
    )
    
    # Email configuration
    email: EmailConfig = EmailConfig(
        host="${EMAIL_HOST:smtp.gmail.com}",
        port="${EMAIL_PORT:587}",
        username="${EMAIL_HOST_USER:}",
        password="${EMAIL_HOST_PASSWORD:}",
        use_tls="${EMAIL_USE_TLS:True}",
        default_from_email="${EMAIL_DEFAULT_FROM:orders@ecommerce.com}",
        default_from_name="Ecommerce Platform",
    )
    
    # API zones
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api/v1",
        zones={
            "public": APIZone(
                name="public",
                apps=["products"],
                title="Public API",
                description="Product catalog and search",
                public=True,
                auth_required=False,
                version="v1",
            ),
            "customer": APIZone(
                name="customer",
                apps=["orders", "accounts"],
                title="Customer API", 
                description="Customer orders and account management",
                public=True,
                auth_required=True,
                version="v1",
            ),
            "admin": APIZone(
                name="admin",
                apps=["inventory", "analytics"],
                title="Admin API",
                description="Administrative operations",
                public=False,
                auth_required=True,
                version="v1",
            ),
        }
    )
    
    # Security domains
    security_domains: List[str] = [
        "ecommerce.com",
        "api.ecommerce.com", 
        "admin.ecommerce.com",
    ]
    
    # Custom middleware
    custom_middleware: List[str] = [
        "ecommerce.middleware.RequestLoggingMiddleware",
        "ecommerce.middleware.RateLimitMiddleware",
        "ecommerce.middleware.SecurityHeadersMiddleware",
    ]

config = EcommerceConfig()
```

### Dynamic Cache Configuration
```python
# Add analytics cache dynamically
def configure_analytics_cache():
    """Add dedicated analytics cache"""
    analytics_cache = CacheBackend(
        redis_url="${REDIS_ANALYTICS_URL:redis://localhost:6379/5}",
        timeout=7200,  # 2 hours
        key_prefix="analytics:",
    )
    
    # Add to configuration
    config.cache_analytics = analytics_cache
    
    print(f"Added analytics cache: {config.cache_analytics.redis_url}")

# Usage in analytics app
from ecommerce.config import config

def get_analytics_data(key: str):
    """Get analytics data with dedicated cache"""
    # django_cfg automatically configures Django cache settings
    # We can access our custom cache via Django's cache framework
    from django.core.cache import caches
    
    analytics_cache = caches['analytics']  # Maps to config.cache_analytics
    return analytics_cache.get(f"analytics:{key}")
```

---

## 🌐 API-First Project

### Microservice Configuration
```python
# config.py
from django_cfg import (
    DjangoConfig, DatabaseConnection, CacheBackend,
    RevolutionConfig, APIZone, LoggingConfig
)

class UserServiceConfig(DjangoConfig):
    """Microservice for user management"""
    
    # Project info
    project_name: str = "UserService"
    project_version: str = "2.1.0"
    project_description: str = "User management microservice"
    
    # Minimal app list for microservice
    project_apps: List[str] = [
        "users",
        "profiles",
        "authentication",
    ]
    
    # Single database for microservice
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_URL:postgresql://user:pass@db:5432/users}",
            connect_timeout=5,  # Fast timeout for microservices
            sslmode="require",
        )
    }
    
    # Lightweight caching
    cache_default: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://redis:6379/0}",
        timeout=600,  # 10 minutes
        max_connections=20,  # Lower for microservice
    )
    
    # API-first configuration
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api",
        zones={
            "v1": APIZone(
                name="v1",
                apps=["users", "profiles"],
                title="User Service API v1",
                description="User management endpoints",
                public=True,
                auth_required=True,
                version="v1",
            ),
            "v2": APIZone(
                name="v2", 
                apps=["users", "profiles", "authentication"],
                title="User Service API v2",
                description="Enhanced user management with OAuth",
                public=True,
                auth_required=True,
                version="v2",
            ),
        }
    )
    
    # Microservice logging
    logging: LoggingConfig = LoggingConfig(
        level="INFO",
        console_output=True,
        json_format_in_prod=True,  # Structured logging for containers
        file_path="",  # No file logging in containers
    )
    
    # Security for microservice
    security_domains: List[str] = [
        "users.internal",
        "api.users.internal",
    ]
    
    # Minimal custom middleware
    custom_middleware: List[str] = [
        "users.middleware.ServiceDiscoveryMiddleware",
        "users.middleware.MetricsMiddleware",
    ]

config = UserServiceConfig()
```

### API Response Models
```python
# users/models.py - Using the same Pydantic pattern
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class UserProfile(BaseModel):
    """User profile data model"""
    
    id: int = Field(..., description="User ID")
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email address")
    first_name: str = Field(default="", max_length=100)
    last_name: str = Field(default="", max_length=100)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(..., description="Account creation date")
    last_login: Optional[datetime] = Field(default=None)
    
    class Config:
        from_attributes = True  # For Django model integration

class UserCreateRequest(BaseModel):
    """Request model for creating users"""
    
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(...)
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(default="", max_length=100)
    last_name: Optional[str] = Field(default="", max_length=100)

class UserListResponse(BaseModel):
    """Response model for user list"""
    
    users: List[UserProfile]
    total: int = Field(..., ge=0)
    page: int = Field(..., ge=1)
    per_page: int = Field(..., ge=1, le=100)
```

---

## 🏢 Enterprise Application

### Complex Enterprise Setup
```python
# config.py
from django_cfg import (
    DjangoConfig, DatabaseConnection, DatabaseRoutingRule,
    CacheBackend, EmailConfig, TelegramConfig,
    RevolutionConfig, APIZone, UnfoldConfig, DashboardConfig,
    LoggingConfig, QuickAction, NavigationItem, NavigationGroup,
    UnfoldColors, UnfoldSidebar, EnvironmentConfig
)

class EnterpriseConfig(DjangoConfig):
    """Enterprise application with full feature set"""
    
    # === Project Information ===
    project_name: str = "Enterprise Platform"
    project_version: str = "3.2.1"
    project_description: str = "Multi-tenant enterprise management platform"
    
    # === Core Settings ===
    secret_key: str = "${SECRET_KEY:}"
    debug: bool = "${DEBUG:False}"
    allowed_hosts: List[str] = [
        "enterprise.com",
        "*.enterprise.com", 
        "api.enterprise.com",
        "admin.enterprise.com",
    ]
    
    # === Custom User Model ===
    auth_user_model: str = "accounts.User"
    
    # === Project Applications ===
    project_apps: List[str] = [
        # Core modules
        "accounts",
        "organizations",
        "billing",
        "subscriptions",
        
        # Business modules  
        "projects",
        "tasks",
        "documents",
        "reports",
        
        # Integration modules
        "api",
        "webhooks",
        "notifications",
        
        # Analytics modules
        "analytics",
        "metrics",
        "auditing",
    ]
    
    # === Multi-Database Architecture ===
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_URL:postgresql://user:pass@db-main:5432/enterprise}",
            connect_timeout=10,
            sslmode="require",
            options={
                "isolation_level": "read_committed",
                "autocommit": True,
            }
        ),
        "analytics": DatabaseConnection(
            engine="django.db.backends.postgresql", 
            name="${DATABASE_ANALYTICS_URL:postgresql://user:pass@db-analytics:5432/analytics}",
            connect_timeout=15,
            sslmode="require",
        ),
        "documents": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_DOCS_URL:postgresql://user:pass@db-docs:5432/documents}",
            connect_timeout=10,
            sslmode="require",
        ),
        "audit": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_AUDIT_URL:postgresql://user:pass@db-audit:5432/audit}",
            connect_timeout=5,
            sslmode="require",
        ),
    }
    
    # === Smart Database Routing ===
    database_routing: List[DatabaseRoutingRule] = [
        DatabaseRoutingRule(
            apps=["analytics", "metrics"],
            database="analytics",
            operations=["read", "write"],
            migrate_to="default",
            description="Analytics and metrics data with read replicas",
        ),
        DatabaseRoutingRule(
            apps=["documents"],
            database="documents", 
            operations=["read", "write", "migrate"],
            description="Document storage and management",
        ),
        DatabaseRoutingRule(
            apps=["auditing"],
            database="audit",
            operations=["write"],  # Write-only for audit logs
            description="Audit trail and compliance logging",
        ),
        DatabaseRoutingRule(
            apps=["accounts", "organizations", "billing", "subscriptions"],
            database="default",
            operations=["read", "write", "migrate"],
            description="Core business data",
        ),
        DatabaseRoutingRule(
            apps=["projects", "tasks", "reports"],
            database="default",
            operations=["read", "write", "migrate"], 
            description="Primary business operations",
        ),
    ]
    
    # === Advanced Caching Strategy ===
    cache_default: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://redis-main:6379/0}",
        timeout=300,
        max_connections=200,
        key_prefix="enterprise:",
    )
    
    cache_sessions: CacheBackend = CacheBackend(
        redis_url="${REDIS_SESSIONS_URL:redis://redis-sessions:6379/0}",
        timeout=86400,  # 24 hours
        max_connections=100,
        key_prefix="sessions:",
    )
    
    cache_analytics: CacheBackend = CacheBackend(
        redis_url="${REDIS_ANALYTICS_URL:redis://redis-analytics:6379/0}",
        timeout=3600,  # 1 hour
        max_connections=50,
        key_prefix="analytics:",
    )
    
    cache_documents: CacheBackend = CacheBackend(
        redis_url="${REDIS_DOCS_URL:redis://redis-docs:6379/0}",
        timeout=7200,  # 2 hours
        max_connections=50,
        key_prefix="docs:",
    )
    
    # === Communication Services ===
    email: EmailConfig = EmailConfig(
        host="${EMAIL_HOST:smtp.enterprise.com}",
        port="${EMAIL_PORT:587}",
        username="${EMAIL_HOST_USER:noreply@enterprise.com}",
        password="${EMAIL_HOST_PASSWORD:}",
        use_tls="${EMAIL_USE_TLS:True}",
        default_from_email="${EMAIL_DEFAULT_FROM:Enterprise Platform <noreply@enterprise.com>}",
        default_from_name="Enterprise Platform",
        timeout=30,
    )
    
    telegram: TelegramConfig = TelegramConfig(
        bot_token="${TELEGRAM_BOT_TOKEN:}",
        chat_id="${TELEGRAM_ALERTS_CHAT:0}",
        parse_mode="HTML",
        disable_notification=False,
        timeout=30,
    )
    
    # === API Architecture ===
    revolution: RevolutionConfig = RevolutionConfig(
        api_prefix="api/v1",
        monorepo_enabled=True,
        monorepo_path="frontend/apps",
        zones={
            "public": APIZone(
                name="public",
                apps=["api"],
                title="Public API",
                description="Public endpoints for external integrations",
                public=True,
                auth_required=False,
                version="v1",
            ),
            "client": APIZone(
                name="client", 
                apps=["accounts", "projects", "tasks", "documents"],
                title="Client API",
                description="Main application API for authenticated users",
                public=True,
                auth_required=True,
                version="v1",
            ),
            "admin": APIZone(
                name="admin",
                apps=["organizations", "billing", "analytics", "auditing"],
                title="Administration API",
                description="Administrative operations and reporting",
                public=False,
                auth_required=True,
                version="v1",
            ),
            "webhooks": APIZone(
                name="webhooks",
                apps=["webhooks", "notifications"],
                title="Webhooks API",
                description="Webhook endpoints for external systems",
                public=True,
                auth_required=False,  # Uses signature verification
                version="v1",
            ),
        }
    )
    
    # === Advanced Dashboard Configuration ===
    dashboard: DashboardConfig = DashboardConfig(
        title="Enterprise Dashboard",
        site_header="Enterprise Platform Administration",
        site_title="Enterprise Admin",
        index_title="Welcome to Enterprise Platform",
        
        # Real-time stats with callbacks
        stats_callbacks={
            "active_users": "enterprise.dashboard.callbacks.get_active_users_count",
            "monthly_revenue": "enterprise.dashboard.callbacks.get_monthly_revenue",
            "system_health": "enterprise.dashboard.callbacks.get_system_health_status",
            "pending_tasks": "enterprise.dashboard.callbacks.get_pending_tasks_count",
            "storage_usage": "enterprise.dashboard.callbacks.get_storage_usage",
        },
        
        # Quick actions for administrators
        quick_actions=[
            QuickAction(
                title="System Backup",
                url="/admin/system/backup/",
                icon="backup",
                permission="superuser",
            ),
            QuickAction(
                title="User Reports",
                url="/admin/reports/users/",
                icon="people",
                permission="staff",
            ),
            QuickAction(
                title="API Monitoring",
                url="/admin/monitoring/api/",
                icon="monitoring",
                permission="staff",
            ),
            QuickAction(
                title="Audit Logs",
                url="/admin/audit/logs/",
                icon="security",
                permission="auditor",
            ),
        ],
        
        # Comprehensive navigation
        navigation=[
            NavigationGroup(
                title="User Management",
                items=[
                    NavigationItem(title="Users", url="/admin/accounts/user/", icon="person"),
                    NavigationItem(title="Organizations", url="/admin/organizations/organization/", icon="business"),
                    NavigationItem(title="Permissions", url="/admin/auth/permission/", icon="security"),
                ]
            ),
            NavigationGroup(
                title="Business Operations",
                items=[
                    NavigationItem(title="Projects", url="/admin/projects/project/", icon="work"),
                    NavigationItem(title="Tasks", url="/admin/tasks/task/", icon="task"),
                    NavigationItem(title="Documents", url="/admin/documents/document/", icon="description"),
                ]
            ),
            NavigationGroup(
                title="Billing & Finance",
                items=[
                    NavigationItem(title="Subscriptions", url="/admin/subscriptions/subscription/", icon="payment"),
                    NavigationItem(title="Invoices", url="/admin/billing/invoice/", icon="receipt"),
                    NavigationItem(title="Revenue Reports", url="/admin/reports/revenue/", icon="trending_up"),
                ]
            ),
            NavigationGroup(
                title="Analytics & Monitoring",
                items=[
                    NavigationItem(title="Usage Analytics", url="/admin/analytics/usage/", icon="analytics"),
                    NavigationItem(title="Performance Metrics", url="/admin/metrics/performance/", icon="speed"),
                    NavigationItem(title="System Health", url="/admin/monitoring/health/", icon="health_and_safety"),
                ]
            ),
            NavigationGroup(
                title="Integration & API",
                items=[
                    NavigationItem(title="API Keys", url="/admin/api/keys/", icon="vpn_key"),
                    NavigationItem(title="Webhooks", url="/admin/webhooks/webhook/", icon="webhook"),
                    NavigationItem(title="API Documentation", url="/api/v1/docs/", icon="api", external=True),
                ]
            ),
            NavigationGroup(
                title="System Administration",
                items=[
                    NavigationItem(title="Audit Logs", url="/admin/auditing/auditlog/", icon="security"),
                    NavigationItem(title="System Settings", url="/admin/system/settings/", icon="settings"),
                    NavigationItem(title="Backups", url="/admin/system/backups/", icon="backup"),
                ]
            ),
        ]
    )
    
    # === Unfold Dashboard Customization ===
    unfold: UnfoldConfig = UnfoldConfig(
        site_title="Enterprise Platform",
        site_header="Enterprise Administration",
        site_url="https://enterprise.com",
        theme="dark",
        
        colors=UnfoldColors(
            primary="#1976d2",
            success="#4caf50",
            info="#2196f3", 
            warning="#ff9800",
            danger="#f44336",
        ),
        
        sidebar=UnfoldSidebar(
            show_search=True,
            show_all_applications=True,
        ),
        
        dashboard_callback="enterprise.dashboard.callbacks.dashboard_callback",
        environment_callback="enterprise.dashboard.callbacks.environment_callback",
        
        styles=["admin/css/enterprise.css"],
        scripts=["admin/js/enterprise.js"],
    )
    
    # === Environment Configuration ===
    environments: EnvironmentConfig = EnvironmentConfig(
        development_config="configs/development.yaml",
        production_config="configs/production.yaml", 
        testing_config="configs/testing.yaml",
        staging_config="configs/staging.yaml",
        auto_detect=True,
    )
    
    # === Security Configuration ===
    security_domains: List[str] = [
        "enterprise.com",
        "*.enterprise.com",
        "api.enterprise.com",
        "admin.enterprise.com",
        "docs.enterprise.com",
    ]
    
    # === Advanced Logging ===
    logging: LoggingConfig = LoggingConfig(
        level="INFO",
        file_path="logs/enterprise.log",
        console_output=True,
        json_format_in_prod=True,
        max_file_size_mb=50,
        backup_count=10,
    )
    
    # === Custom Middleware Stack ===
    custom_middleware: List[str] = [
        "enterprise.middleware.TenantMiddleware",
        "enterprise.middleware.AuditLoggingMiddleware", 
        "enterprise.middleware.RateLimitingMiddleware",
        "enterprise.middleware.SecurityHeadersMiddleware",
        "enterprise.middleware.RequestTrackingMiddleware",
        "enterprise.middleware.PerformanceMonitoringMiddleware",
    ]

config = EnterpriseConfig()
```

### Environment-Specific Configurations

```yaml
# configs/production.yaml
database:
  default:
    options:
      pool_size: 20
      max_overflow: 30
      pool_timeout: 30
      
cache:
  default:
    timeout: 3600
    max_connections: 500
    
  sessions:
    timeout: 86400
    
logging:
  level: "WARNING"
  json_format_in_prod: true
  
email:
  backend: "django.core.mail.backends.smtp.EmailBackend"
  
security:
  ssl_required: true
  secure_cookies: true
  
monitoring:
  enabled: true
  metrics_endpoint: "/metrics"
  health_check_endpoint: "/health"
```

```yaml
# configs/development.yaml
database:
  default:
    options:
      pool_size: 5
      max_overflow: 10
      
cache:
  default:
    timeout: 300
    
logging:
  level: "DEBUG"
  console_output: true
  
email:
  backend: "django.core.mail.backends.console.EmailBackend"
  
security:
  ssl_required: false
  secure_cookies: false
  
debug_toolbar:
  enabled: true
```

---

## 🌍 Multi-Environment Setup

### Environment-Aware Configuration
```python
# config.py
import os
from django_cfg import DjangoConfig, EnvironmentConfig

class MultiEnvConfig(DjangoConfig):
    """Configuration that adapts to different environments"""
    
    project_name: str = "Multi-Environment App"
    
    # Environment detection
    environments: EnvironmentConfig = EnvironmentConfig(
        development_config="configs/dev.yaml",
        production_config="configs/prod.yaml",
        testing_config="configs/test.yaml",
        staging_config="configs/staging.yaml",
        auto_detect=True,
    )
    
    def __init__(self, **data):
        super().__init__(**data)
        self._configure_for_environment()
    
    def _configure_for_environment(self):
        """Apply environment-specific configuration"""
        env = self._environment
        
        if env == "development":
            self._configure_development()
        elif env == "production":
            self._configure_production()
        elif env == "testing":
            self._configure_testing()
        elif env == "staging":
            self._configure_staging()
    
    def _configure_development(self):
        """Development-specific configuration"""
        self.debug = True
        self.allowed_hosts = ["*"]
        
        # Use local databases
        self.databases = {
            "default": DatabaseConnection(
                engine="django.db.backends.sqlite3",
                name="db.sqlite3",
            )
        }
        
        # Use memory cache for development
        self.cache_default = CacheBackend(
            redis_url=None,  # Will use memory cache
            timeout=300,
        )
        
        # Console email backend
        self.email = EmailConfig(
            host="localhost",
            port=1025,  # MailHog for development
            use_tls=False,
        )
    
    def _configure_production(self):
        """Production-specific configuration"""
        self.debug = False
        self.allowed_hosts = ["myapp.com", "www.myapp.com"]
        
        # Use production databases
        self.databases = {
            "default": DatabaseConnection(
                engine="django.db.backends.postgresql",
                name="${DATABASE_URL:}",
                sslmode="require",
            )
        }
        
        # Use Redis for production
        self.cache_default = CacheBackend(
            redis_url="${REDIS_URL:}",
            timeout=3600,
            max_connections=100,
        )
        
        # Production email
        self.email = EmailConfig(
            host="${EMAIL_HOST:}",
            port=587,
            username="${EMAIL_HOST_USER:}",
            password="${EMAIL_HOST_PASSWORD:}",
            use_tls=True,
        )
    
    def _configure_testing(self):
        """Testing-specific configuration"""
        self.debug = False
        self.allowed_hosts = ["testserver"]
        
        # Use in-memory database for tests
        self.databases = {
            "default": DatabaseConnection(
                engine="django.db.backends.sqlite3",
                name=":memory:",
            )
        }
        
        # Use dummy cache for tests
        self.cache_default = CacheBackend(
            redis_url=None,
            timeout=1,  # Very short timeout for tests
        )
        
        # Dummy email backend
        self.email = EmailConfig(
            host="localhost",
            port=1025,
            use_tls=False,
        )
    
    def _configure_staging(self):
        """Staging-specific configuration"""
        self.debug = False
        self.allowed_hosts = ["staging.myapp.com"]
        
        # Use staging databases (similar to production)
        self.databases = {
            "default": DatabaseConnection(
                engine="django.db.backends.postgresql",
                name="${STAGING_DATABASE_URL:}",
                sslmode="prefer",
            )
        }
        
        # Use Redis for staging
        self.cache_default = CacheBackend(
            redis_url="${STAGING_REDIS_URL:}",
            timeout=1800,  # 30 minutes
            max_connections=50,
        )

config = MultiEnvConfig()
```

---

## 🔄 Migration Examples

### Migrating from Standard Django
```python
# BEFORE: Standard Django settings.py (100+ lines)
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'myapp',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'
WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_NAME', 'mydb'),
        'USER': os.environ.get('DATABASE_USER', 'postgres'),
        'PASSWORD': os.environ.get('DATABASE_PASSWORD', ''),
        'HOST': os.environ.get('DATABASE_HOST', 'localhost'),
        'PORT': os.environ.get('DATABASE_PORT', '5432'),
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
            }
        }
    }
}

# ... 50+ more lines of configuration
```

```python
# AFTER: Django-CFG configuration (20 lines)
# config.py
from django_cfg import DjangoConfig, DatabaseConnection, CacheBackend

class MyProjectConfig(DjangoConfig):
    """Migrated configuration using django_cfg"""
    
    project_name: str = "My Project"
    project_apps: List[str] = ["myapp"]
    
    secret_key: str = "${SECRET_KEY:dev-key}"
    debug: bool = "${DEBUG:False}"
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    databases: Dict[str, DatabaseConnection] = {
        "default": DatabaseConnection(
            engine="django.db.backends.postgresql",
            name="${DATABASE_NAME:mydb}",
            user="${DATABASE_USER:postgres}",
            password="${DATABASE_PASSWORD:}",
            host="${DATABASE_HOST:localhost}",
            port="${DATABASE_PORT:5432}",
        )
    }
    
    cache_default: CacheBackend = CacheBackend(
        redis_url="${REDIS_URL:redis://localhost:6379/1}",
        max_connections=50,
    )

config = MyProjectConfig()
```

```python
# settings.py (3 lines!)
from myproject.config import config
globals().update(config.get_all_settings())
```

### Migration Checklist
```python
# migration_checklist.py
"""
Step-by-step migration from standard Django to django_cfg
"""

def migration_steps():
    """Complete migration process"""
    
    steps = [
        # 1. Install django_cfg
        "pip install django-cfg",
        
        # 2. Create config.py
        "Create config.py with DjangoConfig subclass",
        
        # 3. Move core settings
        "Move SECRET_KEY, DEBUG, ALLOWED_HOSTS to config",
        
        # 4. Convert INSTALLED_APPS
        "Set project_apps list, django_cfg handles core apps",
        
        # 5. Convert DATABASES
        "Replace DATABASES dict with DatabaseConnection models",
        
        # 6. Convert CACHES  
        "Replace CACHES dict with CacheBackend models",
        
        # 7. Move custom middleware
        "Move custom middleware to custom_middleware list",
        
        # 8. Replace settings.py
        "Replace settings.py with config import and globals().update()",
        
        # 9. Test configuration
        "Run python manage.py check to verify configuration",
        
        # 10. Test application
        "Run full test suite to ensure everything works",
    ]
    
    return steps

def validate_migration():
    """Validate successful migration"""
    from myproject.config import config
    
    # Check configuration loads
    settings = config.get_all_settings()
    
    # Validate required settings
    required_settings = [
        'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS',
        'INSTALLED_APPS', 'MIDDLEWARE', 'DATABASES'
    ]
    
    missing = [key for key in required_settings if key not in settings]
    
    if missing:
        print(f"❌ Missing settings: {missing}")
        return False
    
    print("✅ Migration successful!")
    return True
```

---

## 🔧 Advanced Patterns

### Dynamic Configuration Loading
```python
# advanced_config.py
from django_cfg import DjangoConfig
from typing import Dict, Any
import importlib

class DynamicConfig(DjangoConfig):
    """Configuration that can be modified at runtime"""
    
    def __init__(self, **data):
        super().__init__(**data)
        self._load_plugins()
    
    def _load_plugins(self):
        """Load configuration plugins dynamically"""
        plugins = [
            'myproject.config_plugins.database_plugin',
            'myproject.config_plugins.cache_plugin',
            'myproject.config_plugins.api_plugin',
        ]
        
        for plugin_path in plugins:
            try:
                plugin = importlib.import_module(plugin_path)
                if hasattr(plugin, 'configure'):
                    plugin.configure(self)
            except ImportError:
                continue  # Plugin not available
    
    def add_database_dynamically(self, alias: str, connection: DatabaseConnection):
        """Add database connection at runtime"""
        self.databases[alias] = connection
        
        # Invalidate cached settings
        self._django_settings = None
    
    def add_api_zone_dynamically(self, zone_name: str, zone: APIZone):
        """Add API zone at runtime"""
        if not self.revolution:
            from django_cfg import RevolutionConfig
            self.revolution = RevolutionConfig(
                api_prefix="api",
                zones={}
            )
        
        self.revolution.zones[zone_name] = zone
        
        # Invalidate cached settings
        self._django_settings = None

# Plugin example
# myproject/config_plugins/database_plugin.py
def configure(config):
    """Configure additional databases based on environment"""
    if config._environment == "production":
        # Add read replica
        config.add_database_dynamically(
            "read_replica",
            DatabaseConnection(
                engine="django.db.backends.postgresql",
                name="${READ_REPLICA_URL:}",
                options={"default-transaction-isolation": "read-committed"}
            )
        )
```

### Configuration Validation and Testing
```python
# test_config.py
import pytest
from myproject.config import config

class TestConfiguration:
    """Test configuration validity"""
    
    def test_config_loads(self):
        """Test that configuration loads without errors"""
        settings = config.get_all_settings()
        assert isinstance(settings, dict)
        assert len(settings) > 0
    
    def test_required_settings_present(self):
        """Test that all required Django settings are present"""
        settings = config.get_all_settings()
        
        required = [
            'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS',
            'INSTALLED_APPS', 'MIDDLEWARE', 'DATABASES'
        ]
        
        for setting in required:
            assert setting in settings, f"Missing required setting: {setting}"
    
    def test_database_connections(self):
        """Test database connections are valid"""
        assert 'default' in config.databases
        
        default_db = config.databases['default']
        assert default_db.engine
        assert default_db.name
    
    def test_cache_configuration(self):
        """Test cache configuration is valid"""
        if config.cache_default:
            cache_config = config.cache_default.to_django_config(
                config._environment, config.debug
            )
            assert 'BACKEND' in cache_config
    
    def test_api_zones(self):
        """Test API zones configuration"""
        if config.revolution:
            assert len(config.revolution.zones) > 0
            
            for zone_name, zone in config.revolution.zones.items():
                assert zone.name == zone_name
                assert zone.apps
                assert zone.title
    
    def test_environment_detection(self):
        """Test environment is detected correctly"""
        assert config._environment in [
            'development', 'production', 'testing', 'staging'
        ]
    
    @pytest.mark.parametrize("env", ["development", "production", "testing"])
    def test_environment_specific_config(self, env, monkeypatch):
        """Test configuration adapts to different environments"""
        monkeypatch.setenv("DJANGO_ENV", env)
        
        # Create new config instance
        from myproject.config import MyProjectConfig
        test_config = MyProjectConfig()
        
        assert test_config._environment == env
        
        # Environment-specific assertions
        if env == "development":
            assert test_config.debug == True
        elif env == "production":
            assert test_config.debug == False
```

### Performance Monitoring
```python
# performance_monitoring.py
import time
from functools import wraps
from myproject.config import config

def monitor_config_performance(func):
    """Decorator to monitor configuration performance"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"⏱️  {func.__name__} took {duration:.2f}ms")
        
        # Log slow operations
        if duration > 100:  # More than 100ms
            print(f"⚠️  Slow configuration operation detected: {func.__name__}")
        
        return result
    
    return wrapper

# Monitor configuration loading
@monitor_config_performance
def load_configuration():
    """Load and return complete configuration"""
    return config.get_all_settings()

# Monitor specific operations
@monitor_config_performance  
def get_database_config():
    """Get database configuration"""
    return {
        alias: db.to_django_config()
        for alias, db in config.databases.items()
    }

# Usage
if __name__ == "__main__":
    print("🚀 Loading configuration...")
    settings = load_configuration()
    
    print("🗄️  Loading database config...")
    db_config = get_database_config()
    
    print(f"✅ Configuration loaded successfully!")
    print(f"📊 Total settings: {len(settings)}")
    print(f"🗄️  Total databases: {len(db_config)}")
```

---

**These examples demonstrate the power and flexibility of django_cfg across different project types and complexity levels. From simple blogs to complex enterprise applications, django_cfg provides consistent, type-safe, and maintainable configuration management.**
