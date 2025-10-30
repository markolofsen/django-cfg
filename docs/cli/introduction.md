---
title: CLI Tools Introduction
description: Django-CFG CLI introduction commands. Command-line interface for cli tools introduction with examples, options, and production workflows.
sidebar_label: Introduction
sidebar_position: 1
keywords:
  - django-cfg introduction
  - django-cfg command introduction
  - cli introduction
---

# CLI Tools Introduction

Django-CFG provides a powerful command-line interface built with **Click** for project management, development, and deployment tasks.

## Overview

The CLI system includes:

- **Project Creation** - Bootstrap new Django projects with full Django-CFG setup
- **Information Display** - Check installation status and dependencies
- **Enhanced Commands** - Improved versions of standard Django management commands
- **Development Tools** - Utilities for configuration validation and debugging

## Installation

The CLI is automatically available after installing Django-CFG:

```bash
# Install Django-CFG
pip install django-cfg

# Verify CLI is available
django-cfg --help
```

## Quick Start

### Create a New Project

```bash
# Create project in current directory
django-cfg create-project "My Awesome Project"

# Create project in specific location
django-cfg create-project "My Project" --path ./projects/

# Skip automatic dependency installation
django-cfg create-project "My Project" --no-deps

# Use pip instead of Poetry
django-cfg create-project "My Project" --use-pip
```

### Check System Information

```bash
# Basic information
django-cfg info

# Detailed information with paths
django-cfg info --verbose
```

## Enhanced Management Commands

Django-CFG projects include enhanced versions of standard Django commands:

```bash
# In your Django-CFG project directory
cd my_project/

# Enhanced runserver with better output
poetry run cli runserver --port 8080 --host 0.0.0.0

# Smart migrator with automatic database detection
poetry run cli migrator --auto

# Configuration validation
poetry run cli validate-config --show-details

# Show project URLs in table format
poetry run cli show-urls --format table

# Enhanced superuser creation
poetry run cli superuser --email admin@example.com
```

## Features

### Rich Output

The CLI uses **Rich** library for beautiful, colored output:

- ✅ **Success indicators** with green checkmarks
- ⚠️ **Warnings** with yellow alerts  
- ❌ **Errors** with red crosses
- 📦 **Progress indicators** for long operations
- 🎨 **Syntax highlighting** for code and configuration

### Smart Defaults

- **Auto-detection** of Poetry vs pip environments
- **Intelligent fallbacks** when commands fail
- **Environment-aware** configuration loading
- **Dependency checking** with helpful error messages

### Type Safety

All CLI commands use **Click** with full type hints:

```python
@click.command()
@click.argument("project_name", type=str)
@click.option("--port", type=int, default=8000)
@click.option("--debug", is_flag=True)
def runserver(project_name: str, port: int, debug: bool):
    """Enhanced runserver command."""
    pass
```

## Development Mode

When developing Django-CFG itself, additional commands are available:

```bash
# Create template archive for project creation
python scripts/template_manager.py create

# Validate all configurations
python scripts/validate_configs.py

# Run comprehensive tests
python scripts/test_all.py
```

## Command Categories

### Project Management
- `create-project` - Create new Django projects
- `info` - System and installation information

### Development Tools  
- `runserver` - Enhanced development server
- `migrator` - Smart database migrations
- `validate-config` - Configuration validation

### Utilities
- `show-config` - Display current configuration
- `show-urls` - List all URL patterns
- `superuser` - Enhanced superuser creation
- `test-email` - Test email configuration
- `test-telegram` - Test Telegram integration

## Integration with Django

Django-CFG CLI commands seamlessly integrate with standard Django management:

```bash
# Standard Django commands still work
python manage.py runserver
python manage.py migrate

# Enhanced CLI commands provide better UX
poetry run cli runserver    # Better output, more options
poetry run cli migrator     # Smart database detection
```

## Command Reference

