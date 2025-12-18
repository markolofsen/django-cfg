# 🚨 CRITICAL PYTHON REQUIREMENTS - Code Development Standards

## ⚡ ZERO TOLERANCE VIOLATIONS

Based on **production failures and code review disasters**, these patterns are **ABSOLUTELY FORBIDDEN** in Python development.

### 🚫 **FORBIDDEN PYTHON PATTERNS** %%PRODUCTION_KILLERS%%

#### ❌ Raw Dict/Any Usage (TYPE SAFETY KILLER!)

```python
# ❌ FORBIDDEN - Raw dictionaries for data
def bad_function(data: Dict[str, Any]) -> Dict:  # NEVER!
    return {"status": "success", "result": data}

# ❌ FORBIDDEN - Untyped dictionaries
config = {"host": "localhost", "port": 5432}  # NEVER!
metadata = {}  # NEVER!

# ❌ FORBIDDEN - Any type usage
def process_data(data: Any) -> Any:  # NEVER!
    return data

# ✅ CORRECT - Pydantic v2 models everywhere
from pydantic import BaseModel, Field
from typing import Annotated

class Config(BaseModel):
    host: str = "localhost"
    port: Annotated[int, Field(gt=0, le=65535)] = 5432

class Response(BaseModel):
    status: str
    result: str

def good_function(config: Config) -> Response:
    return Response(status="success", result="processed")
```

#### ❌ Exception Suppression (DEBUG NIGHTMARE!)

```python
# ❌ FORBIDDEN - Silent failures
try:
    risky_operation()
except:  # NEVER!
    pass

# ❌ FORBIDDEN - Generic exception catching
try:
    api_call()
except Exception:  # NEVER!
    return None

# ❌ FORBIDDEN - Logging without re-raising
try:
    critical_operation()
except SomeError as e:
    logger.error(f"Error: {e}")  # NEVER! - swallows error
    return default_value

# ✅ CORRECT - Specific exception handling
try:
    result = api_call()
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise  # Re-raise for proper handling
except ValidationError as e:
    logger.error(f"Invalid data: {e}")
    raise ValueError(f"Data validation failed: {e}") from e
```

#### ❌ String Manipulation for Paths/URLs (SECURITY RISK!)

```python
# ❌ FORBIDDEN - String concatenation for paths
path = "/api" + "/" + endpoint + "?" + params  # NEVER!
file_path = base_dir + "/" + filename  # NEVER!

# ❌ FORBIDDEN - String formatting for SQL
query = f"SELECT * FROM users WHERE id = {user_id}"  # NEVER!

# ✅ CORRECT - Proper libraries
from pathlib import Path
from urllib.parse import urljoin, urlencode

# Paths
path = Path(base_dir) / filename
api_url = urljoin(base_url, endpoint)

# SQL with parameters
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

#### ❌ Mutable Default Arguments (SHARED STATE BUG!)

```python
# ❌ FORBIDDEN - Mutable defaults
def bad_function(items: List[str] = []) -> List[str]:  # NEVER!
    items.append("new")
    return items

def bad_config(options: Dict[str, Any] = {}) -> Dict:  # NEVER!
    options["key"] = "value"
    return options

# ✅ CORRECT - Immutable defaults with Optional
from typing import Optional, List, Dict

def good_function(items: Optional[List[str]] = None) -> List[str]:
    if items is None:
        items = []
    items.append("new")
    return items

