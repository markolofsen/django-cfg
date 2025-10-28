---
title: Registry System - Component Discovery & Management
description: Django-CFG registry fundamentals. Comprehensive guide to registry system - component discovery & management with Pydantic validation, type safety, and enterpris
sidebar_label: Registry System
sidebar_position: 5
keywords:
  - django-cfg registry
  - django registry
---

# Registry System - Component Discovery & Management

The **Registry System** is Django-CFG's centralized component discovery and import management system. It provides automatic registration, lazy loading, and organized access to all Django-CFG components.

## Overview

The Registry System provides:

- **🔍 Automatic Discovery** - Components register themselves automatically
- **📦 Lazy Loading** - Import components only when needed
- **🏗️ Organized Structure** - Components grouped by functionality
- **🔌 Plugin Architecture** - Easy third-party integration
- **⚡ Performance Optimization** - Efficient import management
- **🛡️ Type Safety** - Full type hints and validation

## Registry Architecture

### Registry Structure

Django-CFG uses multiple specialized registries:

```python
# Combined registry structure
DJANGO_CFG_REGISTRY = {
    **CORE_REGISTRY,        # Core components (config, exceptions, etc.)
    **SERVICES_REGISTRY,    # Service integrations (email, telegram, etc.)
    **THIRD_PARTY_REGISTRY, # Third-party integrations (unfold, etc.)
    **MODULES_REGISTRY,     # Utility modules and functions
    **EXCEPTIONS_REGISTRY,  # Exception classes and handlers
}
```

### Registry Categories

#### 1. Core Registry (`CORE_REGISTRY`)

Essential Django-CFG components:

```python
CORE_REGISTRY = {
    # Core configuration
    "DjangoConfig": ("django_cfg.core.config", "DjangoConfig"),
    
    # Core exceptions
    "ConfigurationError": ("django_cfg.core.exceptions", "ConfigurationError"),
    "ValidationError": ("django_cfg.core.exceptions", "ValidationError"),
    "DatabaseError": ("django_cfg.core.exceptions", "DatabaseError"),
    
    # Database models
    "DatabaseConfig": ("django_cfg.models.database", "DatabaseConfig"),
    
    # Cache models
    "CacheConfig": ("django_cfg.models.cache", "CacheConfig"),
    
    # Security models
    "SecuritySettings": ("django_cfg.models.security", "SecuritySettings"),
    
    # Logging models
    "LoggingConfig": ("django_cfg.models.logging", "LoggingConfig"),
    
    # JWT models
    "JWTConfig": ("django_cfg.models.jwt", "JWTConfig"),
    
    # Task models
    "TaskConfig": ("django_cfg.models.tasks", "TaskConfig"),
    "DramatiqConfig": ("django_cfg.models.tasks", "DramatiqConfig"),

    # Utils
    "version_check": ("django_cfg.utils.version_check", "version_check"),

    # Routing
    "DynamicRouter": ("django_cfg.routing.routers", "DynamicRouter"),
}
```

#### 2. Services Registry (`SERVICES_REGISTRY`)

Service integrations and modules:

```python
SERVICES_REGISTRY = {
    # Email services
    "EmailConfig": ("django_cfg.models.services", "EmailConfig"),
    "DjangoEmailService": ("django_cfg.modules.django_email", "DjangoEmailService"),
    "send_email": ("django_cfg.modules.django_email", "send_email"),
    
    # Telegram services
    "TelegramConfig": ("django_cfg.models.services", "TelegramConfig"),
    "DjangoTelegram": ("django_cfg.modules.django_telegram", "DjangoTelegram"),
    "send_telegram_message": ("django_cfg.modules.django_telegram", "send_telegram_message"),
    
    # Twilio services
    "TwilioConfig": ("django_cfg.modules.django_twilio.models", "TwilioConfig"),
    "TwilioVerifyConfig": ("django_cfg.modules.django_twilio.models", "TwilioVerifyConfig"),
    
    # Logging services
    "DjangoLogger": ("django_cfg.modules.django_logger", "DjangoLogger"),
    "get_logger": ("django_cfg.modules.django_logger", "get_logger"),
}
```

#### 3. Third-Party Registry (`THIRD_PARTY_REGISTRY`)

