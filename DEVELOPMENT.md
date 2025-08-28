# 🛠️ Development Setup Guide

This guide explains how to set up local development environment with django-revolution from source.

## 📁 Project Structure

```
@CARAPIS/encar_parser_new/
├── @pypi/
│   ├── django-cfg/           # This project
│   └── django-revolution/    # Local django-revolution source
```

## 🚀 Local Development Setup

### Option 1: Using pip with requirements files (Recommended)

```bash
# Navigate to django-cfg directory
cd @pypi/django-cfg

# Install for local development (uses local django-revolution)
pip install -r requirements-local.txt

# Or for production (uses PyPI django-revolution)
pip install -r requirements-production.txt
```

### Option 2: Using pip with optional dependencies

```bash
# For local development
pip install -e .[local-dev]

# For production
pip install django-cfg
```

### Option 3: Using Poetry (Alternative)

```toml
# In your project's pyproject.toml
[tool.poetry.dependencies]
# For production
django-cfg = "^1.1.3"

# For local development
django-cfg = {path = "../django-cfg", develop = true, extras = ["local-dev"]}
django-revolution = {path = "../django-revolution", develop = true}
```

## 🔄 Switching Between Environments

### Development → Production
```bash
pip uninstall django-revolution django-cfg
pip install -r requirements-production.txt
```

### Production → Development  
```bash
pip uninstall django-revolution django-cfg
pip install -r requirements-local.txt
```

## 📦 Publishing to PyPI

When publishing to PyPI, the package will automatically use the production dependencies from `pyproject.toml`:

```toml
dependencies = [
    "django-revolution>=1.0.30",  # Uses PyPI version
    # ... other deps
]
```

The `local-dev` optional dependency is only used during development and won't affect production installs.

## 🧪 Testing

```bash
# Test with local django-revolution
pip install -r requirements-local.txt
pytest

# Test with PyPI django-revolution  
pip install -r requirements-production.txt
pytest
```

## 📋 Best Practices

1. **Always use requirements files** for consistent environments
2. **Test both local and PyPI versions** before releasing
3. **Keep django-revolution version in sync** between local and PyPI
4. **Use virtual environments** to avoid conflicts

## 🔧 Troubleshooting

### Import errors with django-revolution
```bash
# Ensure both packages are installed in editable mode
pip install -e ../django-revolution
pip install -e .[local-dev]
```

### Version conflicts
```bash
# Clean install
pip uninstall django-cfg django-revolution
pip install -r requirements-local.txt
```
