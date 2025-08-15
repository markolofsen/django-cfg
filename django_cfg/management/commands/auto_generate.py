"""
Auto Generation Command for Django Config Toolkit
Generate configuration files, models, and other Django components.
"""

import os
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import questionary
from datetime import datetime

from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = 'Auto-generate configuration files and Django components'

    def add_arguments(self, parser):
        parser.add_argument(
            '--config',
            action='store_true',
            help='Generate configuration files only'
        )
        parser.add_argument(
            '--models',
            action='store_true',
            help='Generate model files only'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Generate all components'
        )

    def handle(self, *args, **options):
        if options['all']:
            self.generate_all()
        elif options['config']:
            self.generate_config_files()
        elif options['models']:
            self.generate_model_files()
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with generation options"""
        self.stdout.write(self.style.SUCCESS('\n🚀 Auto Generation Tool - Django Config Toolkit\n'))

        choices = [
            questionary.Choice('⚙️  Generate Configuration Files', value='config'),
            questionary.Choice('📊 Generate Model Files', value='models'),
            questionary.Choice('🔄 Generate All Components', value='all'),
            questionary.Choice('📝 Generate Environment Template', value='env'),
            questionary.Choice('🔧 Generate Settings Template', value='settings'),
            questionary.Choice('❌ Exit', value='exit')
        ]

        choice = questionary.select(
            'Select generation option:',
            choices=choices
        ).ask()

        if choice == 'config':
            self.generate_config_files()
        elif choice == 'models':
            self.generate_model_files()
        elif choice == 'all':
            self.generate_all()
        elif choice == 'env':
            self.generate_env_template()
        elif choice == 'settings':
            self.generate_settings_template()
        elif choice == 'exit':
            self.stdout.write('Goodbye! 👋')
            return

    def generate_all(self):
        """Generate all components"""
        self.stdout.write(self.style.SUCCESS('🔄 Generating all components...'))
        
        self.generate_config_files()
        self.generate_model_files()
        self.generate_env_template()
        self.generate_settings_template()
        
        self.stdout.write(self.style.SUCCESS('✅ All components generated!'))

    def generate_config_files(self):
        """Generate configuration files"""
        self.stdout.write(self.style.SUCCESS('⚙️  Generating configuration files...'))
        
        # Generate config.py
        self.generate_config_py()
        
        # Generate database config
        self.generate_database_config()
        
        # Generate security config
        self.generate_security_config()
        
        self.stdout.write(self.style.SUCCESS('✅ Configuration files generated!'))

    def generate_model_files(self):
        """Generate model files"""
        self.stdout.write(self.style.SUCCESS('📊 Generating model files...'))
        
        # Generate base models
        self.generate_base_models()
        
        # Generate API models
        self.generate_api_models()
        
        self.stdout.write(self.style.SUCCESS('✅ Model files generated!'))

    def generate_config_py(self):
        """Generate main config.py file"""
        config_content = '''"""
Configuration file for Django Config Toolkit
Auto-generated configuration with smart defaults.
"""

from django_cfg import ConfigToolkit

# Initialize configuration
config = ConfigToolkit()

# Export all settings
globals().update(config.get_django_settings())

# Type-safe access to configuration
DEBUG = config.debug
SECRET_KEY = config.secret_key
DATABASE_URL = config.database_url
ALLOWED_HOSTS = config.allowed_hosts
'''
        
        config_path = Path('config.py')
        if not config_path.exists():
            with open(config_path, 'w') as f:
                f.write(config_content)
            self.stdout.write(f'  📄 Created {config_path}')

    def generate_database_config(self):
        """Generate database configuration"""
        db_config_content = '''"""
Database Configuration
Auto-generated database settings.
"""

from django_cfg import DatabaseConfig

# Database configuration
db_config = DatabaseConfig(
    database_url="sqlite:///db.sqlite3",
    max_connections=20,
    conn_max_age=600,
    conn_health_checks=True,
    ssl_require=False,
    ssl_mode="prefer",
    query_timeout=30,
)

# Additional databases (uncomment and configure as needed)
# db_config.read_replica_url = "postgresql://user:pass@host:port/db"
# db_config.cache_db_url = "redis://localhost:6379/1"
# db_config.analytics_db_url = "postgresql://user:pass@host:port/analytics"

# Export database settings
globals().update(db_config.to_django_settings())
'''
        
        db_config_path = Path('database_config.py')
        if not db_config_path.exists():
            with open(db_config_path, 'w') as f:
                f.write(db_config_content)
            self.stdout.write(f'  📄 Created {db_config_path}')

    def generate_security_config(self):
        """Generate security configuration"""
        security_config_content = '''"""