External integrations:

```python
THIRD_PARTY_REGISTRY = {
    # Django-CFG API Client Generation
    "OpenAPIClientConfig": ("django_cfg.models.openapi_client", "OpenAPIClientConfig"),
    "GroupModel": ("django_cfg.client.config", "GroupModel"),
    
    # Unfold Admin
    "UnfoldConfig": ("django_cfg.modules.django_unfold.models.config", "UnfoldConfig"),
    "UnfoldTheme": ("django_cfg.modules.django_unfold.models.config", "UnfoldTheme"),
    "NavigationItem": ("django_cfg.modules.django_unfold.models.navigation", "NavigationItem"),

    # DRF Integration
    "DRFConfig": ("django_cfg.models.drf", "DRFConfig"),
    "DRFPaginationConfig": ("django_cfg.models.drf", "DRFPaginationConfig"),
    
    # Constance Integration
    "ConstanceConfig": ("django_cfg.models.constance", "ConstanceConfig"),
    "ConstanceFieldConfig": ("django_cfg.models.constance", "ConstanceFieldConfig"),
}
```

#### 4. Modules Registry (`MODULES_REGISTRY`)

Utility modules and functions:

```python
MODULES_REGISTRY = {
    # URL integration
    "add_django_cfg_urls": ("django_cfg.core.integration", "add_django_cfg_urls"),
    "get_django_cfg_urls_info": ("django_cfg.core.integration", "get_django_cfg_urls_info"),
    
    # Configuration utilities
    "set_current_config": ("django_cfg.core.config", "set_current_config"),
    
    # Import/Export integration
    "ImportForm": ("django_cfg.modules.django_import_export", "ImportForm"),
    "ExportForm": ("django_cfg.modules.django_import_export", "ExportForm"),
    "ImportExportMixin": ("django_cfg.modules.django_import_export", "ImportExportMixin"),
}
```

## Component Discovery

### Automatic Registration

Components register themselves automatically when imported:

```python
# Component registration happens automatically
from django_cfg import DjangoConfig, EmailConfig, DjangoEmailService

# All components are now available in the registry
```

### Manual Registration

You can also register custom components:

```python
from django_cfg.registry import register_component

# Register custom component
@register_component("MyCustomService")
class MyCustomService:
    """Custom service implementation."""
    pass

# Register with specific category
register_component("MyUtility", category="utilities")(MyUtility)
```

### Registry Access

Access registered components programmatically:

```python
from django_cfg.registry import get_component, list_components

# Get specific component
DjangoConfig = get_component("DjangoConfig")
EmailService = get_component("DjangoEmailService")

# List all components
all_components = list_components()

# List components by category
core_components = list_components(category="core")
service_components = list_components(category="services")
```

## Lazy Loading System

### Import Optimization

The registry uses lazy loading to optimize performance:

```python
# Components are not imported until actually used
from django_cfg import DjangoEmailService  # Module not loaded yet

# Component is loaded only when instantiated
email_service = DjangoEmailService()  # Now the module is loaded
```

### Lazy Import Implementation

```python
class LazyImport:
    """Lazy import wrapper for registry components."""
    
    def __init__(self, module_path: str, component_name: str):
        self.module_path = module_path
        self.component_name = component_name
        self._component = None
    
    def __call__(self, *args, **kwargs):
        """Import and instantiate component on first use."""
        if self._component is None:
            module = importlib.import_module(self.module_path)
            self._component = getattr(module, self.component_name)
        
        return self._component(*args, **kwargs)
    
    def __getattr__(self, name):
        """Delegate attribute access to the actual component."""
        if self._component is None:
            module = importlib.import_module(self.module_path)
            self._component = getattr(module, self.component_name)
        
        return getattr(self._component, name)

# Usage in registry
REGISTRY = {
    "DjangoEmailService": LazyImport(
        "django_cfg.modules.django_email", 
        "DjangoEmailService"
    )
}
```

## 🔌 Plugin Architecture

### Plugin Registration

Create and register plugins easily:

