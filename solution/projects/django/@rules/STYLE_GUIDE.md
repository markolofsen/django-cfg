# 📝 Python Style Guide

## 🎯 Quick Summary
Consistent code formatting and naming conventions for Python projects, optimized for AI readability and team collaboration.

## 📋 Table of Contents
1. [Naming Conventions](#naming-conventions)
2. [Code Formatting](#code-formatting)
3. [Import Organization](#import-organization)
4. [Documentation Standards](#documentation-standards)
5. [Tool Configuration](#tool-configuration)

## 🔑 Key Principles at a Glance
- **Black formatting**: Non-negotiable automated formatting
- **Type hints**: Always explicit, never implicit
- **Clear names**: Descriptive over clever
- **Consistent imports**: Organized and absolute
- **Docstring standard**: Google style with type info

## 🚀 Quick Setup
```bash
# Install tools
pip install black isort flake8 mypy

# Format code
black .
isort .

# Check style
flake8 .
mypy . --strict
```

---

## 🏷️ Naming Conventions

### Variables and Functions
```python
# ✅ GOOD - Clear, descriptive names
user_data: UserModel = get_user_data(user_id=123)
processed_cars: List[CarData] = parse_car_listings(url)
is_authenticated: bool = check_user_permissions(user)

# ❌ BAD - Unclear abbreviations
ud = get_data(123)  # What is ud?
cars = parse(url)   # What kind of parsing?
auth = check(user)  # Check what?
```

### Classes and Types
```python
# ✅ GOOD - PascalCase for classes
class UserRepository:
    pass

class CarDataParser:
    pass

class DatabaseConnectionManager:
    pass

# ✅ GOOD - Descriptive type aliases
UserId = int
CarPrice = Decimal
ApiResponse = Dict[str, Any]  # Only when Pydantic not possible
```

### Constants and Enums
```python
# ✅ GOOD - ALL_CAPS for constants
MAX_RETRY_ATTEMPTS: int = 3
DATABASE_URL: str = "postgresql://..."
DEFAULT_TIMEOUT_SECONDS: int = 30

# ✅ GOOD - Enum naming
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class CarCondition(str, Enum):
    NEW = "new"
    USED = "used"
    DAMAGED = "damaged"
```

### Files and Modules
```python
# ✅ GOOD - snake_case for modules
user_repository.py
car_data_parser.py
database_connection.py

# ✅ GOOD - Package structure
src/
  models/
    user_model.py
    car_model.py
  services/
    user_service.py
    parsing_service.py
  repositories/
    user_repository.py
    car_repository.py
```

---

## 🎨 Code Formatting

### Line Length and Wrapping
```python
# ✅ GOOD - Black-compatible formatting
def process_user_data(
    user_id: int,
    include_preferences: bool = True,
    include_history: bool = False,
    timeout_seconds: int = 30,
) -> UserProcessingResult:
    """Process user data with optional includes."""
    pass

# ✅ GOOD - Method chaining
result = (
    CarDataProcessor()
    .filter_by_brand("Toyota")
    .filter_by_year_range(2020, 2024)
    .sort_by_price()
    .limit(100)
    .execute()
)

# ✅ GOOD - Long argument lists
user = UserModel(
    id=user_data.id,
    name=user_data.name,
    email=user_data.email,
    preferences=UserPreferences(
        theme="dark",
        notifications=True,
        language="en",
    ),
    created_at=datetime.utcnow(),
)
```

### Spacing and Organization
```python
# ✅ GOOD - Logical grouping with blank lines
class UserService:
    """Service for user operations."""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return await self.repository.find_by_id(user_id)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user."""
        user = User(**user_data.dict())
        return await self.repository.save(user)

    async def update_user(self, user_id: int, updates: UserUpdate) -> User:
        """Update existing user."""
        user = await self.get_user(user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")

        for field, value in updates.dict(exclude_unset=True).items():
            setattr(user, field, value)

        return await self.repository.save(user)
```

---

## 📦 Import Organization

### Import Order (isort configuration)
```python
# 1. Standard library imports
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# 2. Third-party imports
import aiohttp
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String

# 3. Local application imports
from models.user_model import User, UserCreate
from repositories.user_repository import UserRepository
from services.notification_service import NotificationService
```

### Import Styles
```python
# ✅ GOOD - Explicit imports
from typing import Dict, List, Optional
from models.user_model import User, UserCreate, UserUpdate

# ✅ GOOD - Type-only imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from services.external_service import ExternalService

# ❌ BAD - Wildcard imports
from models import *  # NEVER!
from typing import *  # NEVER!

# ❌ BAD - Relative imports
from ..models import User  # NEVER!
from .services import UserService  # NEVER!
```

---

## 📚 Documentation Standards

### Function Docstrings (Google Style)
```python
async def parse_car_listings(
    url: str,
    max_pages: int = 5,
    filters: Optional[CarFilters] = None,
) -> List[CarData]:
    """Parse car listings from website with pagination.

    Extracts car data from multiple pages with optional filtering.
    Handles rate limiting and error recovery automatically.

    Args:
        url: Base URL for car listings page
        max_pages: Maximum number of pages to parse (default: 5)
        filters: Optional filters for brand, price, etc.

    Returns:
        List of validated car data objects

    Raises:
        ParsingError: When website structure changes
        RateLimitError: When requests are blocked
        ValidationError: When car data is invalid

    Example:
        >>> filters = CarFilters(brand="Toyota", max_price=30000)
        >>> cars = await parse_car_listings(
        ...     "https://encar.com/search",
        ...     max_pages=3,
        ...     filters=filters
        ... )
        >>> print(f"Found {len(cars)} cars")
        Found 45 cars
    """
    pass
```

### Class Docstrings
```python
class CarDataParser:
    """High-performance parser for automotive listing websites.

    Provides async parsing with built-in rate limiting, error recovery,
    and data validation using Pydantic models.

    Attributes:
        session: HTTP session for requests
        rate_limiter: Controls request frequency
        validator: Validates extracted data

    Example:
        >>> parser = CarDataParser(delay_ms=1000)
        >>> async with parser:
        ...     cars = await parser.parse_search_results(url)
        ...     print(f"Parsed {len(cars)} cars")
    """

    def __init__(self, delay_ms: int = 1000):
        """Initialize parser with rate limiting.

        Args:
            delay_ms: Delay between requests in milliseconds
        """
        pass
```

---

## 🛠 Tool Configuration

### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["src", "models", "services"]

[tool.mypy]
python_version = "3.9"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.flake8]
max-line-length = 88
max-complexity = 10
extend-ignore = ["E203", "W503"]
```

### .pre-commit-config.yaml
```yaml
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
```

---

## ✅ Style Checklist

### Before Commit
- [ ] Black formatting applied (`black .`)
- [ ] Imports organized (`isort .`)
- [ ] No linting errors (`flake8 .`)
- [ ] Type checking passes (`mypy . --strict`)
- [ ] Descriptive variable names used
- [ ] Functions have docstrings with examples
- [ ] No magic numbers or strings

### Before Code Review
- [ ] All public functions documented
- [ ] Complex logic explained with comments
- [ ] Type annotations complete
- [ ] Error cases handled and documented
- [ ] Examples provided for main use cases

**Remember**: Consistent style enables better AI code generation and team collaboration. These tools are configured to work together seamlessly!
