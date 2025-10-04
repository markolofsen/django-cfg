# Django CFG Integration System

Modern, class-based integration system with configurable startup information display and modular architecture.

## Overview

The Django CFG integration system provides comprehensive startup information display with three configurable modes controlled by `DjangoConfig.startup_info_mode`:

- **`NONE`**: Minimal info only (version, environment, critical updates)
- **`SHORT`**: Essential info (apps, endpoints, status, updates) 
- **`FULL`**: Complete info (comprehensive system overview)

## Architecture

### Class-Based Display System

```
integration/
├── __init__.py                    # Main exports and entry points
├── display/                       # Modular display system
│   ├── __init__.py               # Display system exports
│   ├── base.py                   # BaseDisplayManager with common utilities
│   ├── startup.py                # StartupDisplayManager for main info
│   └── ngrok.py                  # NgrokDisplayManager for tunnel info
├── commands_collector.py         # Management commands collection
├── version_checker.py            # Version checking with cachetools
├── url_integration.py            # URL registration system
└── README.md                     # This documentation
```

### Display Managers

#### `BaseDisplayManager`
- **Purpose**: Common utilities and base functionality
- **Features**: 
  - Rich console integration
  - Panel creation with consistent styling
  - Table creation and formatting
  - Two-column layout utilities
  - Full-width panel support
  - URL generation helpers

#### `StartupDisplayManager`
- **Purpose**: Main startup information display
- **Features**:
  - Configurable display modes (NONE/SHORT/FULL)
  - Django CFG configuration panel
  - Apps and endpoints overview
  - Constance fields integration
  - Management commands breakdown
  - Background tasks status
  - Update notifications

#### `NgrokDisplayManager`
- **Purpose**: Ngrok tunnel information display
- **Features**:
  - Tunnel status and configuration
  - Active tunnel information
  - Configuration validation
  - Usage instructions

## Configuration

### In your DjangoConfig:

```python
from django_cfg.core.config import DjangoConfig, StartupInfoMode

class MyProjectConfig(DjangoConfig):
    project_name: str = "My Project"
    
    # Control startup information display
    startup_info_mode: StartupInfoMode = StartupInfoMode.FULL  # Default
    
    # ... other config
```

### Environment Variables:

```bash
# Control via environment variable
DJANGO_STARTUP_INFO_MODE=none    # Minimal
DJANGO_STARTUP_INFO_MODE=short   # Essential  
DJANGO_STARTUP_INFO_MODE=full    # Complete (default)
```

## Display Modes

### 🔴 NONE Mode
**Perfect for**: Production, CI/CD, Docker containers

**Shows**:
```
🚀 Django CFG v1.2.30 • production • My Project • 🚨 UPDATE AVAILABLE
```

**Features**:
- Single line output
- Critical information only
- Update notifications
- Minimal resource usage

### 🟡 SHORT Mode  
**Perfect for**: Development, staging, quick checks

**Shows**:
- Compact header with version and environment
- Apps grid (up to 8 apps)
- Essential endpoints (up to 6)
- System status metrics
- Update notifications
- Commands summary

**Layout**: Horizontal columns, space-efficient

### 🟢 FULL Mode
**Perfect for**: Development, debugging, system analysis

**Shows**: **COMPREHENSIVE SYSTEM OVERVIEW**

#### Main Panels (Full Width):
- **Django CFG Configuration**: Version, environment, project info, health URL
- **Update Available**: Version comparison and upgrade instructions
- **Background Tasks**: Dramatiq status, queue info, worker commands
- **Constance Fields Summary**: Dynamic settings breakdown by source
- **Management Commands**: Core, app, and project commands overview

#### Two-Column Layouts (50/50):
- **Apps & Endpoints**: Enabled apps | API endpoints
- **Payments & Configuration**: Payment status | System config
- **Core & App Commands**: Django-CFG commands | App-specific commands
- **General & Blog Settings**: Constance field details by group

#### Special Layouts:
- **Project Commands**: Two-column layout within single panel
- **Ngrok Integration**: Configuration and tunnel status

## Key Features

### ✅ **Rich Visual Layout**
- **Fixed-width panels**: Consistent 120-character width
- **50/50 column layouts**: Perfectly proportioned two-column displays
- **Full-width panels**: Single panels matching two-column width
- **Integrated blocks**: Complex layouts with nested components

### ⚙️ **Smart Configuration Integration**
- **Constance Integration**: Dynamic fields from multiple sources
  - User-defined fields
  - Tasks module fields
  - Knowbase app fields  
  - Payments app fields
- **App-specific configurations**: Payments, tasks, knowbase status
- **Environment detection**: Development, production, testing modes

### 🚀 **Performance Optimized**
- **Caching**: Version checking with TTL cache
- **Lazy loading**: App fields loaded only when needed
- **Error resilience**: Graceful degradation on failures
- **Resource efficiency**: Mode-based resource usage