def good_config(options: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    if options is None:
        options = {}
    options["key"] = "value"
    return options
```

#### ❌ Global State Management (TESTING NIGHTMARE!)

```python
# ❌ FORBIDDEN - Global variables for state
DATABASE_CONNECTION = None  # NEVER!
CACHE = {}  # NEVER!
CONFIG = {"key": "value"}  # NEVER!

def init_db():
    global DATABASE_CONNECTION
    DATABASE_CONNECTION = connect()  # NEVER!

# ✅ CORRECT - Dependency injection
from typing import Protocol

class DatabaseProtocol(Protocol):
    async def execute(self, query: str) -> Any: ...

class ServiceClass:
    def __init__(self, db: DatabaseProtocol, cache: CacheProtocol):
        self.db = db
        self.cache = cache
```

### 🚫 **FORBIDDEN CODE STRUCTURES**

#### ❌ Deeply Nested Code (COMPLEXITY BOMB!)

```python
# ❌ FORBIDDEN - Deep nesting
def bad_process_data(data):
    if data:
        if data.get("status") == "active":
            if data.get("type") == "user":
                if data.get("permissions"):
                    if "admin" in data["permissions"]:
                        if data.get("settings"):
                            return process_admin(data)  # NEVER!

# ✅ CORRECT - Early returns and guard clauses
def good_process_data(data: UserData) -> ProcessResult:
    if not data:
        raise ValueError("Data is required")

    if data.status != "active":
        raise ValueError("User must be active")

    if data.type != "user":
        raise ValueError("Invalid user type")

    if not data.permissions or "admin" not in data.permissions:
        raise PermissionError("Admin access required")

    if not data.settings:
        raise ValueError("User settings missing")

    return process_admin(data)
```

#### ❌ Monolithic Functions (DEBUGGING HELL!)

```python
# ❌ FORBIDDEN - Giant functions
def bad_process_user_data(user_data):  # 200+ lines NEVER!
    # validation logic (50 lines)
    # data transformation (50 lines)
    # business logic (50 lines)
    # database operations (50 lines)
    pass

# ✅ CORRECT - Single responsibility functions
def validate_user_data(data: UserInput) -> ValidatedUser:
    """Single purpose: validation only."""
    pass

def transform_user_data(user: ValidatedUser) -> ProcessedUser:
    """Single purpose: data transformation."""
    pass

def save_user_data(user: ProcessedUser) -> SavedUser:
    """Single purpose: persistence."""
    pass

def process_user_data(input_data: UserInput) -> SavedUser:
    """Orchestrates the pipeline."""
    validated = validate_user_data(input_data)
    processed = transform_user_data(validated)
    return save_user_data(processed)
```

---

## ✅ **MANDATORY PATTERNS**

### 📋 **Type Annotations Everywhere**

```python
# ✅ REQUIRED - Complete type annotations
from typing import Optional, List, Dict, Union, Protocol
from pydantic import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    is_active: bool = True

class UserRepository(Protocol):
    async def get_user(self, user_id: int) -> Optional[UserModel]: ...
    async def save_user(self, user: UserModel) -> UserModel: ...

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo: UserRepository = repo
        self.cache: Dict[int, UserModel] = {}

    async def get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        """Get user with proper typing."""
        if user_id in self.cache:
            return self.cache[user_id]

        user = await self.repo.get_user(user_id)
        if user:
            self.cache[user_id] = user
        return user
```

### 📋 **Pydantic v2 Models for All Data**

```python
# ✅ REQUIRED - No raw dicts, Pydantic v2 everywhere
from pydantic import BaseModel, Field, ConfigDict, field_validator, ValidationError
from typing import Optional, List, Annotated
from enum import Enum
from datetime import datetime

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class UserPreferences(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    theme: str = Field(default="light", description="UI theme")
    notifications: bool = Field(default=True, description="Email notifications")
    language: Annotated[str, Field(regex=r"^[a-z]{2}$")] = "en"

class User(BaseModel):
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    id: int = Field(..., gt=0, description="User ID")
    name: Annotated[str, Field(min_length=1, max_length=100)]
    email: Annotated[str, Field(regex=r"^[^@]+@[^@]+\.[^@]+$")]
    role: UserRole = Field(default=UserRole.USER)
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().title()

# ✅ REQUIRED - Typed API responses with v2 methods
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[User] = None
    errors: List[str] = Field(default_factory=list)

async def create_user(user_data: dict) -> ApiResponse:
    """Fully typed API endpoint using Pydantic v2."""
    try:
        # Use model_validate instead of parse_obj
        user = User.model_validate(user_data)
        saved_user = await user_repository.save(user)

        # Use model_dump instead of dict()
        return ApiResponse(
            success=True,
            message="User created",
            data=saved_user
        )
    except ValidationError as e:
        return ApiResponse(
            success=False,
            message="Validation failed",
            errors=[f"{error['loc']}: {error['msg']}" for error in e.errors()]
        )

# ✅ REQUIRED - Advanced v2 patterns
class LimitedString(BaseModel):
    """Example of Annotated constraints."""
    text: Annotated[str, Field(max_length=10, pattern="^[a-zA-Z]+$")]

class NumbersList(BaseModel):
    """Example of strict typing."""
    values: list[int]  # Strict typing in v2

class StatusResponse(BaseModel):
    """Example of serialization control."""
    status: str
    code: int
    details: Optional[dict] = None

    def model_dump_exclude_none(self) -> dict:
        """Exclude None values from serialization."""
        return self.model_dump(exclude_none=True)
```

### 📋 **Pydantic v2 Migration Guide**

| v1 Method | v2 Method | Notes |
|-----------|-----------|-------|
| `.parse_obj(x)` | `.model_validate(x)` | Main validation method |
| `.dict()` | `.model_dump()` | Serialization |
| `.parse_raw(s)` | `.model_validate_json(s)` | JSON validation |
| `.schema()` | `.model_json_schema()` | Schema generation |
| `@validator` | `@field_validator` | Field validation decorator |
| `@root_validator` | `@model_validator` | Model validation decorator |

### 📋 **Pydantic v2 Best Practices**

```python
# ✅ REQUIRED - Use Annotated for constraints
from typing import Annotated
from pydantic import BaseModel, Field

class ApiConfig(BaseModel):
    # Use Annotated for complex constraints
    api_key: Annotated[str, Field(min_length=32, max_length=64)]
    timeout: Annotated[int, Field(gt=0, le=300)] = 30
    retries: Annotated[int, Field(ge=0, le=10)] = 3

# ✅ REQUIRED - Strict typing by default
class StrictModel(BaseModel):
    # v2 is strict by default - no implicit conversions
    age: int  # Will NOT convert "10" to 10 unless configured
    active: bool  # Will NOT convert "true" to True unless configured

# ✅ REQUIRED - Error handling with v2
try:
    user = User.model_validate(invalid_data)
except ValidationError as e:
    # e.errors() returns list of error dicts
    for error in e.errors():
        print(f"Field: {error['loc']}, Error: {error['msg']}, Value: {error['input']}")

# ✅ REQUIRED - Async validation support
async def validate_async_data(data: dict) -> User:
    """Pydantic v2 works great with async frameworks."""
    return User.model_validate(data)
```

### 📋 **Proper Error Handling**

```python
# ✅ REQUIRED - Custom exception hierarchy
class AppError(Exception):
    """Base application error."""
    def __init__(self, message: str, code: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

class ValidationError(AppError):
    """Data validation errors."""
    pass

class BusinessLogicError(AppError):
    """Business rule violations."""
    pass

class ExternalServiceError(AppError):
    """External API/service errors."""
    pass

# ✅ REQUIRED - Specific error handling with context
async def process_user_registration(data: UserRegistrationData) -> User:
    """Process user registration with proper error handling."""
    try:
        # Validation
        validated_data = UserModel.parse_obj(data.dict())
    except ValidationError as e:
        raise ValidationError(
            message="Invalid user data",
            code="USER_VALIDATION_FAILED",
            details={"validation_errors": e.errors()}
        ) from e

    try:
        # Business logic
        if await user_exists(validated_data.email):
            raise BusinessLogicError(
                message="User already exists",
                code="USER_ALREADY_EXISTS",
                details={"email": validated_data.email}
            )

        # External service
        user = await user_service.create(validated_data)
        return user

    except ExternalServiceError as e:
        logger.error(f"User service failed: {e}")
        raise ExternalServiceError(
            message="Failed to create user account",
            code="USER_SERVICE_UNAVAILABLE",
            details={"original_error": str(e)}
        ) from e
```

### 📋 **Async/Await Patterns**

```python
# ✅ REQUIRED - Proper async patterns
import asyncio
from typing import List, Optional
from contextlib import asynccontextmanager

class AsyncUserService:
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool

    @asynccontextmanager
    async def db_transaction(self):
        """Proper async context manager."""
        async with self.db_pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def get_users_batch(self, user_ids: List[int]) -> List[User]:
        """Efficient batch operations."""
        async with self.db_transaction() as conn:
            tasks = [self._get_user_by_id(conn, user_id) for user_id in user_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            users = []
            for result in results:
                if isinstance(result, Exception):
                    logger.warning(f"Failed to fetch user: {result}")
                    continue
                if result:
                    users.append(result)

            return users

    async def _get_user_by_id(self, conn: DatabaseConnection, user_id: int) -> Optional[User]:
        """Internal async method."""
        query = "SELECT * FROM users WHERE id = $1"
        row = await conn.fetchrow(query, user_id)
        return User.parse_obj(dict(row)) if row else None
```

---

## 🔍 **QUALITY GATES**

### **Layer 0: Foundation**

- [ ] ✅ Complete type annotations (mypy --strict passes)
- [ ] ✅ No `Any` type usage
- [ ] ✅ No raw `dict`/`Dict[str, Any]` usage
- [ ] ✅ Custom exception hierarchy
- [ ] ✅ Pydantic models for all data structures
- [ ] ✅ No mutable default arguments

### **Layer 1: Code Structure**

- [ ] ✅ Functions < 20 lines (complex logic split)
- [ ] ✅ Classes < 200 lines (single responsibility)
- [ ] ✅ Modules < 500 lines (proper separation)
- [ ] ✅ Cyclomatic complexity < 10
- [ ] ✅ No global state variables
- [ ] ✅ Dependency injection patterns

### **Layer 2: Error Handling**

- [ ] ✅ No bare `except:` clauses
- [ ] ✅ No generic `except Exception:` without re-raising
- [ ] ✅ Specific exception types for different error cases
- [ ] ✅ Error context preservation with `raise ... from e`
- [ ] ✅ Structured error responses
- [ ] ✅ Proper logging with error context

### **Layer 3: Performance & Security**

- [ ] ✅ No string concatenation for paths/URLs
- [ ] ✅ Parameterized queries for database operations
- [ ] ✅ Async patterns for I/O operations
- [ ] ✅ Resource cleanup with context managers
- [ ] ✅ Input validation at API boundaries
- [ ] ✅ No secrets in code (environment variables)

---

## 📊 **COMPLIANCE METRICS**

### **Code Quality (100% Required)**

- Raw Dict Usage: **0** instances
- `Any` Type Usage: **0** instances
- Bare Except Clauses: **0** instances
- Functions > 20 lines: **< 10%**
- Mutable Default Args: **0** instances
- Global Variables: **0** instances

### **Type Safety (100% Required)**

- Type Annotation Coverage: **100%**
- MyPy Strict Mode: **Pass**
- Pydantic v2 Model Coverage: **100%**
- Pydantic v2 Method Usage: **100%** (model_validate, model_dump)
- Protocol Interface Usage: **90%+**

### **Error Handling (100% Required)**

- Custom Exception Usage: **100%**
- Error Context Preservation: **100%**
- Specific Exception Handling: **95%+**
- Error Response Structure: **100%**

---

## 🚨 **VIOLATION DETECTION**

### **Automated Checks**

```bash
# Type checking
mypy . --strict --show-error-codes

# Code quality
flake8 . --max-complexity=10 --max-line-length=88
black . --check
isort . --check-only

# Security
bandit -r . -f json

# Raw dict detection
grep -r "Dict\[str.*Any\]" src/  # Should return 0 results
grep -r ": dict" src/  # Should return 0 results
grep -r "except:" src/  # Should return 0 results

# Mutable defaults
grep -r "def.*\[\]" src/  # Should return 0 results
grep -r "def.*{}" src/  # Should return 0 results

# Pydantic v2 compliance
grep -r "\.parse_obj(" src/  # Should return 0 results (use model_validate)
grep -r "\.dict()" src/  # Should return 0 results (use model_dump)
grep -r "@validator" src/  # Should return 0 results (use @field_validator)
```

### **Code Review Checklist**

- [ ] All functions have complete type annotations
- [ ] No `Any`, `dict`, or `Dict[str, Any]` usage
- [ ] Pydantic v2 models used for all data structures
- [ ] Using `model_validate()` instead of `parse_obj()`
- [ ] Using `model_dump()` instead of `dict()`
- [ ] Using `@field_validator` instead of `@validator`
- [ ] Custom exceptions with proper hierarchy
- [ ] No bare `except:` or generic `except Exception:`
- [ ] No mutable default arguments
- [ ] Functions under 20 lines with single responsibility
- [ ] Proper async/await usage for I/O operations
- [ ] Context managers for resource management
- [ ] Input validation at API boundaries

---

## 🎯 **SUCCESS CRITERIA**

### **Development Phase**

✅ MyPy strict mode passes
✅ All quality gates pass
✅ Code review approval
✅ No security vulnerabilities
✅ Performance benchmarks met

### **Production Phase**

✅ Zero runtime type errors
✅ Error rates < 1%
✅ Response times within SLA
✅ Memory usage stable
✅ Security audit passed

---

**REMEMBER**: These requirements are **NON-NEGOTIABLE** for production Python code. Every violation must be fixed before merge. Focus on **Type Safety**, **Error Handling**, and **Code Clarity** as the foundation of maintainable Python applications.