```python
from django_cfg.registry import register_plugin
from django_cfg.modules.base import BaseCfgModule

@register_plugin("my_custom_plugin")
class MyCustomPlugin(BaseCfgModule):
    """Custom plugin implementation."""
    
    def __init__(self):
        super().__init__()
        self.config = self.get_config()
    
    def process_data(self, data):
        """Process data using plugin logic."""
        return f"Processed: {data}"
    
    def health_check(self):
        """Plugin health check."""
        return {"status": "healthy", "plugin": "my_custom_plugin"}

# Plugin is automatically available
from django_cfg import MyCustomPlugin

plugin = MyCustomPlugin()
result = plugin.process_data("test data")
```

### Plugin Discovery

Discover and load plugins dynamically:

```python
from django_cfg.registry import discover_plugins, load_plugin

# Discover all available plugins
plugins = discover_plugins()
print(f"Found {len(plugins)} plugins")

# Load specific plugin
plugin_class = load_plugin("my_custom_plugin")
plugin_instance = plugin_class()

# Load all plugins of a specific type
service_plugins = discover_plugins(plugin_type="service")
for plugin_name, plugin_class in service_plugins.items():
    plugin = plugin_class()
    print(f"Loaded service plugin: {plugin_name}")
```

### Plugin Metadata

Add metadata to plugins for better discovery:

```python
from django_cfg.registry import register_plugin, PluginMetadata

@register_plugin(
    "advanced_email_plugin",
    metadata=PluginMetadata(
        name="Advanced Email Plugin",
        description="Enhanced email functionality with templates",
        version="1.0.0",
        author="Django-CFG Team",
        dependencies=["sendgrid", "jinja2"],
        tags=["email", "templates", "notifications"]
    )
)
class AdvancedEmailPlugin(BaseCfgModule):
    """Advanced email plugin with template support."""
    
    def send_templated_email(self, template, context, recipients):
        """Send email using template."""
        # Implementation here
        pass
```

## Registry Management

### Registry Inspection

Inspect registry contents and structure:

```python
from django_cfg.registry import inspect_registry, get_registry_stats

# Get registry statistics
stats = get_registry_stats()
print(f"Total components: {stats['total']}")
print(f"Core components: {stats['core']}")
print(f"Service components: {stats['services']}")

# Inspect specific component
component_info = inspect_registry("DjangoEmailService")
print(f"Module: {component_info['module']}")
print(f"Class: {component_info['class']}")
print(f"Category: {component_info['category']}")

# List all components with details
all_components = inspect_registry()
for name, info in all_components.items():
    print(f"{name}: {info['module']}.{info['class']}")
```

### Registry Validation

Validate registry integrity:

```python
from django_cfg.registry import validate_registry, RegistryValidator

# Basic validation
validation_result = validate_registry()
if validation_result.is_valid:
    print("Registry is valid")
else:
    print(f"Registry errors: {validation_result.errors}")

# Advanced validation
validator = RegistryValidator()
validator.check_imports()
validator.check_dependencies()
validator.check_duplicates()

report = validator.generate_report()
print(report)
```

### Registry Debugging

Debug registry issues:

```python
from django_cfg.registry import debug_registry, RegistryDebugger

# Debug specific component
debug_info = debug_registry("DjangoEmailService")
print(f"Import path: {debug_info['import_path']}")
print(f"Is loaded: {debug_info['is_loaded']}")
print(f"Dependencies: {debug_info['dependencies']}")

# Comprehensive debugging
debugger = RegistryDebugger()
debugger.trace_imports()
debugger.check_circular_dependencies()
debugger.analyze_load_times()

debug_report = debugger.generate_report()
print(debug_report)
```

## Advanced Registry Features

### Conditional Registration

Register components conditionally:

```python
from django_cfg.registry import register_conditional
import sys

# Register only on specific Python versions
@register_conditional(
    condition=lambda: sys.version_info >= (3, 9),
    name="ModernPythonFeature"
)
class ModernPythonFeature:
    """Feature that requires Python 3.9+."""
    pass

# Register based on installed packages
@register_conditional(
    condition=lambda: importlib.util.find_spec("redis") is not None,
    name="RedisIntegration"
)
class RedisIntegration:
    """Redis integration (only if redis is installed)."""
    pass

# Register based on configuration
@register_conditional(
    condition=lambda: getattr(settings, 'ENABLE_ADVANCED_FEATURES', False),
    name="AdvancedFeatures"
)
class AdvancedFeatures:
    """Advanced features (only if enabled in settings)."""
    pass
```