### 🔄 **Modular Architecture**
- **Class inheritance**: Shared utilities via BaseDisplayManager
- **Separation of concerns**: Each manager handles specific domain
- **Extensible design**: Easy to add new display managers
- **Clean imports**: Well-organized public API

## Implementation Details

### Panel Width System

```python
# Fixed width constants for consistent layout
CONSOLE_WIDTH = 120
MAIN_PANEL_WIDTH = 120      # Full-width panels
HALF_PANEL_WIDTH = 55       # 50% width for columns

# Panel creation methods
create_panel()              # Standard width panels
create_full_width_panel()   # Full-width panels with table wrapper
print_two_column_table()    # 50/50 column layout with panels
```

### Display Flow

1. **Configuration Loading**: Get DjangoConfig instance
2. **Mode Detection**: Check startup_info_mode setting
3. **Manager Initialization**: Create appropriate display manager
4. **Information Gathering**: Collect system information
5. **Layout Rendering**: Display using Rich components
6. **Error Handling**: Graceful degradation on failures

### Integration Points

```python
# Main entry points
from django_cfg.core.integration import print_startup_info, print_ngrok_tunnel_info

# Display managers
from django_cfg.core.integration.display import (
    BaseDisplayManager,
    StartupDisplayManager, 
    NgrokDisplayManager
)

# Utilities
from django_cfg.core.integration import (
    get_version_info,
    get_all_commands,
    get_commands_with_descriptions
)
```

## Usage Examples

### Basic Usage

```python
# In your Django startup (settings.py, apps.py, etc.)
from django_cfg.core.integration import print_startup_info

# Display startup information based on config
print_startup_info()
```

### Custom Display Manager

```python
from django_cfg.core.integration.display import BaseDisplayManager

class CustomDisplayManager(BaseDisplayManager):
    def display_custom_info(self):
        # Create custom panels
        info_table = self.create_table()
        info_table.add_column("Setting", style="cyan")
        info_table.add_column("Value", style="white")
        
        # Add your data
        info_table.add_row("Custom Setting", "Custom Value")
        
        # Display as full-width panel
        panel = self.create_full_width_panel(
            info_table,
            title="Custom Information",
            border_style="green"
        )
        
        self.console.print(panel)
```

### Ngrok Integration

```python
from django_cfg.core.integration import print_ngrok_tunnel_info

# After ngrok tunnel is established
tunnel_url = "https://abc123.ngrok-free.app"
print_ngrok_tunnel_info(tunnel_url)
```

## Migration Guide

### From Old Integration System:

The new system is **fully backward compatible**:

```python
# Old usage (still works)
from django_cfg.core.integration import print_startup_info
print_startup_info()

# New usage (same result)
from django_cfg.core.integration.display import StartupDisplayManager
manager = StartupDisplayManager()
manager.display_startup_info()
```

### Customization Migration:

```python
# Old: Direct function modification
# New: Class-based extension

class MyStartupDisplayManager(StartupDisplayManager):
    def display_startup_info(self):
        # Call parent method
        super().display_startup_info()
        
        # Add custom information
        self.display_custom_section()
    
    def display_custom_section(self):
        # Your custom display logic
        pass
```

## Advanced Features

### Dynamic Constance Integration

The system automatically discovers and displays Constance fields from:
- **User-defined fields**: Manual configuration
- **App modules**: Tasks, knowbase, payments
- **Dynamic loading**: Only enabled apps contribute fields

### Command Collection

Comprehensive management command discovery:
- **Core commands**: Django-CFG framework commands
- **App commands**: Application-specific commands  
- **Project commands**: Local project commands
- **Categorization**: Automatic grouping and counting

### Version Management

Smart version checking with caching:
- **Current version**: Automatic detection via importlib
- **Latest version**: PyPI API integration
- **Caching**: TTL-based cache to prevent redundant calls
- **Update notifications**: Prominent display when updates available

## Troubleshooting

### Common Issues

1. **Panel width problems**: Check CONSOLE_WIDTH constants
2. **Import errors**: Verify display manager imports
3. **Missing information**: Check app configuration and enabled status
4. **Layout issues**: Ensure proper panel creation methods

### Debug Mode

```python
# Enable detailed error reporting
import traceback

try:
    from django_cfg.core.integration import print_startup_info
    print_startup_info()
except Exception as e:
    print(f"❌ ERROR: {e}")
    traceback.print_exc()
```

### Performance Monitoring

```python
import time
from django_cfg.core.integration.display import StartupDisplayManager

start_time = time.time()
manager = StartupDisplayManager()
manager.display_startup_info()
print(f"Display time: {time.time() - start_time:.2f}s")
```

## Future Enhancements

- **Interactive mode**: Navigate through information sections
- **Export options**: JSON/YAML output for automation
- **Custom themes**: User-defined color schemes
- **Plugin system**: Third-party display extensions
- **Performance metrics**: Built-in timing and resource monitoring
- **Configuration validation**: Real-time config checking