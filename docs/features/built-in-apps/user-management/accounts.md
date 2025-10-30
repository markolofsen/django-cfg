---
title: Accounts App - OTP Authentication & User Management
description: Django-CFG accounts feature guide. Production-ready accounts app - otp authentication & user management with built-in validation, type safety, and seamless Djan
sidebar_label: Accounts App
sidebar_position: 1
keywords:
  - django-cfg accounts
  - django accounts
  - accounts django-cfg
---

# Accounts App - OTP Authentication & User Management

The **Accounts** app provides a comprehensive user authentication and management system with OTP (One-Time Password) authentication, registration source tracking, and advanced profile management.

## Overview

The Accounts app includes:

- **🔐 OTP Authentication** - Email and SMS-based one-time passwords
- **👥 Custom User Model** - Extended user model with email as primary identifier
- **📊 Registration Tracking** - Track user acquisition sources and analytics
- **🎨 Profile Management** - Avatar support and user preferences
- **🔧 Manager-based Logic** - Performance-optimized computed properties
- **📱 API Integration** - Complete REST API with DRF and Spectacular

## Architecture

### Core Models

```python
# User Management
CustomUser              # Extended AbstractUser with email auth
UserRegistrationSource  # Links users to registration sources
RegistrationSource      # Tracks acquisition channels

# OTP System
OTPSecret              # Stores OTP codes and expiration
TwilioResponse         # Tracks SMS/WhatsApp delivery status
```

### Service Layer

```python
# Business Logic Services
OTPService             # OTP generation, sending, verification
AuthEmailService       # Email notifications for auth events
ActivityService        # User activity tracking
```

### API Layer

```python
# REST API ViewSets
OTPViewSet            # OTP request/verify endpoints
ProfileViewSet        # User profile management
WebhookViewSet        # External service webhooks
```

## OTP Authentication System

### How It Works

1. **User requests OTP** → Email/phone provided to API
2. **OTP generated** → 6-digit code with 10-minute expiration
3. **OTP delivered** → Email or SMS via Twilio
4. **User verifies** → Code submitted to verification endpoint
5. **JWT issued** → User authenticated with refresh/access tokens

### Request OTP

```python
# API Endpoint: POST /api/auth/otp/request/
{
    "identifier": "user@example.com",
    "channel": "email",  # or "phone"
    "source_url": "https://dashboard.unrealon.com"
}

# Response
{
    "success": true,
    "message": "OTP sent successfully",
    "channel": "email",
    "expires_in": 600
}
```

### Verify OTP

```python
# API Endpoint: POST /api/auth/otp/verify/
{
    "identifier": "user@example.com",
    "otp_code": "123456",
    "source_url": "https://dashboard.unrealon.com"
}

# Response
{
    "success": true,
    "message": "Authentication successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "is_new_user": false
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### Service Usage

```python
from django_cfg.apps.accounts.services import OTPService

# Request OTP
success, error_type = OTPService.request_otp(
    email="user@example.com",
    source_url="https://myapp.com"
)

if success:
    print("OTP sent successfully!")
else:
    print(f"Failed to send OTP: {error_type}")

# Verify OTP
user = OTPService.verify_otp(
    email="user@example.com",
    otp_code="123456",
    source_url="https://myapp.com"
)

if user:
    print(f"User authenticated: {user.email}")
else:
    print("Invalid OTP code")
```

## User Management

### Custom User Model

The `CustomUser` model extends Django's `AbstractUser` with:

```python
class CustomUser(AbstractUser):
    # Email as primary identifier
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    
    # Profile fields
    phone_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Metadata
    is_verified = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
```

### Manager Methods

The `UserManager` provides optimized business logic:

```python
# User registration with source tracking
user, created = CustomUser.objects.register_user(
    email="user@example.com",
    source_url="https://dashboard.unrealon.com"
)

# Computed properties (performance optimized)
full_name = CustomUser.objects.get_full_name(user)
initials = CustomUser.objects.get_initials(user)
display_name = CustomUser.objects.get_display_username(user)

