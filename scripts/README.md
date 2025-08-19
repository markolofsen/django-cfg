# Django-CFG Scripts

Collection of utility scripts for development, testing, and publishing.

## 📁 Scripts Overview

### Core Scripts

- **`dev_cli.py`** - Main development CLI with interactive menu
- **`version_manager.py`** - Version management and bumping using tomlkit
- **`publisher.py`** - Interactive PyPI publishing
- **`generate_requirements.py`** - Generate requirements.txt files using Poetry
- **`sync_versions.py`** - Synchronize versions across all files

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
python scripts/version_manager.py validate

# Sync versions
python scripts/sync_versions.py

# Generate requirements
python scripts/generate_requirements.py

# Publish package
python scripts/publisher.py
```

## 📦 Package Scripts

### Version Management
- **Get current version**: `python scripts/version_manager.py get`
- **Bump version**: `python scripts/version_manager.py bump --bump-type [major|minor|patch]`
- **Validate versions**: `python scripts/version_manager.py validate`
- **Sync all versions**: `python scripts/sync_versions.py`

### Publishing
- **Interactive publishing**: `python scripts/publisher.py`
- Supports PyPI and TestPyPI
- Automatic version bumping
- Build artifact cleanup
- Uses `twine` for secure uploads

### Requirements Generation
- **Main dependencies**: `requirements.txt`
- **Development dependencies**: `requirements-dev.txt`
- Generated using Poetry export for accuracy

## 🔧 Development Workflow

1. **Start development**: `python scripts/dev_cli.py`
2. **Make changes** to your code
3. **Run tests**: Use the test option in dev CLI
4. **Bump version**: Use version management (updates pyproject.toml and __init__.py)
5. **Generate requirements**: Update dependency files using Poetry
6. **Build package**: Create distribution files
7. **Publish**: Upload to PyPI

## 📋 Requirements Files

The `generate_requirements.py` script creates two files using Poetry:

- **`requirements.txt`** - Main runtime dependencies
- **`requirements-dev.txt`** - Development dependencies (includes main)

Both files are generated with:
- Proper headers indicating auto-generation
- No version hashes for better readability
- Sorted dependencies

## 🛠️ Version Management

The version manager uses `tomlkit` for safe TOML manipulation:

1. **Reads version** from `pyproject.toml` (supports both PEP 621 and Poetry formats)
2. **Updates version** in:
   - `pyproject.toml` 
   - `src/django_cfg/__init__.py`
3. **Generates requirements** automatically after version bump
4. **Validates consistency** across all files

## 🔍 Troubleshooting

### Import Errors
If you get import errors when running scripts directly:
1. Make sure you're in the correct directory
2. Activate the virtual environment: `poetry shell`
3. Install dependencies: `poetry install`

### Poetry Issues
If Poetry commands fail:
1. Install Poetry: `pip install poetry`
2. Update Poetry: `poetry self update`
3. Install project dependencies: `poetry install`

### Permission Issues
Make scripts executable:
```bash
chmod +x scripts/*.py
```

## 📚 Integration

These scripts integrate with:
- **Poetry**: For dependency management and building
- **tomlkit**: For safe TOML file manipulation
- **Rich**: For beautiful CLI output
- **Questionary**: For interactive prompts
- **Twine**: For secure PyPI uploads

## 🎯 Best Practices

1. **Always use Poetry** for dependency management
2. **Test before publishing** using TestPyPI
3. **Validate versions** before release
4. **Use interactive CLI** for complex operations
5. **Keep requirements files up to date** with Poetry export
6. **Use semantic versioning** (major.minor.patch)

## 🔄 Automation

These scripts support automation:
- **CI/CD integration**: All scripts can run non-interactively
- **Automatic requirements generation**: Triggered by version bumps  
- **Version synchronization**: Ensures consistency across files
- **Build and publish**: Streamlined release process