Security Configuration
Auto-generated security settings.
"""

from django_cfg import SecurityConfig

# Security configuration
security_config = SecurityConfig(
    secret_key="your-secret-key-here",
    debug=False,
    allowed_hosts=["localhost", "127.0.0.1"],
    csrf_trusted_origins=["http://localhost:3000"],
    cors_allowed_origins=["http://localhost:3000"],
    cors_allowed_methods=["GET", "POST", "PUT", "DELETE"],
    cors_allowed_headers=["*"],
)

# Export security settings
globals().update(security_config.to_django_settings())
'''
        
        security_config_path = Path('security_config.py')
        if not security_config_path.exists():
            with open(security_config_path, 'w') as f:
                f.write(security_config_content)
            self.stdout.write(f'  📄 Created {security_config_path}')

    def generate_base_models(self):
        """Generate base model files"""
        base_models_content = '''"""
Base Models
Auto-generated base model classes.
"""

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Base model with common fields."""
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return f"{self.__class__.__name__} {self.id}"


class TimestampedModel(BaseModel):
    """Model with timestamps."""
    
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    
    class Meta:
        abstract = True
'''
        
        base_models_path = Path('models/base.py')
        base_models_path.parent.mkdir(exist_ok=True)
        
        if not base_models_path.exists():
            with open(base_models_path, 'w') as f:
                f.write(base_models_content)
            self.stdout.write(f'  📄 Created {base_models_path}')

    def generate_api_models(self):
        """Generate API model files"""
        api_models_content = '''"""
API Models
Auto-generated API model classes.
"""

from django.db import models
from .base import BaseModel


class APIModel(BaseModel):
    """Base model for API resources."""
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    
    class Meta:
        abstract = True
    
    def __str__(self):
        return self.name


class ConfigModel(APIModel):
    """Configuration model for storing settings."""
    
    key = models.CharField(max_length=255, unique=True)
    value = models.JSONField()
    value_type = models.CharField(
        max_length=50,
        choices=[
            ('string', 'String'),
            ('integer', 'Integer'),
            ('float', 'Float'),
            ('boolean', 'Boolean'),
            ('json', 'JSON'),
        ],
        default='string'
    )
    
    class Meta:
        verbose_name = 'Configuration'
        verbose_name_plural = 'Configurations'
'''
        
        api_models_path = Path('models/api.py')
        api_models_path.parent.mkdir(exist_ok=True)
        
        if not api_models_path.exists():
            with open(api_models_path, 'w') as f:
                f.write(api_models_content)
            self.stdout.write(f'  📄 Created {api_models_path}')

    def generate_env_template(self):
        """Generate environment template file"""
        env_template_content = '''# Environment Configuration Template
# Copy this file to .env and configure your settings

# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DATABASE_URL=sqlite:///db.sqlite3
# DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# DATABASE_URL=mysql://user:password@localhost:3306/dbname

# Additional Databases (optional)
# DATABASE_URL_CARS=postgresql://user:password@localhost:5432/cars_db
# DATABASE_URL_ANALYTICS=postgresql://user:password@localhost:5432/analytics_db
# DATABASE_URL_CACHE=redis://localhost:6379/1

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cache Settings
CACHE_BACKEND=django.core.cache.backends.locmem.LocMemCache
# CACHE_BACKEND=django.core.cache.backends.redis.RedisCache
# CACHE_LOCATION=redis://127.0.0.1:6379/1

# Security Settings
CSRF_TRUSTED_ORIGINS=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000

# API Settings
API_KEY=your-api-key-here
API_RATE_LIMIT=1000

# Logging Settings
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
'''
        
        env_template_path = Path('.env.template')
        if not env_template_path.exists():
            with open(env_template_path, 'w') as f:
                f.write(env_template_content)
            self.stdout.write(f'  📄 Created {env_template_path}')

    def generate_settings_template(self):
        """Generate Django settings template"""
        settings_template_content = '''"""
Django Settings Template
Auto-generated Django settings with Django Config Toolkit.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Import configuration from Django Config Toolkit
from django_cfg import ConfigToolkit

# Initialize configuration
config = ConfigToolkit()

# Export all settings
globals().update(config.get_django_settings())

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'corsheaders',
    'django_cfg',
    
    # Local apps
    # Add your apps here
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Health check URLs
HEALTH_CHECK_URLS = [
    'health/',
    'health/detailed/',
    'ready/',
    'alive/',
]
'''
        
        settings_template_path = Path('settings_template.py')
        if not settings_template_path.exists():
            with open(settings_template_path, 'w') as f:
                f.write(settings_template_content)
            self.stdout.write(f'  📄 Created {settings_template_path}')
