# 🧪 Django-CFG Development Makefile
# Simple commands following KISS principles

.PHONY: help test test-unit test-integration test-apps test-core test-fast test-coverage clean lint format install dev-install

# Default target
help:
	@echo "🚀 Django-CFG Development Commands"
	@echo ""
	@echo "📋 Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-unit      - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-apps      - Run app tests (accounts, support)"
	@echo "  make test-core      - Run core configuration tests"
	@echo "  make test-fast      - Run tests (skip slow ones)"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo ""
	@echo "🔧 Development:"
	@echo "  make lint           - Run linting (ruff, mypy)"
	@echo "  make format         - Format code (black, isort)"
	@echo "  make clean          - Clean build artifacts"
	@echo "  make install        - Install package"
	@echo "  make dev-install    - Install in development mode"
	@echo ""

# Testing commands
test:
	python run_tests.py

test-unit:
	python run_tests.py --unit --verbose

test-integration:
	python run_tests.py --integration --verbose

test-apps:
	python run_tests.py --apps --verbose

test-core:
	python run_tests.py --core --verbose

test-fast:
	python run_tests.py --fast

test-coverage:
	python run_tests.py --coverage

# Development commands
lint:
	@echo "🔍 Running linting..."
	python -m ruff check src/ tests/
	python -m mypy src/

format:
	@echo "🎨 Formatting code..."
	python -m black src/ tests/ run_tests.py
	python -m isort src/ tests/ run_tests.py

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	pip install -e .

dev-install:
	pip install -e ".[dev,test]"

# Quick development workflow
dev: clean format lint test-fast
	@echo "✅ Development workflow completed!"
