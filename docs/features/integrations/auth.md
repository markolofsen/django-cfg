---
title: Authentication
description: Django-CFG auth feature guide. Production-ready authentication with built-in validation, type safety, and seamless Django integration.
sidebar_label: Authentication
sidebar_position: 4
keywords:
  - django-cfg auth
  - django auth
  - auth django-cfg
---
# 🔐 Authentication Integration

## JWT Configuration


Django CFG provides comprehensive JWT authentication configuration through the `JWTConfig` class, offering type-safe, environment-aware JWT token management.

## Quick Start

```python
from django_cfg import DjangoConfig, JWTConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"
    
    # JWT Configuration
    jwt: JWTConfig = JWTConfig(
        access_token_lifetime_hours=24,
        refresh_token_lifetime_days=30,
    )

config = MyConfig()
```

## Configuration Options

### Token Lifetimes

```python
jwt: JWTConfig = JWTConfig(
    # Token lifetimes
    access_token_lifetime_hours=24,      # 1-8760 hours (1 year max)
    refresh_token_lifetime_days=30,      # 1-365 days (1 year max)
    
    # Token rotation
    rotate_refresh_tokens=True,          # Rotate tokens on refresh
    blacklist_after_rotation=True,       # Blacklist old tokens
)
```

### Security Settings

```python
jwt: JWTConfig = JWTConfig(
    # Security
    algorithm="HS256",                   # JWT signing algorithm
    update_last_login=True,              # Update user's last login
    leeway=0,                           # Token expiration leeway (seconds)
    
    # Optional claims
    audience="my-app",                   # JWT audience claim
    issuer="my-company",                 # JWT issuer claim
)
```

### Token Claims

```python
jwt: JWTConfig = JWTConfig(
    # Claims configuration
    user_id_field="id",                  # User model field for ID
    user_id_claim="user_id",             # JWT claim name for user ID
    token_type_claim="token_type",       # JWT claim name for token type
    jti_claim="jti",                     # JWT claim name for token ID
)
```

### Authentication Headers

```python
jwt: JWTConfig = JWTConfig(
    # Header configuration
    auth_header_types=("Bearer",),       # Accepted header types
    auth_header_name="HTTP_AUTHORIZATION", # HTTP header name
)
```

## Environment-Aware Configuration

JWT configuration automatically adapts to different environments:

### Development Environment
```python
# Automatically configured for development
jwt_dev = jwt_config.configure_for_environment("development", debug=True)
# Result: 1 hour access, 7 days refresh, 30s leeway
```

### Production Environment
```python
# Automatically configured for production
jwt_prod = jwt_config.configure_for_environment("production", debug=False)
# Result: 24 hours access, 30 days refresh, 0s leeway
```

### Testing Environment
```python
# Automatically configured for testing
jwt_test = jwt_config.configure_for_environment("testing")
# Result: 1 hour access, 1 day refresh, no rotation
```

## Advanced Usage

### Custom Environment Configuration

```python
class MyConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig()
    
    def __post_init__(self):
        # Configure JWT based on environment
        if self.debug:
            # Development: short-lived tokens
            self.jwt = self.jwt.configure_for_environment("development", True)
        else:
            # Production: long-lived tokens
            self.jwt = self.jwt.configure_for_environment("production", False)
```

### Token Information

```python
# Get human-readable token info
token_info = config.jwt.get_token_info()
print(token_info)
# Output: {
#     'access_token': '24 hours',
#     'refresh_token': '30 days', 
#     'algorithm': 'HS256',
#     'rotation': 'enabled'
# }
```

### Manual Django Settings

If you need to access the raw Django settings:

```python
# Get Django SIMPLE_JWT settings
jwt_settings = config.jwt.to_django_settings(config.secret_key)
print(jwt_settings['SIMPLE_JWT']['ACCESS_TOKEN_LIFETIME'])
# Output: datetime.timedelta(hours=24)
```

## Supported Algorithms

- **HMAC**: HS256, HS384, HS512
- **RSA**: RS256, RS384, RS512  
- **ECDSA**: ES256, ES384, ES512

