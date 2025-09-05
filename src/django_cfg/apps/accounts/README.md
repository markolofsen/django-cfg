# 🧩 Accounts Module Documentation

## 🎯 Goal

Comprehensive Django accounts module with OTP authentication, user management, and registration source tracking. Optimized for LLM understanding and code generation.

---

## 📖 Overview

The accounts module provides a complete user authentication and management system with:
- Custom User model with email-based authentication
- OTP (One-Time Password) authentication system
- Registration source tracking for analytics
- Profile management with avatar support
- Manager-based computed properties for performance

---

## 📦 Modules

### @accounts/models

**Purpose**: Core data models for user management and authentication.

**Models**:
- `CustomUser`: Extended AbstractUser with email as primary identifier
- `OTPSecret`: One-time password secrets for authentication
- `RegistrationSource`: Tracks where users register from
- `UserRegistrationSource`: Links users to their registration sources

**Dependencies**:
- `django.contrib.auth.models.AbstractUser`
- `django.db.models`
- `django.utils.timezone`

**Used in**:
- All views and serializers
- Admin interface
- Services layer

---

### @accounts/managers

**Purpose**: Custom model managers with business logic and computed properties.

**Managers**:
- `UserManager`: Handles user creation, registration, and computed properties
- `OTPSecretManager`: Manages OTP secret lifecycle

**Key Methods**:
- `register_user()`: Creates new users with source tracking
- `get_full_name()`: Computes user's full name
- `get_initials()`: Computes user's initials for avatar
- `get_display_username()`: Formats username for display

**Used in**:
- Models for computed properties
- Admin interface
- Services layer

---

### @accounts/services

**Purpose**: Business logic layer for authentication and user operations.

**Services**:
- `OTPService`: Handles OTP generation, sending, and verification
- `AuthEmailService`: Email notifications for authentication events

**Key Methods**:
- `request_otp()`: Generates and sends OTP
- `verify_otp()`: Verifies OTP and authenticates user
- `send_otp_email()`: Sends OTP via email

**Used in**:
- Views for authentication
- API endpoints
- Management commands

---

### @accounts/serializers

**Purpose**: DRF serializers for API data validation and transformation.

**Serializers**:
- `OTPRequestSerializer`: Validates OTP request data
- `OTPVerifySerializer`: Validates OTP verification data
- `UserProfileUpdateSerializer`: Handles profile updates
- `RegistrationSourceSerializer`: Manages registration sources

**Used in**:
- API views
- Admin interface
- External integrations

---

### @accounts/views

**Purpose**: API endpoints for authentication and user management.

**Views**:
- `OTPRequestView`: Handles OTP requests
- `OTPVerifyView`: Handles OTP verification
- `ProfileUpdateView`: Manages profile updates
- `UserSourcesView`: Lists user registration sources

**Used in**:
- URL routing
- API documentation
- Frontend integration

---

## 🧾 APIs (ReadMe.LLM Format)

````markdown
%%README.LLM id=accounts%%

## 🧭 Module Description

Django accounts module with OTP authentication and user management. Provides complete user lifecycle management.

## ✅ Rules

- Always use CustomUser instead of Django's default User model
- Use manager methods for computed properties (full_name, initials, display_username)
- OTP secrets expire after 10 minutes
- Registration sources are automatically tracked
- All email operations are async

## 🧪 Functions

### CustomUser.objects.register_user(email: str, source_url: Optional[str] = None) -> Tuple[CustomUser, bool]

**Creates or retrieves user with source tracking.**

```python
user, created = CustomUser.objects.register_user(
    "user@example.com", 
    source_url="https://dashboard.unrealon.com"
)
```

### CustomUser.objects.get_full_name(user: CustomUser) -> str

**Computes user's full name with fallbacks.**

```python
full_name = user.objects.get_full_name(user)  # "John Doe" or "john@example.com"
```

### OTPService.request_otp(email: str, source_url: Optional[str] = None) -> bool

**Generates and sends OTP to user.**

