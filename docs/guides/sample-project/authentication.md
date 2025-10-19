---
title: Authentication System
description: OTP-based authentication and user management in Django-CFG sample project
sidebar_label: Authentication
sidebar_position: 7
---

# Authentication System

The Django-CFG sample project demonstrates a secure OTP (One-Time Password) authentication system with user registration tracking. This guide covers the complete authentication flow and user management.

## Authentication Overview

The sample project uses:
- **OTP Authentication** - Passwordless login via email/SMS
- **JWT Tokens** - Secure API authentication
- **User Registration Tracking** - Analytics for acquisition sources
- **Custom User Model** - Email-based authentication

## OTP Authentication System

### Authentication Flow

1. User requests OTP (via email or SMS)
2. System generates and sends OTP code
3. User verifies OTP code
4. System issues JWT tokens for API access

### Requesting OTP

Send OTP to user's email or phone:

```python
from django_cfg.apps.accounts.services import OTPService

# Request OTP via email
success, error = OTPService.request_otp(
    email="user@example.com",
    source_url="https://myapp.com"
)

if success:
    print("OTP sent to email")
else:
    print(f"Failed to send OTP: {error}")
```

### Verifying OTP

Validate the OTP code and authenticate user:

```python
from django_cfg.apps.accounts.services import OTPService

# Verify OTP
user = OTPService.verify_otp(
    email="user@example.com",
    otp_code="123456",
    source_url="https://myapp.com"
)

if user:
    print(f"User authenticated: {user.email}")
    # Generate JWT tokens
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
else:
    print("Invalid OTP code")
```

### OTP Configuration

Configure OTP settings:

```python
# OTP expiration time (seconds)
OTP_EXPIRATION = 300  # 5 minutes

# OTP length
OTP_LENGTH = 6  # 6-digit code

# Max verification attempts
OTP_MAX_ATTEMPTS = 3
```

## API Authentication

### Authentication Endpoints

```
POST   /api/auth/otp/request/        # Request OTP
POST   /api/auth/otp/verify/         # Verify OTP and get tokens
POST   /api/auth/token/refresh/      # Refresh access token
POST   /api/auth/logout/             # Logout user
```

See [API Documentation](./api-documentation) for complete endpoint details.

### Request OTP (API)

```bash
curl -X POST http://localhost:8000/api/auth/otp/request/ \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "channel": "email"
  }'
```

Response:
```json
{
  "success": true,
  "message": "OTP sent to email"
}
```

### Verify OTP (API)

```bash
curl -X POST http://localhost:8000/api/auth/otp/verify/ \
  -H "Content-Type: application/json" \
  -d '{
    "identifier": "user@example.com",
    "otp_code": "123456"
  }'
```

Response:
```json
{
  "success": true,
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  },
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Using JWT Tokens

Include access token in API requests:

```bash
curl -X GET http://localhost:8000/api/profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Refreshing Tokens

Access tokens expire after a set time. Refresh them:

```bash
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

## User Registration Tracking

### Registration Source Tracking

Track where users come from for analytics:

```python
from django_cfg.apps.accounts.models import RegistrationSource, UserRegistrationSource

# Automatic source creation during OTP verification
user, created = CustomUser.objects.register_user(
    email="user@example.com",
    source_url="https://dashboard.myapp.com"
)

if created:
    # New user registered
    source_link = user.userregistrationsource_set.first()
    print(f"New user from: {source_link.source.get_display_name()}")
```

### Source URL Patterns

The system automatically categorizes sources:

```python
# Dashboard registration
source_url = "https://dashboard.myapp.com"
# Category: "Dashboard"

# Marketing campaign
source_url = "https://myapp.com?utm_source=facebook&utm_campaign=spring"
# Category: "Facebook - Spring Campaign"

# Direct registration
source_url = "https://myapp.com/register"
# Category: "Website Registration"
```

### Analytics Queries

Query user acquisition data:

```python
from django.db.models import Count

# Top acquisition sources
top_sources = RegistrationSource.objects.annotate(
    user_count=Count('userregistrationsource')
).order_by('-user_count')[:10]

for source in top_sources:
    print(f"{source.get_display_name()}: {source.user_count} users")

# Users by source this month
from django.utils import timezone
from datetime import timedelta

month_ago = timezone.now() - timedelta(days=30)

recent_sources = UserRegistrationSource.objects.filter(
    created_at__gte=month_ago
).values('source__url').annotate(
    count=Count('id')
).order_by('-count')

for source in recent_sources:
    print(f"{source['source__url']}: {source['count']} users")
```

## Custom User Model

### User Model

The sample project uses a custom user model:

```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name
```

### User Manager

Custom manager for user creation:

```python
from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

    def register_user(self, email, source_url=None):
        """Register user with source tracking."""
        user, created = self.get_or_create(email=email)

        if created and source_url:
            # Track registration source
            source, _ = RegistrationSource.objects.get_or_create(
                url=source_url
            )
            UserRegistrationSource.objects.create(
                user=user,
                source=source
            )

        return user, created
```

## Email Integration

### Sending OTP via Email

The system uses SendGrid (production) or console (development):

```python
from django_cfg import DjangoEmailService

email_service = DjangoEmailService()

