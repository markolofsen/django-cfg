# 🧪 Python Testing Standards (Quick Reference)

> 📚 **Full Guide**: See [TESTING_COMPLETE.md](./TESTING_COMPLETE.md) for comprehensive testing framework

## 🎯 Quick Summary
Essential testing standards and quick reference for Python projects. For complete testing patterns, setup guides, and examples, see the full testing guide.

## 📋 Table of Contents
1. [Essential Requirements](#essential-requirements)
2. [Quick Setup](#quick-setup)
3. [Testing Layers](#testing-layers)
4. [Quality Checklist](#quality-checklist)
5. [Common Commands](#common-commands)

## 🔑 Key Concepts at a Glance
- **100% coverage**: For critical business logic paths
- **Fast feedback**: Unit tests < 100ms each
- **Isolation**: No shared state between tests
- **Type-safe**: All test data uses Pydantic models
- **AI-friendly**: Clear test names and assertions

---

## ⚡ Essential Requirements

### 🚨 Zero Tolerance Violations
- **No production code without tests** - 100% coverage required
- **No flaky tests** - All tests must be deterministic
- **No raw dict/Any in tests** - Use Pydantic models for test data
- **No shared state** - Tests must be completely isolated
- **No slow tests** - Total execution <60 seconds

### ✅ Mandatory Patterns
- **Type annotations** in all test functions
- **Pydantic models** for all test data
- **Async/await** for I/O operations in tests
- **Proper mocking** with AsyncMock/MagicMock
- **Clear assertions** with descriptive error messages

---

## 🚀 Quick Setup
```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-benchmark pytest-mock bandit

# Configure pytest.ini
cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
addopts = --cov=src --cov-fail-under=95 --asyncio-mode=auto -v
EOF

# Create test structure
mkdir -p tests/{unit,integration,performance}
touch tests/__init__.py tests/conftest.py

# Verify setup
pytest --version && echo "✅ Setup complete!"
```

---

## 🏗️ Testing Layers

### 🟢 Unit Tests (100% Coverage Required)
```python
@pytest.mark.asyncio
async def test_car_service_get_by_id(mock_repository):
    service = CarService(mock_repository)
    result = await service.get_car(1)
    assert result.id == 1
    mock_repository.find_by_id.assert_called_once_with(1)
```

### 🟡 Integration Tests (90% Coverage)
```python
@pytest.mark.asyncio
async def test_car_creation_workflow(db_session):
    service = CarService(CarRepository(db_session))
    car_data = CarCreate(brand="Toyota", model="Camry", year=2023, price=25000)
    result = await service.create_car(car_data)
    assert result.brand == "Toyota"
```

### 🔴 Performance Tests (Critical Paths)
```python
@pytest.mark.benchmark
async def test_car_retrieval_performance(benchmark, car_service):
    result = await benchmark(car_service.get_car, 1)
    assert benchmark.stats.mean < 0.1  # <100ms
```

---

## ✅ Quality Checklist

### Before Commit
- [ ] All tests pass (`pytest`)
- [ ] Coverage >= 95% (`pytest --cov=src --cov-fail-under=95`)
- [ ] Type checking passes (`mypy src/ --strict`)
- [ ] Security scan clean (`bandit -r src/`)
- [ ] No flaky tests in recent runs

### Before Code Review
- [ ] Critical business logic has 100% coverage
- [ ] Integration tests cover service interactions
- [ ] Error cases tested with proper assertions
- [ ] Test data uses Pydantic models
- [ ] Async tests use proper pytest-asyncio patterns

### Before Production
- [ ] End-to-end tests cover critical user journeys
- [ ] Performance tests validate response times
- [ ] Security tests check for vulnerabilities
- [ ] All tests consistently pass in CI/CD
- [ ] Load tests verify system under stress

---

## 🔧 Common Commands

### Development Testing
```bash
# Run all tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_car_service.py -v

# Run tests with specific marker
pytest -m "unit" -v
pytest -m "not slow" -v

# Run tests in parallel
pytest -n auto

# Watch for changes and re-run tests
pytest-watch
```

### Quality Gates
```bash
# Complete quality check
pytest --cov=src --cov-fail-under=95 --maxfail=1 && \
mypy src/ --strict && \
bandit -r src/ && \
black --check src/ && \
isort --check-only src/

# Performance benchmarks
pytest tests/performance/ --benchmark-only

# Security scan
bandit -r src/ -f json | jq '.results | length'  # Should be 0
safety check --json
```

### Test Data Generation
```bash
# Generate test fixtures
python scripts/generate_test_data.py

# Create mock responses
python scripts/create_mock_responses.py

# Update test snapshots
pytest --snapshot-update
```

**🔗 For complete testing patterns, setup guides, and advanced examples, see [TESTING_COMPLETE.md](./TESTING_COMPLETE.md)**

## ✅ Testing Checklist

### Before Commit
- [ ] All tests pass (`pytest`)
- [ ] Coverage >= 95% (`pytest --cov=src --cov-fail-under=95`)
- [ ] No slow tests in unit test suite
- [ ] All test names descriptive and clear
- [ ] Mock external dependencies properly

### Before Code Review
- [ ] Critical business logic has 100% coverage
- [ ] Integration tests cover service interactions
- [ ] Error cases tested with proper assertions
- [ ] Test data uses realistic domain examples
- [ ] Async tests use proper pytest-asyncio patterns

### Before Production
- [ ] End-to-end tests cover critical user journeys
- [ ] Performance tests validate response times
- [ ] Load tests verify system under stress
- [ ] Security tests check for vulnerabilities
- [ ] All flaky tests fixed or marked as expected

**Remember**: Good tests enable confident refactoring and AI-assisted development. Clear test names and assertions help AI understand expected behavior patterns!