### Registry Hooks

Add hooks for registry events:

```python
from django_cfg.registry import add_registry_hook

@add_registry_hook("component_registered")
def on_component_registered(component_name, component_class):
    """Called when a component is registered."""
    print(f"Registered component: {component_name}")
    
    # Log to monitoring system
    logger.info(f"Component registered: {component_name}")

@add_registry_hook("component_loaded")
def on_component_loaded(component_name, component_instance):
    """Called when a component is first loaded."""
    print(f"Loaded component: {component_name}")
    
    # Initialize component if needed
    if hasattr(component_instance, 'initialize'):
        component_instance.initialize()

@add_registry_hook("registry_ready")
def on_registry_ready():
    """Called when registry is fully initialized."""
    print("Django-CFG registry is ready")
    
    # Perform post-initialization tasks
    validate_all_components()
    setup_monitoring()
```

### Registry Caching

Cache registry operations for performance:

```python
from django_cfg.registry import RegistryCache
from functools import lru_cache

class CachedRegistry:
    """Registry with caching support."""
    
    def __init__(self):
        self.cache = RegistryCache()
    
    @lru_cache(maxsize=128)
    def get_component(self, name: str):
        """Get component with caching."""
        return self.cache.get_or_load(name)
    
    def invalidate_cache(self, name: str = None):
        """Invalidate cache for specific component or all."""
        if name:
            self.cache.invalidate(name)
        else:
            self.cache.clear()
    
    def warm_cache(self, components: list = None):
        """Pre-load components into cache."""
        components = components or self.list_all_components()
        for component_name in components:
            self.get_component(component_name)

# Usage
registry = CachedRegistry()
registry.warm_cache(['DjangoEmailService', 'DjangoTelegram'])
```

## Registry Monitoring

### Performance Monitoring

Monitor registry performance:

```python
from django_cfg.registry import RegistryMonitor
import time

class RegistryPerformanceMonitor:
    """Monitor registry performance metrics."""
    
    def __init__(self):
        self.metrics = {
            'load_times': {},
            'access_counts': {},
            'error_counts': {}
        }
    
    def track_component_load(self, component_name: str):
        """Track component loading time."""
        start_time = time.time()
        
        try:
            component = get_component(component_name)
            load_time = time.time() - start_time
            
            self.metrics['load_times'][component_name] = load_time
            self.metrics['access_counts'][component_name] = \
                self.metrics['access_counts'].get(component_name, 0) + 1
            
            return component
            
        except Exception as e:
            self.metrics['error_counts'][component_name] = \
                self.metrics['error_counts'].get(component_name, 0) + 1
            raise
    
    def get_performance_report(self):
        """Generate performance report."""
        return {
            'slowest_components': sorted(
                self.metrics['load_times'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'most_accessed': sorted(
                self.metrics['access_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10],
            'error_prone': sorted(
                self.metrics['error_counts'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }

# Usage
monitor = RegistryPerformanceMonitor()
email_service = monitor.track_component_load('DjangoEmailService')
report = monitor.get_performance_report()
```

### Health Monitoring

Monitor registry health:

```python
from django_cfg.registry import RegistryHealthChecker

class RegistryHealthChecker:
    """Check registry health and component availability."""
    
    def check_all_components(self):
        """Check health of all registered components."""
        results = {}
        
        for component_name in list_components():
            try:
                component = get_component(component_name)
                
                # Check if component has health_check method
                if hasattr(component, 'health_check'):
                    health_result = component.health_check()
                else:
                    health_result = {"status": "unknown", "details": "No health check"}
                
                results[component_name] = {
                    "status": "healthy",
                    "component_health": health_result,
                    "loadable": True
                }
                
            except Exception as e:
                results[component_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "loadable": False
                }
        
        return results
    
    def check_dependencies(self):
        """Check component dependencies."""
        dependency_issues = []
        
        for component_name in list_components():
            try:
                component_info = inspect_registry(component_name)
                dependencies = component_info.get('dependencies', [])
                
                for dep in dependencies:
                    try:
                        importlib.import_module(dep)
                    except ImportError:
                        dependency_issues.append({
                            'component': component_name,
                            'missing_dependency': dep
                        })
                        
            except Exception as e:
                dependency_issues.append({
                    'component': component_name,
                    'error': str(e)
                })
        
        return dependency_issues

# Usage
health_checker = RegistryHealthChecker()
component_health = health_checker.check_all_components()
dependency_issues = health_checker.check_dependencies()
```

