# 🧪 Complete Python Testing Guide

## 🎯 Quick Summary
Comprehensive testing framework for Python projects ensuring 100% coverage, enterprise reliability, and AI-friendly test patterns with automated validation and zero regression tolerance.

## 📋 Table of Contents
1. [Testing Philosophy](#testing-philosophy)
2. [Quick Setup](#quick-setup)
3. [Testing Layers](#testing-layers)
4. [Test Patterns](#test-patterns)
5. [Quality Gates](#quality-gates)
6. [Automation & CI/CD](#automation--cicd)

## 🔑 Key Concepts at a Glance
- **100% Coverage**: No production code without comprehensive tests
- **Type-Safe Testing**: All test data uses Pydantic v2 models
- **Layer Architecture**: Unit → Integration → Performance → Security
- **Fast Feedback**: Tests execute in <60 seconds total
- **Deterministic**: Reproducible, isolated, no flaky tests

## 🚀 Quick Setup (5 minutes)

### One-Command Setup
```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-benchmark pytest-mock bandit safety

# Configure pytest.ini
cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=95
    --asyncio-mode=auto
    -v
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    security: Security tests
EOF

# Create test structure
mkdir -p tests/{unit,integration,performance,security}
touch tests/__init__.py tests/conftest.py

# Verify setup
pytest --version && echo "✅ Testing setup complete!"
```

---

## 🧪 Testing Philosophy

### Core Principles
- **🏗️ Test-First**: Tests written before or with production code
- **✅ 100% Coverage**: Every line of code must have corresponding tests
- **🔒 Type Safe**: All test data uses Pydantic v2 models for validation
- **⚡ Performance**: Tests execute fast (<60 seconds total)
- **🔄 Deterministic**: Tests must be repeatable and isolated

### Quality Standards
```python
from pydantic import BaseModel, Field
from enum import Enum

class TestQualityStandards(BaseModel):
    """Enforced test quality requirements."""

    # Coverage requirements
    unit_test_coverage: float = Field(default=100.0, ge=100.0)
    integration_coverage: float = Field(default=90.0, ge=90.0)

    # Execution requirements
    max_execution_time_seconds: int = Field(default=60, le=60)
    max_flaky_test_rate: float = Field(default=0.0, le=0.01)

    # Performance requirements
    max_test_complexity: int = Field(default=5, le=5)
    memory_leak_tolerance_mb: float = Field(default=5.0, le=5.0)

    # Security requirements
    vulnerability_count: int = Field(default=0, le=0)
    security_test_coverage: float = Field(default=100.0, ge=100.0)
```

---

## 🏗️ Testing Layers

### 🟢 Layer 1: Unit Tests (Required - 100% Coverage)
**Purpose**: Test individual components in isolation with comprehensive mocking

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.models import CarData, CarFilters
from src.services import CarService

class TestCarService:
    """Comprehensive unit tests for CarService."""

    @pytest.fixture
    def mock_repository(self):
        """Mock repository with proper interface."""
        mock_repo = AsyncMock()
        mock_repo.find_by_id.return_value = CarData(
            id=1, brand="Toyota", model="Camry", year=2023, price=25000
        )
        mock_repo.save.return_value = CarData(
            id=1, brand="Toyota", model="Camry", year=2023, price=25000
        )
        return mock_repo

    @pytest.fixture
    def service(self, mock_repository):
        """Service with mocked dependencies."""
        return CarService(repository=mock_repository)

    @pytest.mark.asyncio
    async def test_get_car_success(self, service, mock_repository):
        """Should return car data for valid ID."""
        # Act
        result = await service.get_car(1)

        # Assert
        assert result.id == 1
        assert result.brand == "Toyota"
        mock_repository.find_by_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_get_car_not_found_raises_error(self, service, mock_repository):
        """Should raise CarNotFoundError for invalid ID."""
        # Arrange
        mock_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(CarNotFoundError) as exc_info:
            await service.get_car(999)

        assert "Car with id 999 not found" in str(exc_info.value)
        assert exc_info.value.car_id == 999

    @pytest.mark.parametrize("brand,expected_count", [
        ("Toyota", 5),
        ("Honda", 3),
        ("Ford", 0),
    ])
    async def test_search_cars_by_brand(self, service, mock_repository, brand, expected_count):
        """Should filter cars by brand correctly."""
        # Arrange
        mock_cars = [
            CarData(id=i, brand=brand, model=f"Model{i}", year=2023, price=20000)
            for i in range(expected_count)
        ]
        mock_repository.search.return_value = mock_cars

        # Act
        filters = CarFilters(brand=brand)
        results = await service.search_cars(filters)

        # Assert
        assert len(results) == expected_count
        for car in results:
            assert car.brand == brand
```

### 🟡 Layer 2: Integration Tests (90% Coverage)
**Purpose**: Test component interactions with real dependencies

```python
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.services import CarService
from src.repositories import CarRepository
from src.models import CarCreate, CarData

@pytest.mark.asyncio
class TestCarServiceIntegration:
    """Integration tests with real database."""

    @pytest.fixture
    async def db_session(self):
        """Real database session for testing."""
        # Setup test database session
        async with async_session_maker() as session:
            yield session
            await session.rollback()

    @pytest.fixture
    def car_service(self, db_session):
        """Service with real repository."""
        repository = CarRepository(session=db_session)
        return CarService(repository=repository)

    async def test_create_and_retrieve_car_workflow(self, car_service):
        """Should save car to database and retrieve it."""
        # Arrange
        car_data = CarCreate(
            brand="Honda",
            model="Civic",
            year=2023,
            price=22000.00
        )

        # Act - Create car
        created_car = await car_service.create_car(car_data)

        # Act - Retrieve car
        retrieved_car = await car_service.get_car(created_car.id)

        # Assert
        assert retrieved_car is not None
        assert retrieved_car.brand == "Honda"
        assert retrieved_car.model == "Civic"
        assert created_car.id == retrieved_car.id

    async def test_search_with_complex_filters(self, car_service, sample_cars_in_db):
        """Should handle complex search filters correctly."""
        # Act
        filters = CarFilters(
            brand="Toyota",
            min_price=20000,
            max_price=30000,
            year_from=2020
        )
        results = await car_service.search_cars(filters)

        # Assert
        assert len(results) > 0
        for car in results:
            assert car.brand == "Toyota"
            assert 20000 <= car.price <= 30000
            assert car.year >= 2020
```

### 🔴 Layer 3: Performance Tests (Critical Path Benchmarks)
**Purpose**: Validate performance SLAs and detect regressions

```python
import pytest
import time
import asyncio
from memory_profiler import profile
from src.services import CarService

class TestCarServicePerformance:
    """Performance benchmarks with SLA validation."""

    @pytest.mark.benchmark
    async def test_get_car_performance(self, benchmark, car_service):
        """Car retrieval must be <100ms."""

        async def get_car_operation():
            return await car_service.get_car(1)

        # Benchmark the operation
        result = await benchmark(get_car_operation)

        # Verify SLA compliance
        assert benchmark.stats.mean < 0.1, "Car retrieval must be <100ms"
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_concurrent_request_performance(self, car_service):
        """Should handle 50 concurrent requests in <500ms."""

        # Prepare concurrent operations
        tasks = [
            car_service.get_car(i % 10 + 1)  # Cycle through 10 cars
            for i in range(50)
        ]

        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = (time.time() - start_time) * 1000  # Convert to ms

        # Verify performance
        assert len(results) == 50, "All requests must complete"
        assert total_time < 500, f"Concurrent requests took {total_time}ms, must be <500ms"
        assert all(r.id > 0 for r in results), "All requests must succeed"

    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, car_service):
        """Should maintain stable memory under extended load."""

        import psutil
        import gc

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate extended operation
        for batch in range(10):
            # Process batch of operations
            tasks = [car_service.get_car(i % 100 + 1) for i in range(100)]
            await asyncio.gather(*tasks)

            # Force garbage collection
            gc.collect()

            # Check memory usage
            current_memory = process.memory_info().rss / 1024 / 1024
            memory_increase = current_memory - initial_memory

            # Verify no significant memory leaks
            assert memory_increase < 50, f"Memory increase {memory_increase}MB must be <50MB"
```

### 🛡️ Layer 4: Security Tests (Zero Tolerance)
**Purpose**: Identify vulnerabilities and ensure secure coding patterns

```python
import pytest
import bandit
from src.services import CarService
from src.models import CarData

class TestCarServiceSecurity:
    """Security testing with zero vulnerability tolerance."""

    def test_no_sql_injection_vulnerabilities(self, car_service):
        """Should prevent SQL injection attacks."""

        # Test malicious input
        malicious_inputs = [
            "'; DROP TABLE cars; --",
            "1 OR 1=1",
            "'; DELETE FROM cars WHERE 1=1; --"
        ]

        for malicious_input in malicious_inputs:
            with pytest.raises((ValueError, ValidationError)):
                # Should validate input and reject malicious content
                await car_service.get_car(malicious_input)

    def test_input_validation_prevents_xss(self, car_service):
        """Should sanitize user input to prevent XSS."""

        malicious_script = "<script>alert('xss')</script>"

        car_data = CarCreate(
            brand=malicious_script,
            model="Test",
            year=2023,
            price=25000
        )

        # Should either reject or sanitize malicious input
        with pytest.raises(ValidationError):
            await car_service.create_car(car_data)

    def test_sensitive_data_not_logged(self, car_service, caplog):
        """Should not log sensitive information."""

        # Simulate operation with sensitive data
        await car_service.authenticate_user("secret_api_key_12345")

        # Verify sensitive data not in logs
        log_content = " ".join(record.message for record in caplog.records)
        assert "secret_api_key" not in log_content
        assert "12345" not in log_content

    @pytest.mark.security
    def test_dependency_vulnerabilities(self):
        """Should have no known security vulnerabilities in dependencies."""

        import subprocess
        import json

        # Run safety check
        result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            vulnerabilities = json.loads(result.stdout)
            pytest.fail(f"Found {len(vulnerabilities)} security vulnerabilities")
```

---

## 🔧 Test Patterns & Best Practices

### Type-Safe Test Data with Pydantic
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TestEnvironment(str, Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"

class TestConfiguration(BaseModel):
    """Type-safe test configuration."""

    environment: TestEnvironment
    coverage_threshold: float = Field(default=100.0, ge=95.0, le=100.0)
    timeout_seconds: int = Field(default=60, ge=30, le=300)
    parallel_execution: bool = Field(default=True)

    # Test selection
    test_pattern: Optional[str] = Field(default=None)
    test_markers: List[str] = Field(default_factory=list)

    # Performance settings
    benchmark_enabled: bool = Field(default=False)
    memory_profiling: bool = Field(default=False)

class MockConfiguration(BaseModel):
    """Mock object setup configuration."""

    component_name: str
    mock_type: str = Field(pattern=r"^(AsyncMock|MagicMock|Mock)$")
    return_values: dict = Field(default_factory=dict)
    side_effects: dict = Field(default_factory=dict)
    expected_calls: List[str] = Field(default_factory=list)
```

### Async Testing Patterns
```python
@pytest.mark.asyncio
class TestAsyncOperations:
    """Async testing best practices."""

    @pytest.fixture
    async def async_service(self):
        """Async service fixture with proper cleanup."""
        service = AsyncCarService()
        await service.startup()
        yield service
        await service.shutdown()

    async def test_async_operation_with_timeout(self, async_service):
        """Should handle async operations with timeout."""

        # Test with timeout
        result = await asyncio.wait_for(
            async_service.slow_operation(),
            timeout=5.0
        )

        assert result.success is True

    async def test_concurrent_operations(self, async_service):
        """Should handle multiple concurrent operations."""

        # Execute operations concurrently
        tasks = [
            async_service.process_car(f"car_{i}")
            for i in range(10)
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all succeeded
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) == 10
```

---

## 🔍 Quality Gates & Automation

### Required Quality Checks
```bash
# Complete test suite with coverage
pytest tests/ --cov=src --cov-fail-under=95 --maxfail=1

# Type checking
mypy src/ --strict

# Security scanning
bandit -r src/ -f json
safety check --json

# Code quality
black --check src/
isort --check-only src/
flake8 src/ --max-complexity=10

# Performance benchmarks
pytest tests/performance/ --benchmark-only --benchmark-sort=mean
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install -e .[test]

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-fail-under=95

      - name: Security scan
        run: |
          bandit -r src/ -f json
          safety check

      - name: Type checking
        run: |
          mypy src/ --strict

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Pre-commit Configuration
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--strict]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-r, src/]
```

---

## ❌ Testing Anti-Patterns

### Critical Violations to Avoid
```python
# ❌ WRONG - No test coverage
def new_feature():
    return "implemented"  # No tests!

# ❌ WRONG - Flaky timing-dependent test
def test_async_operation():
    start_operation()
    time.sleep(1)  # Unreliable!
    assert operation_complete()

# ❌ WRONG - Shared state between tests
global_state = {}
def test_modifies_global():
    global_state["key"] = "value"  # Affects other tests!

# ❌ WRONG - Raw data without validation
def test_with_raw_data():
    data = {"raw": "dict"}  # No type safety!
    assert process(data) == expected

# ✅ CORRECT - Complete test with type safety
@pytest.mark.asyncio
async def test_feature_comprehensive():
    """Complete test with all scenarios."""

    # Type-safe test data
    test_config = TestConfiguration(
        environment=TestEnvironment.UNIT,
        coverage_threshold=100.0
    )

    # Success case
    result = await feature_function(test_config)
    assert result.success is True

    # Error cases
    with pytest.raises(ValidationError):
        await feature_function(invalid_config)

    # Performance validation
    start_time = time.time()
    await feature_function(test_config)
    execution_time = time.time() - start_time
    assert execution_time < 0.1  # <100ms SLA
```

---

## ✅ Testing Checklist

### Before Commit
- [ ] All tests pass (`pytest`)
- [ ] Coverage >= 95% (`pytest --cov=src --cov-fail-under=95`)
- [ ] Type checking passes (`mypy src/ --strict`)
- [ ] Security scan clean (`bandit -r src/`)
- [ ] No code quality issues (`black --check`, `flake8`)

### Before Code Review
- [ ] Critical paths have 100% coverage
- [ ] Integration tests cover service interactions
- [ ] Performance tests validate SLAs
- [ ] Error cases tested with proper assertions
- [ ] Test data uses Pydantic models

### Before Production
- [ ] End-to-end tests cover user journeys
- [ ] Load tests verify system under stress
- [ ] Security tests check vulnerabilities
- [ ] All flaky tests fixed
- [ ] CI/CD pipeline passes all gates

---

## 📊 Success Metrics

### Coverage Targets
- **Unit Tests**: 100% line coverage (no exceptions)
- **Integration Tests**: 90% workflow coverage
- **Performance Tests**: All critical paths benchmarked
- **Security Tests**: Zero vulnerabilities

### Performance SLAs
- **Test Execution**: <60 seconds total
- **Individual Tests**: <100ms each
- **Memory Usage**: <5MB increase under load
- **Concurrent Operations**: Handle 50+ requests efficiently

### Quality Standards
- **Flaky Test Rate**: <1%
- **Security Vulnerabilities**: 0 allowed
- **Type Checking**: 100% mypy strict compliance
- **Code Quality**: All linting checks pass

**Remember**: Good tests enable confident refactoring and AI-assisted development. Type-safe, well-structured tests help AI understand expected behavior patterns and generate accurate code suggestions!