## Integration with Django REST Framework

The JWT configuration automatically integrates with `djangorestframework-simplejwt`:

```python
# In your DRF views
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairView(TokenObtainPairView):
    # Automatically uses your JWT configuration
    pass
```

## Best Practices

### 1. Environment-Specific Lifetimes
```python
class MyConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        # Short tokens for development
        access_token_lifetime_hours=1 if debug else 24,
        refresh_token_lifetime_days=7 if debug else 30,
    )
```

### 2. Security in Production
```python
class ProductionConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        algorithm="RS256",              # Use RSA for production
        leeway=0,                       # No leeway in production
        rotate_refresh_tokens=True,     # Always rotate tokens
        blacklist_after_rotation=True, # Blacklist old tokens
    )
```

### 3. Testing Configuration
```python
class TestConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        access_token_lifetime_hours=1,
        refresh_token_lifetime_days=1,
        rotate_refresh_tokens=False,    # Simpler for tests
        blacklist_after_rotation=False,
    )
```

## Troubleshooting

### Token Expiration Issues
```python
# Check current token lifetimes
print(f"Access token: {config.jwt.access_token_lifetime_hours} hours")
print(f"Refresh token: {config.jwt.refresh_token_lifetime_days} days")
```

### Algorithm Validation Errors
```python
# Ensure you're using a supported algorithm
try:
    jwt_config = JWTConfig(algorithm="INVALID")
except ValueError as e:
    print(f"Invalid algorithm: {e}")
```

### Environment Detection
```python
# Verify environment configuration
env_jwt = config.jwt.configure_for_environment("production")
print(f"Production access token: {env_jwt.access_token_lifetime_hours} hours")
```

## Migration from Manual Configuration

### Before (Manual SIMPLE_JWT)
```python
# settings.py
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=24),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': True,
    # ... many more settings
}
```

### After (Django CFG)
```python
# config.py
class MyConfig(DjangoConfig):
    jwt: JWTConfig = JWTConfig(
        access_token_lifetime_hours=24,
        refresh_token_lifetime_days=30,
    )
    # All other settings are automatically configured!
```

## Related Documentation

