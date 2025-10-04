# 🤝 Contributing to Django-CFG

Thank you for your interest in contributing to Django-CFG! This project aims to make Django configuration simple, type-safe, and developer-friendly.

## 🚀 Quick Start

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/markolofsen/django-cfg.git
   cd django-cfg
   ```

2. **Install dependencies**
   ```bash
   poetry install --extras dev
   ```

3. **Run tests**
   ```bash
   poetry run pytest
   ```

## 📋 Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation if needed

3. **Test your changes**
   ```bash
   # Run all tests
   poetry run pytest
   
   # Run with coverage
   poetry run pytest --cov=django_cfg
   
   # Run linting
   poetry run black src/ tests/
   poetry run isort src/ tests/
   poetry run flake8 src/ tests/
   ```

4. **Update version and generate requirements**
   ```bash
   # Use our development CLI
   poetry run python scripts/dev_cli.py
   
   # Or manually bump version
   poetry run python scripts/version_manager.py bump --bump-type patch
   ```

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **Type Hints**: Required for all public APIs
- **Documentation**: Add docstrings for public methods
- **Tests**: Write tests for new features and bug fixes

## 🧪 Testing

### Running Tests

```bash
# All tests
poetry run pytest

# Specific test file
poetry run pytest tests/test_basic_config.py

# With coverage report
poetry run pytest --cov=django_cfg --cov-report=html
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and error cases
- Mock external dependencies

## 📝 Pull Request Process

1. **Ensure tests pass**
   ```bash
   poetry run pytest
   ```

2. **Update documentation** if your change affects the public API

3. **Create a pull request** with:
   - Clear description of changes
   - Link to any related issues
   - Screenshots for UI changes

4. **Code review** - address any feedback from maintainers

## 🐛 Bug Reports

When reporting bugs, please include:

- Django-CFG version
- Django version
- Python version
- Minimal code example
- Full error traceback

## 💡 Feature Requests

For new features:

- Check existing issues first
- Describe the use case clearly
- Provide code examples if possible
- Consider backward compatibility

## 📚 Documentation

Documentation improvements are always welcome:

- Fix typos and grammar
- Add examples and use cases
- Improve API documentation
- Update README with new features

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

All contributors will be recognized in our README and release notes.

---

**Questions?** Open an issue or start a discussion. We're here to help! 🚀
