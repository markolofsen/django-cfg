# Django-CFG DevOps Tools v2.0

A modern, decomposed development operations solution built with Pydantic2 for type safety and logical organization.

## 🎯 Overview

This is a complete rewrite of the original Django-CFG scripts, designed with:

- **Type Safety**: All models use Pydantic2 for validation
- **Logical Organization**: Separated by responsibility into managers
- **Comprehensive Testing**: Full test coverage with pytest
- **Modern CLI**: Interactive interfaces with Rich and Questionary
- **Extensible Design**: Easy to add new functionality

## 📁 Structure

```
devops/
├── models/              # Pydantic2 data models
│   ├── version.py      # Version management models
│   ├── package.py      # Package building/publishing models
│   ├── dependency.py   # Dependency checking models
│   ├── template.py     # Template archiving models
│   └── opensource.py   # Open source preparation models
├── managers/           # Business logic managers
│   ├── base.py         # Base manager with common functionality
│   ├── version_manager.py
│   ├── dependency_manager.py
│   ├── package_manager.py
│   ├── template_manager.py
│   └── opensource_manager.py
├── cli/                # CLI interfaces
│   ├── main_cli.py     # Main interactive CLI
│   └── commands.py     # Command implementations
├── scripts/            # Direct command-line scripts
│   ├── dev_cli.py      # Main development CLI
│   ├── version_manager.py
│   ├── check_dependencies.py
│   ├── build_package.py
│   ├── generate_requirements.py
│   └── prepare_opensource.py
└── tests/              # Comprehensive test suite
    ├── test_models.py
    ├── test_managers.py
    ├── test_cli.py
    └── conftest.py
```

## 🚀 Usage

### Interactive CLI

```bash
python devops/scripts/dev_cli.py
```

The main CLI provides an interactive menu for all operations:
- 📦 Version Management
- 🔍 Dependency Checking
- 🚀 Package Operations
- 📁 Template Management
- 🌐 Opensource Preparation

### Direct Scripts

#### Version Management
```bash
python devops/scripts/version_manager.py get
python devops/scripts/version_manager.py bump --bump-type patch
python devops/scripts/version_manager.py validate
python devops/scripts/version_manager.py sync
```

#### Dependency Checking
```bash
python devops/scripts/check_dependencies.py
python devops/scripts/check_dependencies.py --update
python devops/scripts/check_dependencies.py --json
python devops/scripts/check_dependencies.py --outdated-only
```

#### Package Building
```bash
python devops/scripts/build_package.py
python devops/scripts/build_package.py --no-clean
python devops/scripts/build_package.py --no-template
```

#### Requirements Generation
```bash
python devops/scripts/generate_requirements.py
```

#### Opensource Preparation
```bash
python devops/scripts/prepare_opensource.py
python devops/scripts/prepare_opensource.py --target ./opensource
python devops/scripts/prepare_opensource.py --copy-only
```

## 🔧 Features

### Version Management
- **Type-safe version objects** with validation
- **Multiple format support** (PEP 621, Poetry)
- **Automatic synchronization** across files
- **Semantic version bumping** (major/minor/patch)

### Dependency Management
- **Parallel checking** for fast execution
- **Multiple dependency groups** (main, dev, test, optional)
- **Smart version parsing** with constraint handling
- **Automatic updates** with confirmation

### Package Management
- **Configurable build process** with options
- **Template archive creation** for distribution
- **Multiple repository support** (PyPI, TestPyPI)
- **Validation and cleanup** automation

### Template Management
- **Intelligent file filtering** with exclude patterns
- **Project name replacement** in templates
- **Archive validation** and integrity checks
- **Compression optimization** for size

### Opensource Preparation
- **Sensitive data cleaning** with pattern matching
- **File tree filtering** for public distribution
- **Automatic documentation** generation
- **Git repository initialization** support

## 🧪 Testing

Run the complete test suite:

```bash
cd devops
python -m pytest tests/ -v
```

Test specific components:

```bash
python -m pytest tests/test_models.py -v
python -m pytest tests/test_managers.py -v
python -m pytest tests/test_cli.py -v
```

## 📊 Models Overview

### VersionInfo
```python
version = VersionInfo.from_string("1.2.3")
new_version = version.bump(BumpType.PATCH)  # 1.2.4
```

### DependencyCheck
```python
check = manager.check_all_dependencies()
outdated = check.get_all_outdated_dependencies()
```

### PackageInfo
```python
package = manager.get_package_info()
config = BuildConfig(clean_dist=True, generate_requirements=True)
```

### OpensourceConfig
```python
config = OpensourceConfig(
    source_path=Path("./"),
    target_path=Path("./opensource"),
    cleanup_config=CleanupConfig(remove_dev_files=True)
)
```

## 🔄 Migration from v1.0

The new system is completely backward-compatible in terms of functionality:

1. **All original features** are preserved
2. **Enhanced type safety** with Pydantic2
3. **Better error handling** and validation
4. **Improved performance** with parallel operations
5. **Cleaner code organization** for maintenance

### Key Improvements

- **Type Safety**: All data validated with Pydantic2 models
- **Better Testing**: Comprehensive test coverage
- **Modern CLI**: Rich terminal output with progress bars
- **Flexible Configuration**: Easily customizable behavior
- **Clean Architecture**: Separated concerns and responsibilities

## 🎨 Design Principles

1. **KISS (Keep It Simple)** - Clean, readable code
2. **Type Safety** - Pydantic2 validation everywhere
3. **Separation of Concerns** - Models, managers, CLI, scripts
4. **Fail Fast** - Early validation and clear error messages
5. **Extensibility** - Easy to add new features
6. **Testing** - Comprehensive coverage for reliability

## 📝 Requirements

- Python 3.12+
- pydantic>=2.0.0
- rich>=13.0.0
- questionary>=2.0.0
- tomlkit>=0.12.0

## 🤝 Contributing

1. All code follows PEP8 standards
2. Type hints are required
3. Tests must be written for new features
4. Documentation should be updated
5. Use the existing patterns and structure

## 📄 License

MIT License - see LICENSE file for details.