# Activity tracking
CustomUser.objects.update_last_activity(user)
```

### Registration Source Tracking

Track where users come from for analytics:

```python
# Automatic source creation
source = RegistrationSource.objects.get_or_create(
    url="https://dashboard.unrealon.com",
    defaults={
        'name': 'Unrealon Dashboard',
        'description': 'Main application dashboard'
    }
)[0]

# Link user to source
UserRegistrationSource.objects.create(
    user=user,
    source=source,
    registration_method='otp_email'
)

# Analytics queries
from django.db.models import Count

# Users by source
sources = RegistrationSource.objects.annotate(
    user_count=Count('userregistrationsource')
).order_by('-user_count')

# Registration methods
methods = UserRegistrationSource.objects.values('registration_method').annotate(
    count=Count('id')
)
```

## API Integration

### ViewSets and Endpoints

```python
# OTP Authentication
POST /api/auth/otp/request/     # Request OTP code
POST /api/auth/otp/verify/      # Verify OTP and authenticate

# Profile Management  
GET    /api/profile/            # Get user profile
PUT    /api/profile/            # Update user profile
POST   /api/profile/avatar/     # Upload avatar
DELETE /api/profile/avatar/     # Remove avatar

# User Sources
GET /api/profile/sources/       # List user's registration sources

# Webhooks (for external services)
POST /api/webhooks/twilio/      # Twilio delivery status
POST /api/webhooks/sendgrid/    # SendGrid delivery status
```

### Serializers

```python
# OTP Operations
OTPRequestSerializer       # Request OTP validation
OTPVerifySerializer       # Verify OTP validation
OTPRequestResponseSerializer   # Success response format
OTPVerifyResponseSerializer    # Verification response format

# Profile Management
UserSerializer            # User profile data
UserProfileUpdateSerializer   # Profile update validation
UserAvatarSerializer      # Avatar upload handling

# Registration Sources
RegistrationSourceSerializer  # Source information
UserRegistrationSourceSerializer  # User-source relationships
```

## Configuration

### Required Settings

```python
# settings.py
AUTH_USER_MODEL = 'django_cfg_accounts.CustomUser'

# OTP Configuration
OTP_EXPIRY_MINUTES = 10
OTP_CODE_LENGTH = 6
OTP_MAX_ATTEMPTS = 3

# Email Configuration (for OTP delivery)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# ... email settings

# Twilio Configuration (for SMS OTP)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_VERIFY_SERVICE_SID = 'your_verify_service_sid'
```

### Django-CFG Integration

```python
# api/config.py
from django_cfg.models import EmailConfig, TwilioConfig

class MyProjectConfig(DjangoConfig):
    # Email for OTP delivery
    email: EmailConfig = EmailConfig(
        backend="sendgrid",
        sendgrid_api_key=env.email.sendgrid_api_key,
        from_email="noreply@myproject.com"
    )
    
    # SMS/WhatsApp for OTP delivery
    twilio: TwilioConfig = TwilioConfig(
        account_sid=env.twilio.account_sid,
        auth_token=env.twilio.auth_token,
        verify_service_sid=env.twilio.verify_service_sid
    )
```

## 🧪 Testing

### Unit Tests

```python
# Test OTP Service
from django_cfg.apps.accounts.services import OTPService
from django_cfg.apps.accounts.models import CustomUser, OTPSecret

class OTPServiceTest(TestCase):
    def test_request_otp_success(self):
        success, error = OTPService.request_otp("test@example.com")
        self.assertTrue(success)
        self.assertEqual(error, "")
        
        # Check OTP was created
        otp = OTPSecret.objects.get(email="test@example.com")
        self.assertIsNotNone(otp.secret)
        
    def test_verify_otp_success(self):
        # Create OTP
        OTPService.request_otp("test@example.com")
        otp = OTPSecret.objects.get(email="test@example.com")
        
        # Verify OTP
        user = OTPService.verify_otp("test@example.com", otp.secret)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")
