# Django Config Scripts

Collection of utility scripts for development, testing, and publishing.

## 📁 Scripts Overview

### Core Scripts

- **`dev_cli.py`** - Main development CLI with interactive menu
- **`version_manager.py`** - Version management and bumping
- **`publisher.py`** - Interactive PyPI publishing
- **`generate_requirements.py`** - Generate requirements.txt files
- **`test_generation.sh`** - Test generation in django_sample

## 🚀 Quick Start

### Interactive Development CLI
```bash
python scripts/dev_cli.py
```

### Direct Script Usage
```bash
# Version management
python scripts/version_manager.py get
python scripts/version_manager.py bump --bump-type patch

# Generate requirements
python scripts/generate_requirements.py

# Publish package
python scripts/publisher.py

# Test generation
./scripts/test_generation.sh
```

## 📦 Package Scripts

### Version Management
- **Get current version**: `python scripts/version_manager.py get`
- **Bump version**: `python scripts/version_manager.py bump --bump-type [major|minor|patch]`
- **Validate versions**: `python scripts/version_manager.py validate`
- **Regenerate requirements**: `python scripts/version_manager.py requirements`

### Publishing
- **Interactive publishing**: `python scripts/publisher.py`
- Supports PyPI and TestPyPI
- Automatic version bumping
- Build artifact cleanup

### Requirements Generation
- **Main dependencies**: `requirements.txt`
- **Development dependencies**: `requirements-dev.txt`
- **Minimal dependencies**: `requirements-minimal.txt`

## 🔧 Development Workflow

1. **Start development**: `python scripts/dev_cli.py`
2. **Make changes** to your code
3. **Test generation**: Use the test option in dev CLI
4. **Bump version**: Use version management
5. **Generate requirements**: Update dependency files
6. **Build package**: Create distribution files
7. **Publish**: Upload to PyPI

## 📋 Requirements Files

The `generate_requirements.py` script creates three files:

- **`requirements.txt`** - Main runtime dependencies
- **`requirements-dev.txt`** - Development dependencies (includes main)
- **`requirements-minimal.txt`** - Core dependencies only

## 🛠️ Installation

All scripts are automatically available when the package is installed:

```bash
# Install in development mode
pip install -e .

# Use package scripts
django-cfg --help
version-manager --help
publisher --help
dev-cli --help
```

## 🔍 Troubleshooting

### Import Errors
If you get import errors when running scripts directly:
1. Make sure you're in the correct directory
2. Activate the virtual environment: `source .venv/bin/activate`
3. Install dependencies: `pip install -r requirements-dev.txt`

### TOML Parsing Issues
If you get TOML parsing errors:
1. Install toml: `pip install toml`
2. The script automatically handles both `tomllib` (Python 3.11+) and `toml` package

### Permission Issues
Make scripts executable:
```bash
chmod +x scripts/*.py scripts/*.sh
```

## 📚 Integration

These scripts integrate with:
- **Django management commands**: `python manage.py cfg`
- **Package installation**: Entry points in `pyproject.toml`
- **CI/CD**: Can be used in automated workflows
- **Development tools**: Rich CLI interface with questionary

## 🎯 Best Practices

1. **Always use virtual environments**
2. **Test before publishing**
3. **Validate versions before release**
4. **Use interactive CLI for complex operations**
5. **Keep requirements files up to date** 