## Best Practices

### 1. Component Naming

Use consistent naming conventions:

```python
# Good: Clear, descriptive names
"DjangoEmailService"
"TwilioConfig"  
"UnfoldTheme"

# Bad: Unclear or inconsistent names
"EmailSvc"
"TwilioConf"
"Theme"
```

### 2. Lazy Loading

Always use lazy loading for optional components:

```python
# Good: Lazy loading
@register_component("OptionalService", lazy=True)
class OptionalService:
    pass

# Bad: Eager loading for optional components
import optional_service  # Loaded even if not used
```

### 3. Error Handling

Handle registry errors gracefully:

```python
from django_cfg.registry import get_component, ComponentNotFoundError

try:
    service = get_component("MyService")
except ComponentNotFoundError:
    # Fallback to default implementation
    service = DefaultService()
except ImportError as e:
    # Handle missing dependencies
    logger.warning(f"Service unavailable: {e}")
    service = None
```

### 4. Component Documentation

Document registered components:

```python
@register_component(
    "DocumentedService",
    description="Service for handling complex operations",
    version="1.0.0",
    dependencies=["requests", "pydantic"]
)
class DocumentedService:
    """
    Documented service with clear purpose and usage.
    
    This service handles complex operations with proper
    error handling and monitoring.
    """
    pass
```

### 5. Testing Registry Components

Test component registration and loading:

```python
from django.test import TestCase
from django_cfg.registry import get_component, is_registered

class RegistryTest(TestCase):
    def test_component_registration(self):
        """Test that components are properly registered."""
        self.assertTrue(is_registered("DjangoEmailService"))
        self.assertTrue(is_registered("TwilioConfig"))
    
    def test_component_loading(self):
        """Test that components can be loaded."""
        email_service = get_component("DjangoEmailService")
        self.assertIsNotNone(email_service)
    
    def test_lazy_loading(self):
        """Test that components are loaded lazily."""
        # Component should not be loaded yet
        self.assertFalse(is_loaded("DjangoEmailService"))
        
        # Load component
        service = get_component("DjangoEmailService")
        
        # Component should now be loaded
        self.assertTrue(is_loaded("DjangoEmailService"))
```

## Integration Examples

### With Django Settings

Integrate registry with Django settings:

```python
# settings.py
from django_cfg.registry import configure_registry

# Configure registry based on settings
configure_registry({
    'lazy_loading': True,
    'cache_components': True,
    'validate_on_startup': DEBUG,
    'monitor_performance': DEBUG,
})

# Register custom components from settings
DJANGO_CFG_COMPONENTS = {
    'MyCustomService': 'myapp.services.MyCustomService',
    'MyCustomConfig': 'myapp.config.MyCustomConfig',
}

for name, import_path in DJANGO_CFG_COMPONENTS.items():
    register_component_from_path(name, import_path)
```

### With Django Apps

Register components from Django apps:

```python
# apps.py
from django.apps import AppConfig
from django_cfg.registry import register_component

class MyAppConfig(AppConfig):
    name = 'myapp'
    
    def ready(self):
        # Register app-specific components
        from .services import MyAppService
        from .config import MyAppConfig
        
        register_component("MyAppService")(MyAppService)
        register_component("MyAppConfig")(MyAppConfig)
```

## Related Documentation

- [**Configuration Guide**](/fundamentals/configuration) - Configure registry behavior
- [**Modules System**](/features/modules/overview) - Use registered modules
- [**CLI Tools**](/cli/introduction) - Registry management commands
- [**Built-in Apps**](/features/built-in-apps/user-management/accounts) - Apps using registry

The Registry System provides the foundation for Django-CFG's modular architecture and component management! 🚀