```

### API Tests

```python
# Test OTP API endpoints
class OTPAPITest(APITestCase):
    def test_request_otp_api(self):
        response = self.client.post('/api/auth/otp/request/', {
            'identifier': 'test@example.com',
            'channel': 'email'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        
    def test_verify_otp_api(self):
        # Request OTP first
        self.client.post('/api/auth/otp/request/', {
            'identifier': 'test@example.com'
        })
        
        # Get OTP code
        otp = OTPSecret.objects.get(email='test@example.com')
        
        # Verify OTP
        response = self.client.post('/api/auth/otp/verify/', {
            'identifier': 'test@example.com',
            'otp_code': otp.secret
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('tokens', response.data)
```

## Usage Examples

### Basic OTP Flow

```python
# 1. User requests OTP
from django_cfg.apps.accounts.services import OTPService

success, error = OTPService.request_otp("user@example.com")
if not success:
    print(f"Failed to send OTP: {error}")
    return

# 2. User receives email/SMS with code
# 3. User submits code for verification
user = OTPService.verify_otp("user@example.com", "123456")
if user:
    print(f"Welcome, {user.email}!")
else:
    print("Invalid OTP code")
```

### Registration with Source Tracking

```python
# Register user from specific source
user, created = CustomUser.objects.register_user(
    email="user@example.com",
    source_url="https://dashboard.unrealon.com"
)

if created:
    print("New user registered!")
    
    # Get registration source info
    source_link = user.userregistrationsource_set.first()
    if source_link:
        print(f"Registered from: {source_link.source.get_display_name()}")
```

### Profile Management

```python
# Update user profile
user = CustomUser.objects.get(email="user@example.com")
user.bio = "Django developer passionate about clean code"
user.timezone = "America/New_York"
user.save()

# Get computed properties
full_name = CustomUser.objects.get_full_name(user)
initials = CustomUser.objects.get_initials(user)
display_name = CustomUser.objects.get_display_username(user)

print(f"User: {display_name} ({initials})")
```

### Analytics Queries

```python
from django.db.models import Count, Q
from django_cfg.apps.accounts.models import RegistrationSource, UserRegistrationSource

# Top registration sources
top_sources = RegistrationSource.objects.annotate(
    user_count=Count('userregistrationsource')
).order_by('-user_count')[:10]

# Registration methods breakdown
methods = UserRegistrationSource.objects.values('registration_method').annotate(
    count=Count('id')
).order_by('-count')

# Recent registrations
recent_users = CustomUser.objects.filter(
    date_joined__gte=timezone.now() - timedelta(days=7)
).select_related('userregistrationsource__source')
```

## 🔒 Security Features

### OTP Security

- **Time-based expiration** - OTP codes expire after 10 minutes
- **Single-use codes** - Each OTP can only be used once
- **Rate limiting** - Prevent OTP spam and brute force attacks
- **Secure generation** - Cryptographically secure random codes

### Authentication Security

- **JWT tokens** - Secure token-based authentication
- **Refresh tokens** - Long-lived tokens for seamless re-authentication
- **Token blacklisting** - Revoke compromised tokens
- **Email verification** - Verify email ownership before activation

### Data Protection

- **Password hashing** - Django's built-in password hashing
- **Sensitive data encryption** - OTP codes stored securely
- **GDPR compliance** - User data deletion and export support
- **Activity logging** - Track authentication events for security

## Integration Patterns

### With Django-CFG Core

```python
# Access from configuration
from api.config import config

# Email OTP delivery
if config.email.backend == "sendgrid":
    # Use SendGrid for email delivery
    pass

# SMS OTP delivery  
if hasattr(config, 'twilio') and config.twilio.account_sid:
    # Use Twilio for SMS delivery
    pass
```

### With Other Apps

```python
# Integration with AI Agents
from django_cfg.apps.agents.models import Agent

# Create user-specific agent
agent = Agent.objects.create(
    name=f"Assistant for {user.email}",
    owner=user,
    configuration={
        'language': user.language,
        'timezone': user.timezone
    }
)

# Integration with Tasks
from django_cfg.apps.tasks.models import Task

# Create welcome task for new users
if created:  # New user registration
    Task.objects.create(
        title="Send welcome email",
        task_type="email",
        user=user,
        data={'template': 'welcome', 'email': user.email}
    )
```

## Monitoring & Analytics

### User Metrics

```python
# Active users
active_users = CustomUser.objects.filter(
    last_activity__gte=timezone.now() - timedelta(days=30)
).count()

# Registration trends
from django.db.models import TruncDate
registrations_by_day = CustomUser.objects.extra(
    select={'day': 'date(date_joined)'}
).values('day').annotate(count=Count('id'))

# OTP success rates
total_otp_requests = OTPSecret.objects.count()
successful_verifications = CustomUser.objects.filter(
    date_joined__gte=timezone.now() - timedelta(days=30)
).count()
```

### Error Tracking

```python
# Failed OTP attempts
from django_cfg.apps.accounts.signals import notify_failed_otp_attempt

# Connect to monitoring
@receiver(notify_failed_otp_attempt)
def track_failed_otp(sender, email, error_type, **kwargs):
    # Log to monitoring service
    logger.warning(f"Failed OTP attempt: {email} - {error_type}")
```

## Best Practices

### 1. Use Manager Methods

```python
# Good: Use manager methods for computed properties
full_name = CustomUser.objects.get_full_name(user)

# Avoid: Direct property access (performance impact)
full_name = f"{user.first_name} {user.last_name}".strip()
```

### 2. Track Registration Sources

```python
# Always include source tracking for analytics
user, created = CustomUser.objects.register_user(
    email=email,
    source_url=request.META.get('HTTP_REFERER')
)
```

### 3. Handle OTP Errors Gracefully

```python
success, error_type = OTPService.request_otp(email)
if not success:
    if error_type == "rate_limited":
        return "Too many requests. Please try again later."
    elif error_type == "invalid_email":
        return "Please provide a valid email address."
    else:
        return "Unable to send OTP. Please try again."
```

### 4. Secure API Endpoints

```python
# Use proper permissions and throttling
class OTPViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]
    throttle_scope = 'otp'
```

## See Also

### User Management Apps

**Related User Apps:**
- [**User Management Overview**](./overview)** - All user management features
- [**Support App**](./support)** - Customer support and ticketing system
- [**Newsletter App**](./newsletter)** - Email marketing and campaigns
- [**Leads App**](./leads)** - Lead capture and management

### Authentication & Security

**Security Configuration:**
- [**Security Settings**](/fundamentals/configuration/security)** - CORS, CSRF, SSL configuration
- [**Environment Variables**](/fundamentals/configuration/environment)** - Secure API key management
- [**Production Config**](/guides/production-config)** - Production auth setup

**Integration:**
- [**Twilio Integration**](/features/integrations/twilio)** - SMS OTP integration
- [**Email Module**](/features/modules/email/overview)** - Email OTP delivery
- [**Telegram Module**](/features/modules/telegram/overview)** - Telegram notifications

### Configuration & Setup

**Getting Started:**
- [**Installation**](/getting-started/installation)** - Install Django-CFG with accounts
- [**Configuration Guide**](/getting-started/configuration)** - Enable accounts app
- [**First Project**](/getting-started/first-project)** - Quick start tutorial

**Configuration:**
- [**Configuration Models**](/fundamentals/configuration)** - Accounts config API
- [**Type-Safe Configuration**](/fundamentals/core/type-safety)** - Pydantic patterns
- [**Built-in Apps Overview**](/features/built-in-apps/overview)** - All production apps

### Tools & Development

**CLI & Management:**
- [**CLI Tools**](/cli/introduction)** - Manage users via CLI
- [**Core Commands**](/cli/commands/core-commands)** - User management commands
- [**Troubleshooting**](/guides/troubleshooting)** - Common auth issues

**Advanced Features:**
- [**AI Agents**](/ai-agents/introduction)** - User-specific AI agents
- [**Background Tasks**](/features/integrations/rearq/overview)** - Async email sending

The Accounts app provides a complete, secure, and scalable user authentication system for your Django-CFG projects! 🚀