```python
success = OTPService.request_otp("user@example.com")
```

### OTPService.verify_otp(email: str, otp_code: str, source_url: Optional[str] = None) -> Optional[CustomUser]

**Verifies OTP and returns authenticated user.**

```python
user = OTPService.verify_otp("user@example.com", "123456")
```

%%END%%
````

---

## 🔁 Flows

### User Registration via OTP

1. User submits email → `OTPRequestView` receives request
2. `OTPService.request_otp()` generates OTP secret
3. Email sent via `AuthEmailService.send_otp_email()`
4. User receives email with OTP code
5. User submits OTP → `OTPVerifyView` processes verification
6. `OTPService.verify_otp()` validates and creates user
7. User is authenticated and redirected

**Modules**:
- `@accounts/views.otp`
- `@accounts/services.otp_service`
- `@accounts/utils.auth_email_service`
- `@accounts/managers.user_manager`

---

### Profile Update Flow

1. User submits profile data → `ProfileUpdateView` receives request
2. `UserProfileUpdateSerializer` validates data
3. User model updated with new information
4. Avatar processed if provided
5. Response includes updated user data

**Modules**:
- `@accounts/views.profile`
- `@accounts/serializers.profile`
- `@accounts/models.CustomUser`

---

### Registration Source Tracking

1. User registers from any source URL
2. `UserManager.register_user()` creates/retrieves source
3. `UserRegistrationSource` links user to source
4. Analytics can track user acquisition channels
5. Admin interface shows user registration sources

**Modules**:
- `@accounts/models.RegistrationSource`
- `@accounts/models.UserRegistrationSource`
- `@accounts/managers.user_manager`

---

### Admin User Management

1. Admin accesses Django admin interface
2. `CustomUserAdmin` displays computed properties
3. Manager methods provide formatted data
4. Avatar fallback shows user initials
5. Registration sources displayed in user detail

**Modules**:
- `@accounts/admin`
- `@accounts/managers.user_manager`
- `@accounts/models.CustomUser`

---

## 🧠 Terms

- **OTP (One-Time Password)**: Temporary authentication code sent via email
- **Registration Source**: URL or platform where user registered from
- **Computed Properties**: User data calculated by manager methods (full_name, initials, display_username)
- **Avatar Fallback**: User initials displayed when no avatar image is available
- **Source Tracking**: Automatic recording of where users register from for analytics
- **Manager Methods**: Business logic moved from model properties to manager for better performance

---

## 🔧 Configuration

### Required Settings

```python
# settings.py
AUTH_USER_MODEL = 'accounts.CustomUser'
OTP_EXPIRY_MINUTES = 10
TELEGRAM_DISABLED = True  # For testing
```

### Dependencies

```toml
# pyproject.toml
[tool.poetry.dependencies]
django = "^5.2"
djangorestframework = "^3.14"
drf-spectacular = "^0.27"
coolname = "^2.1"
```

### URL Configuration

```python
# urls.py
urlpatterns = [
    path('auth/otp/request/', OTPRequestView.as_view()),
    path('auth/otp/verify/', OTPVerifyView.as_view()),
    path('profile/update/', ProfileUpdateView.as_view()),
]
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all accounts tests
python manage.py test src.accounts.tests

# Run specific test file
python manage.py test src.accounts.tests.test_models

# Run with pytest
poetry run pytest src/accounts/tests/ -v
```

### Test Coverage

- **Models**: User creation, computed properties, source tracking
- **Services**: OTP generation, verification, email sending
- **Serializers**: Data validation, transformation
- **Views**: API endpoints, authentication flows

---

## 🚀 Migration

### Database Migrations

```bash
# Create migration
python manage.py makemigrations accounts

# Apply migration
python manage.py migrate

# Using pnpm
pnpm migrate
```

### Model Changes

- `Source` → `RegistrationSource` (renamed for clarity)
- `UserSource` → `UserRegistrationSource` (renamed for clarity)
- Computed properties moved to manager methods
- Added app_label to all model Meta classes
