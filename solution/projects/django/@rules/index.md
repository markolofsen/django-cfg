# 🐍 Python Development Requirements

## 🎯 Quick Summary
Comprehensive requirements and standards for Python code development in AI-first projects, focusing on type safety, maintainability, and LLM-friendly code patterns.

## 📋 Table of Contents
1. [Core Requirements](#core-requirements)
2. [Development Standards](#development-standards)
3. [Quality Gates](#quality-gates)
4. [Tools & Automation](#tools--automation)
5. [Compliance Metrics](#compliance-metrics)

## 🔑 Key Documents at a Glance
- **CRITICAL_REQUIREMENTS.md**: 🚨 Zero tolerance violations and mandatory patterns
- **STYLE_GUIDE.md**: 📝 Code formatting and naming conventions
- **TESTING_STANDARDS.md**: 🧪 Testing patterns and requirements
- **PERFORMANCE_GUIDE.md**: ⚡ Performance optimization patterns

## 🚀 Quick Start

### For New Python Projects
1. Read **CRITICAL_REQUIREMENTS.md** first - these are NON-NEGOTIABLE
2. Set up tools: `mypy`, `black`, `isort`, `flake8`
3. Configure pre-commit hooks with quality gates
4. Start with Pydantic models for all data structures
5. Use complete type annotations from day one

### For Existing Python Projects
1. Run compliance audit with automated checks
2. Fix zero tolerance violations immediately
3. Migrate critical paths to Pydantic models
4. Add type annotations to public APIs
5. Implement quality gates in CI/CD

---

## 📚 Core Requirements

### 🚨 [CRITICAL_REQUIREMENTS.md](./CRITICAL_REQUIREMENTS.md) %%PRIORITY:HIGH%%
**Purpose**: Non-negotiable patterns for production Python code
**Zero tolerance**: Raw dicts, exception suppression, missing types
**Mandatory**: Pydantic everywhere, proper error handling, type annotations
**Compliance**: 100% required before merge

### 📝 [STYLE_GUIDE.md](./STYLE_GUIDE.md) %%PRIORITY:MEDIUM%%
**Purpose**: Consistent code formatting and naming conventions
**Coverage**: Naming, formatting, imports, docstrings
**Tools**: Black, isort, flake8 configuration
**Compliance**: Automated enforcement in CI/CD

### 🧪 [TESTING_STANDARDS.md](./TESTING_STANDARDS.md) %%PRIORITY:HIGH%%
**Purpose**: Testing patterns for maintainable Python code
**Coverage**: Unit tests, integration tests, mocking patterns
**Requirements**: 100% coverage for critical paths
**Compliance**: No merge without tests

### ⚡ [PERFORMANCE_GUIDE.md](./PERFORMANCE_GUIDE.md) %%PRIORITY:MEDIUM%%
**Purpose**: Performance optimization patterns and anti-patterns
**Coverage**: Async patterns, memory management, profiling
**Benchmarks**: Response time and memory usage targets
**Compliance**: Performance tests in CI/CD

---

## 🔍 Quality Gates

### 🟢 Level 1: Foundation (Required)
- [ ] MyPy strict mode passes 100%
- [ ] No raw dict/Any usage
- [ ] Complete type annotations
- [ ] Pydantic models for data structures
- [ ] Custom exception hierarchy
- [ ] No mutable default arguments

### 🟡 Level 2: Production (Required)
- [ ] Test coverage > 95%
- [ ] No functions > 20 lines
- [ ] No cyclomatic complexity > 10
- [ ] Proper async/await patterns
- [ ] Resource cleanup with context managers
- [ ] Security audit passes

### 🔴 Level 3: Enterprise (Recommended)
- [ ] Performance benchmarks met
- [ ] Memory usage within limits
- [ ] Error rate < 1%
- [ ] Documentation coverage 100%
- [ ] Code review approval
- [ ] Production monitoring ready

---

## 🛠 Tools & Automation

### Required Development Tools
```bash
# Type checking
mypy . --strict

# Code formatting
black .
isort .

# Linting
flake8 . --max-complexity=10

# Security
bandit -r .

# Testing
pytest --cov=. --cov-report=html
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
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        args: [--strict]
```

### CI/CD Quality Gates
```yaml
# GitHub Actions example
quality_check:
  steps:
    - name: Type checking
      run: mypy . --strict
    - name: Code quality
      run: flake8 . --max-complexity=10
    - name: Security scan
      run: bandit -r .
    - name: Test coverage
      run: pytest --cov=. --cov-fail-under=95
```

---

## 📊 Compliance Metrics

### Code Quality (Zero Tolerance)
- Raw Dict Usage: **0** instances
- Missing Type Annotations: **0** functions
- Bare Exception Handling: **0** instances
- Functions > 20 lines: **< 5%**
- Mutable Default Args: **0** instances

### Test Coverage (Required)
- Unit Test Coverage: **> 95%**
- Integration Test Coverage: **> 80%**
- Critical Path Coverage: **100%**
- Mock Usage: **Proper isolation**

### Performance (Benchmarks)
- Response Time: **< 200ms** for APIs
- Memory Usage: **< 100MB** per worker
- CPU Usage: **< 50%** average
- Error Rate: **< 1%** in production

---

## 🎯 Implementation Roadmap

### Week 1: Foundation
- Set up development tools and pre-commit hooks
- Audit existing code for critical violations
- Fix zero tolerance patterns immediately
- Add type annotations to public APIs

### Week 2: Quality Gates
- Implement automated quality checks
- Achieve 95%+ test coverage
- Migrate to Pydantic models
- Set up performance monitoring

### Week 3: Production Ready
- Security audit and fixes
- Performance optimization
- Documentation completion
- Team training and adoption

### Ongoing: Maintenance
- Weekly compliance reports
- Monthly performance reviews
- Quarterly standard updates
- Continuous tool improvements

---

## 🚀 Success Metrics

### Developer Experience
- **Setup time**: < 30 minutes for new developers
- **Build time**: < 5 minutes for full test suite
- **Error detection**: Caught at development time, not production
- **Code review time**: < 2 hours average

### Code Quality
- **Bug rate**: < 1 bug per 1000 lines of code
- **Technical debt**: Decreasing month over month
- **Refactoring safety**: High confidence due to type safety
- **Onboarding speed**: New developers productive in < 1 week

**Remember**: These standards are designed to work with AI development tools like Cursor. Type-safe, well-structured code enables better AI assistance and code generation accuracy.