### Core Commands
- **[Core Commands](/cli/commands/core-commands)** - Essential project management commands (info, create-project, validate-config)
- **[Development Commands](/cli/commands/development)** - Development server, migrations, debugging tools
- **[Custom Commands](/cli/custom-commands)** - Create your own management commands

### Feature-Specific Commands
- **[AI Agent Commands](/cli/commands/ai-agents)** - Manage AI workflows and agent execution
- **[Knowledge Base Commands](/cli/commands/knowbase)** - Document ingestion and semantic search
- **[Background Task Commands](/features/integrations/rearq/overview)** - Manage ReArq workers and tasks
- **[Payment Commands](/cli/commands/payments)** - Test payment integrations and webhooks
- **[Maintenance Commands](/cli/commands/maintenance)** - Enable/disable maintenance mode

### Guides & Configuration
- **[Configuration Guide](/fundamentals/configuration)** - Configure CLI behavior and defaults
- **[Production Best Practices](/guides/production-config)** - CLI usage in production
- **[Troubleshooting](/guides/troubleshooting)** - Common CLI issues

## Tips & Best Practices

1. **Use Poetry** - Django-CFG projects work best with Poetry for dependency management
2. **Enable Auto-completion** - Most terminals support Click auto-completion:
   ```bash
   # Bash
   eval "$(_DJANGO_CFG_COMPLETE=bash_source django-cfg)"

   # Zsh
   eval "$(_DJANGO_CFG_COMPLETE=zsh_source django-cfg)"
   ```
3. **Check Dependencies** - Use `django-cfg info --verbose` to verify your setup
4. **Read Help** - Every command has detailed help with `--help` flag
5. **Chain Commands** - Combine multiple commands for complex workflows
6. **Use Environment Variables** - Configure defaults via `DJANGO_CFG_*` environment variables

The CLI is designed to make Django development faster, safer, and more enjoyable! 🚀

## See Also

### CLI Commands

**Core Commands:**
- **[Core Commands](/cli/commands/core-commands)** - Essential project management commands
- **[Development Commands](/cli/commands/development)** - Development server and debugging tools
- **[Custom Commands](/cli/custom-commands)** - Create your own management commands
- **[Quick Reference](/cli/commands/quick-reference)** - Command cheat sheet

**Feature Commands:**
- **[AI Agent Commands](/cli/commands/ai-agents)** - Manage AI workflows and agents
- **[Knowledge Base Commands](/cli/commands/knowbase)** - Document ingestion and search
- **[Background Task Commands](/features/integrations/rearq/overview)** - Manage ReArq workers
- **[Payment Commands](/cli/commands/payments)** - Test payment integrations
- **[Maintenance Commands](/cli/commands/maintenance)** - Site maintenance control

### Getting Started

**Project Setup:**
- **[Installation](/getting-started/installation)** - Install Django-CFG
- **[First Project](/getting-started/first-project)** - Complete tutorial
- **[Configuration Guide](/getting-started/configuration)** - Configure your project
- **[Why Django-CFG](/getting-started/why-django-cfg)** - Benefits and features

**Configuration:**
- **[Configuration Models](/fundamentals/configuration)** - All configuration options
- **[Type-Safe Configuration](/fundamentals/core/type-safety)** - Pydantic patterns
- **[Environment Detection](/fundamentals/configuration/environment)** - Multi-environment setup
- **[Environment Variables](/fundamentals/configuration/environment)** - Secrets management

### Features & Deployment

**Built-in Apps:**
- **[Built-in Apps Overview](/features/built-in-apps/overview)** - All available apps
- **[User Management](/features/built-in-apps/user-management/overview)** - Accounts and support
- **[AI Agents](/ai-agents/introduction)** - AI workflow automation
- **[Operations Apps](/features/built-in-apps/operations/overview)** - Maintenance and tasks

**Deployment:**
- **[Docker Deployment](/guides/docker/production)** - Containerized deployment
- **[Production Config](/guides/production-config)** - Production best practices
- **[Environment Setup](/deployment/environment-setup)** - Environment configuration
- **[Troubleshooting](/guides/troubleshooting)** - Common CLI issues