# Send OTP email
def send_otp_email(user_email, otp_code):
    email_service.send_template(
        template_name="emails/otp.html",
        context={
            "otp_code": otp_code,
            "expiry_minutes": 5
        },
        recipient_list=[user_email],
        subject="Your verification code"
    )
```

### Email Template

```html
<!-- templates/emails/otp.html -->
<!DOCTYPE html>
<html>
<head>
    <style>
        .otp-code {
            font-size: 32px;
            font-weight: bold;
            letter-spacing: 5px;
            color: #4F46E5;
        }
    </style>
</head>
<body>
    <h2>Your Verification Code</h2>
    <p>Enter this code to complete your login:</p>
    <div class="otp-code">{{ otp_code }}</div>
    <p>This code expires in {{ expiry_minutes }} minutes.</p>
    <p>If you didn't request this code, please ignore this email.</p>
</body>
</html>
```

See [Service Integrations](./service-integrations) for email configuration.

## SMS Integration

### Sending OTP via SMS

Use Twilio for SMS delivery:

```python
from django_cfg.modules.django_twilio.service import UnifiedOTPService

twilio_service = UnifiedOTPService()

# Send OTP via SMS
def send_otp_sms(phone_number, otp_code):
    message = twilio_service.send_sms(
        to=phone_number,
        body=f"Your verification code is: {otp_code}"
    )
    return message.sid
```

See [Service Integrations](./service-integrations) for Twilio setup.

## Security Best Practices

### 1. Rate Limiting

Prevent brute force attacks:

```python
from django.core.cache import cache

def check_rate_limit(identifier):
    """Check if user exceeded OTP request rate."""
    cache_key = f"otp_rate_limit:{identifier}"
    attempts = cache.get(cache_key, 0)

    if attempts >= 3:  # Max 3 requests per hour
        return False

    cache.set(cache_key, attempts + 1, 3600)  # 1 hour
    return True
```

### 2. OTP Expiration

OTP codes expire after 5 minutes:

```python
from django.utils import timezone
from datetime import timedelta

# Check if OTP is expired
def is_otp_valid(otp_created_at):
    expiry_time = timedelta(minutes=5)
    return timezone.now() - otp_created_at < expiry_time
```

### 3. Single Use OTP

OTP codes can only be used once:

```python
def verify_and_consume_otp(email, otp_code):
    """Verify OTP and mark as used."""
    otp = OTPSecret.objects.filter(
        email=email,
        secret=otp_code,
        used=False
    ).first()

    if otp and is_otp_valid(otp.created_at):
        otp.used = True
        otp.save()
        return True

    return False
```

### 4. Secure Token Storage

Store tokens securely in client applications:

```python
# ✅ Good: Secure storage
# - HTTP-only cookies (web)
# - Secure keychain (mobile)
# - Encrypted storage

# ❌ Bad: Insecure storage
# - localStorage (XSS vulnerable)
# - Plain text files
# - URL parameters
```

## User Profile Management

### Profile Model

Extend user with profile information:

```python
# apps/profiles/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}'s profile"
```

### Auto-create Profile

Automatically create profile for new users:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
```

## Testing Authentication

### Test OTP Flow

```python
from django.test import TestCase
from django_cfg.apps.accounts.services import OTPService

class AuthenticationTest(TestCase):
    def test_otp_request(self):
        """Test OTP request."""
        success, error = OTPService.request_otp(
            email="test@example.com",
            source_url="https://test.com"
        )
        self.assertTrue(success)

    def test_otp_verification(self):
        """Test OTP verification."""
        # Request OTP
        OTPService.request_otp(
            email="test@example.com",
            source_url="https://test.com"
        )

        # Get OTP from database
        from django_cfg.apps.accounts.models import OTPSecret
        otp = OTPSecret.objects.get(email="test@example.com")

        # Verify OTP
        user = OTPService.verify_otp(
            email="test@example.com",
            otp_code=otp.secret,
            source_url="https://test.com"
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.email, "test@example.com")
```

## Best Practices

### 1. Use OTP for Passwordless Auth

```python
# ✅ Good: Passwordless OTP
user = OTPService.verify_otp(email, otp_code, source_url)

# ❌ Bad: Password-based auth (less secure)
user = authenticate(username=email, password=password)
```

### 2. Track User Sources

```python
# ✅ Good: Track registration source
user, created = User.objects.register_user(
    email=email,
    source_url=request.META.get('HTTP_REFERER')
)

# ❌ Bad: No source tracking
user = User.objects.create(email=email)
```

### 3. Implement Rate Limiting

```python
# ✅ Good: Rate limit OTP requests
if not check_rate_limit(email):
    return {"error": "Too many requests"}

# ❌ Bad: No rate limiting
```

### 4. Set Token Expiration

```python
# ✅ Good: Short-lived access tokens
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

# ❌ Bad: Long-lived tokens
ACCESS_TOKEN_LIFETIME = timedelta(days=365)
```

## Related Topics

- [API Documentation](./api-documentation) - Authentication endpoints
- [Service Integrations](./service-integrations) - Email and SMS setup
- [Configuration](./configuration) - Authentication configuration

Secure, passwordless authentication improves user experience and security!