- [Django REST Framework Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/)
- [JWT.io](https://jwt.io/) - JWT token debugger
- [Django CFG Core Configuration](/fundamentals/configuration)

## Phone OTP Authentication


> **⚠️ This documentation has been moved and updated**
>
> **New Location**: Please see the comprehensive Twilio integration documentation:
> - [`@dotwilio`](twilio) - Complete Twilio setup and configuration
>
> The new documentation includes:
> - ✅ Twilio Verify API integration
> - ✅ WhatsApp and SMS OTP delivery
> - ✅ SendGrid email OTP fallback
> - ✅ Webhook handling and status tracking
> - ✅ Comprehensive testing with `test_twilio` command
> - ✅ Production-ready configuration examples

## Legacy Overview (Deprecated)

This document contains outdated information about phone OTP authentication. The system has been completely rewritten to use Twilio Verify API and modern best practices.

## Architecture

### Core Components

1. **OTPService** - Central service handling OTP generation and verification
2. **SimpleTwilioService** - SMS delivery via Twilio integration  
3. **OTPSecret Model** - Unified OTP storage supporting multiple channels
4. **CustomUser Model** - Extended user model with phone support
5. **AccountNotifications** - Multi-channel notification system

### Channel Support

- **Email Channel**: Traditional email-based OTP delivery
- **Phone Channel**: SMS-based OTP delivery via Twilio
- **Auto-detection**: Automatic channel detection based on identifier format

## User Creation Strategy

### Email Authentication
When a user authenticates via email:
```python
email = "user@example.com"
username = "generated_username"  # Auto-generated
phone = ""  # Empty initially
```

### Phone Authentication  
When a user authenticates via phone:
```python
email = "phone_1234567890@yourdomain.com"  # Temporary email using your domain
username = "generated_username"        # Auto-generated  
phone = "+1234567890"                 # Real phone number
phone_verified = True                 # Set on successful OTP
```

## API Endpoints

### Request OTP

**Endpoint**: `POST /accounts/otp/request/`

**New Format** (Recommended):
```json
{
  "identifier": "+1234567890",  // or "user@example.com"
  "channel": "phone",           // or "email" (optional, auto-detected)
  "source_url": "https://reforms.ai"
}
```


### Verify OTP

**Endpoint**: `POST /accounts/otp/verify/`

**New Format** (Recommended):
```json
{
  "identifier": "+1234567890",  // or "user@example.com"
  "otp": "123456",
  "channel": "phone",           // or "email" (optional, auto-detected)
  "source_url": "https://reforms.ai"
}
```

**Legacy Format** (Backward Compatible):
```json
{
  "email": "user@example.com",  // For email
  "phone": "+1234567890",       // For phone
  "otp": "123456",
  "source_url": "https://reforms.ai"
}
```

## Service Layer

### OTPService Methods

```python
# Email OTP (convenience methods)
success, error = OTPService.request_email_otp(email, source_url)
user = OTPService.verify_email_otp(email, otp_code, source_url)

# Phone OTP (convenience methods)  
success, error = OTPService.request_phone_otp(phone, source_url)
user = OTPService.verify_phone_otp(phone, otp_code, source_url)

# Unified methods (auto-detect channel)
success, error = OTPService.request_otp(identifier, channel, source_url)
user = OTPService.verify_otp(identifier, otp_code, channel, source_url)
```

### Phone Validation

The system validates phone numbers using E.164 format:
- Must start with `+`
- Must have country code (1-9)
- Must have 7-15 total digits
- Supports common formatting: spaces, dashes, parentheses

**Valid Examples**:
- `+1234567890`
- `+1 (555) 123-4567`
- `+44 20 7946 0958`

**Invalid Examples**:
- `1234567890` (missing +)
- `+0234567890` (starts with 0)
- `+12` (too short)

## Database Schema

### OTPSecret Model

```python
class OTPSecret(models.Model):
    # Legacy field (backward compatibility)
    email = models.EmailField(db_index=True, blank=True, null=True)
    
    # New unified fields
    channel_type = models.CharField(max_length=10, choices=[
        ('email', 'Email'),
        ('phone', 'Phone'),
    ])
    recipient = models.CharField(max_length=255, db_index=True)
    
    # OTP data
    secret = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
```

### CustomUser Model

```python
class CustomUser(AbstractUser):
    # Contact fields
    phone = models.CharField(max_length=20, blank=True)
    phone_verified = models.BooleanField(default=False)
    
    # Helper method
    def get_identifier_for_otp(self, channel='email'):
        if channel == 'phone':
            return self.phone if self.phone else None
        return self.email if self.email else None
```

## Notification System

### WhatsApp Notifications (Client)
- Sent directly to user's phone via Twilio WhatsApp
- Contains OTP code, verification link, and security note
- Formatted message with line breaks for better readability

### Email Notifications (Client) - Smart Detection
- **Twilio SendGrid**: Used if configured in `twilio.sendgrid`
- **Django Email**: Fallback if Twilio not configured
- Contains OTP code, verification link, and professional template

### Telegram Notifications (Admin)
- Sent to admin channels for monitoring
- **Security**: Does NOT include OTP codes
- Includes user info, channel type, and timestamp

```python
# Client SMS
AccountNotifications.send_phone_otp_notification(user, otp_code, phone_number)

# Admin Telegram (no OTP code)
DjangoTelegram.send_info("🔑📱 Phone OTP Login Request", {
    "phone": phone_number,
    "user_type": "New User" if is_new_user else "Existing User",
    "timestamp": "2025-09-15 18:41:52 UTC"
})
```

## Configuration

### Twilio Setup

```yaml
# config.dev.yaml
twilio:
  account_sid: "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
  auth_token: "your-auth-token"
  whatsapp_from: "+14155238886"  # WhatsApp sandbox
  sms_from: "+12345678900"       # Your SMS number
```

### Django Settings

```python
# config.py
twilio: Optional[TwilioConfig] = (
    TwilioConfig(
        account_sid=env.twilio.account_sid,
        auth_token=SecretStr(env.twilio.auth_token),
        test_mode=env.debug,
        debug_logging=env.debug,
        request_timeout=30,
        max_retries=3,
        retry_delay=1.0,
    )
    if env.twilio.account_sid and env.twilio.auth_token
    else None
)
```

## Error Handling

### Common Error Types

- `invalid_email` - Invalid email format
- `invalid_phone` - Invalid phone number format  
- `user_creation_failed` - Database error during user creation
- `email_send_failed` - Email delivery failure
- `sms_send_failed` - SMS delivery failure

### Response Formats

**Success Response**:
```json
{
  "message": "OTP sent to your phone number"
}
```

**Error Response**:
```json
{
  "error": "Invalid phone number"
}
```

**Verification Success**:
```json
{
  "refresh": "jwt_refresh_token",
  "access": "jwt_access_token", 
  "user": {
    "id": 1,
    "email": "phone_1234567890@yourdomain.com",
    "phone": "+1234567890",
    "phone_verified": true,
    "full_name": "",
    "date_joined": "2025-09-15T18:41:52Z"
  }
}
```

## Security Considerations

### OTP Security
- 6-digit numeric codes
- 10-minute expiration
- Single-use only
- Rate limiting (reuses active OTP)

### Phone Number Security
- E.164 format validation
- Country code verification
- No international premium numbers
- Twilio fraud detection

### Data Privacy
- Temporary emails for phone users
- Admin notifications exclude OTP codes
- Phone numbers stored securely
- GDPR compliance ready

## Testing

### Service Layer Tests
```python
# Phone OTP tests
def test_request_phone_otp_new_user(self):
    success, error_type = OTPService.request_phone_otp("+1234567890")
    self.assertTrue(success)

def test_verify_phone_otp_success(self):
    user = OTPService.verify_phone_otp("+1234567890", "123456")
    self.assertIsNotNone(user)
    self.assertTrue(user.phone_verified)
```

### API Tests
```python
# Views tests
def test_phone_otp_request_api(self):
    response = self.client.post('/accounts/otp/request/', {
        "identifier": "+1234567890",
        "channel": "phone"
    })
    self.assertEqual(response.status_code, 200)
```

## Migration Strategy

### Backward Compatibility
- Legacy `email` field preserved in OTPSecret
- Old API format still supported
- Gradual migration path available

### Database Migration
```sql
-- Add new fields
ALTER TABLE otpsecret ADD COLUMN channel_type VARCHAR(10) DEFAULT 'email';
ALTER TABLE otpsecret ADD COLUMN recipient VARCHAR(255);

-- Populate recipient field
UPDATE otpsecret SET recipient = email WHERE email IS NOT NULL;

-- Add phone verification
ALTER TABLE customuser ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE;
```

## Monitoring & Analytics

### Logging
- OTP request/verification events
- Channel usage statistics  
- Error tracking and analysis
- Performance metrics

### Admin Interface
- OTP management dashboard
- User phone verification status
- Channel-based filtering
- Bulk operations support

## Future Enhancements

### Planned Features
- WhatsApp OTP delivery
- Voice call OTP delivery  
- Multi-factor authentication
- Backup authentication codes
- International phone validation
- Carrier detection and routing

### API Evolution
- GraphQL support
- Webhook notifications
- Real-time OTP status
- Advanced rate limiting
- Fraud detection integration

---

## Quick Reference

### Key Files
- `models.py` - CustomUser, OTPSecret models
- `services/otp_service.py` - Core OTP logic
- `utils/notifications.py` - Multi-channel notifications
- `serializers/otp.py` - API serializers
- `views/otp.py` - REST API endpoints
- `admin/otp.py` - Admin interface

### Dependencies
- `twilio` - SMS delivery
- `django-rest-framework` - API framework
- `django-rest-framework-simplejwt` - JWT tokens
- `pydantic` - Configuration validation

### Configuration Files
- `config.dev.yaml` - Development settings
- `migrations/` - Database schema changes
- `tests/` - Comprehensive test suite

---

*Last updated: September 15, 2025*
*Version: 1.0.0*
*Author: Django-CFG Team*
