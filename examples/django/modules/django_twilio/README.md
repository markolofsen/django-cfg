# 📱 Django CFG Twilio Module

Auto-configuring Twilio services for django-cfg with comprehensive OTP and messaging support via WhatsApp, Email, and SMS.

## ✨ Features

- **🔐 OTP Services**: WhatsApp, SMS, Voice, and Email OTP delivery
- **🎯 Smart Fallbacks**: Automatic channel fallback when primary fails
- **⚡ Async Support**: Full async/await compatibility with Django 5.2+
- **🛡️ Type Safety**: 100% type-safe with Pydantic v2 models
- **🔧 Auto-Configuration**: Zero-boilerplate setup with DjangoConfig
- **📧 SendGrid Integration**: Professional email OTP with templates
- **🌍 Multi-Region**: Support for Twilio regions (US, Dublin, Singapore, Sydney)
- **🧪 Test-Friendly**: Comprehensive test coverage and mock support

## 🚀 Quick Start

### 1. Installation

```bash
poetry add twilio sendgrid  # Dependencies auto-added to django-cfg
```

### 2. Basic Configuration

```python
from django_cfg import DjangoConfig, TwilioConfig
from django_cfg.modules.django_twilio.models import TwilioVerifyConfig
from pydantic import SecretStr

class MyConfig(DjangoConfig):
    project_name: str = "My App"
    secret_key: str = "your-django-secret-key"
    
    # Your database config here
    databases = {...}
    
    # Twilio configuration
    twilio: TwilioConfig = TwilioConfig(
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        auth_token=SecretStr("your_twilio_auth_token"),
        verify=TwilioVerifyConfig(
            service_sid="VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        )
    )

config = MyConfig()
```

### 3. Send OTP

```python
from django_cfg import send_sms_otp, verify_otp

# Send SMS OTP
success, message = send_sms_otp("+1234567890")
if success:
    print(f"OTP sent: {message}")
    
    # Verify OTP
    user_code = input("Enter code: ")
    is_valid, result = verify_otp("+1234567890", user_code)
    
    if is_valid:
        print("✅ Verified!")
    else:
        print(f"❌ {result}")
```

## 📖 Configuration Guide

### Complete Configuration Example

```python
from django_cfg import DjangoConfig, TwilioConfig
from django_cfg.modules.django_twilio.models import (
    TwilioVerifyConfig,
    SendGridConfig,
    TwilioChannelType,
    TwilioRegion,
)
from pydantic import SecretStr

class ProductionConfig(DjangoConfig):
    project_name: str = "Production App"
    secret_key: str = "your-secret-key"
    databases = {...}  # Your database config
    
    twilio: TwilioConfig = TwilioConfig(
        # Core Twilio settings
        account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        auth_token=SecretStr("your_twilio_auth_token"),
        region=TwilioRegion.US,
        
        # Verify service for WhatsApp/SMS/Voice OTP
        verify=TwilioVerifyConfig(
            service_sid="VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            service_name="My App OTP",
            default_channel=TwilioChannelType.WHATSAPP,
            fallback_channels=[TwilioChannelType.SMS, TwilioChannelType.VOICE],
            code_length=6,
            ttl_seconds=600,  # 10 minutes
            max_attempts=5,
            rate_limit_per_phone=5,
            rate_limit_per_ip=10,
        ),
        
        # SendGrid for email OTP
        sendgrid=SendGridConfig(
            api_key=SecretStr("SG.your_sendgrid_api_key"),
            from_email="noreply@yourapp.com",
            from_name="Your App",
            otp_template_id="d-your_template_id",  # Optional
            default_subject="Your verification code",
            reply_to_email="support@yourapp.com",
            tracking_enabled=True,
            custom_template_data={
                "company_name": "Your Company",
                "support_url": "https://yourapp.com/support",
            },
        ),
        
        # Optional settings
        webhook_url="https://yourapp.com/webhooks/twilio",
        test_mode=False,
        debug_logging=False,
        request_timeout=30,
        max_retries=3,
        retry_delay=1.0,
    )
```

### Environment Variables

```bash
# Twilio settings
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_VERIFY_SERVICE_SID=VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# SendGrid settings  
SENDGRID_API_KEY=SG.your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourapp.com
SENDGRID_FROM_NAME="Your App"
```

## 🎯 Usage Examples

### Service Class Usage

```python
from django_cfg.modules.django_twilio.service import DjangoTwilioService
from django_cfg.modules.django_twilio.models import TwilioChannelType

# Initialize service (auto-discovers configuration)
twilio = DjangoTwilioService()

# Get service status
status = twilio.get_service_status()
print(f"Enabled channels: {status['enabled_channels']}")

# Send OTP with preferred channel
success, message, channel = twilio.send_otp(
    "+1234567890",
    preferred_channel=TwilioChannelType.WHATSAPP,
    enable_fallback=True
)

if success:
    print(f"OTP sent via {channel.value}")
    
    # Verify OTP
    user_code = input("Enter OTP: ")
    is_valid, result = twilio.verify_otp("+1234567890", user_code)
    
    if is_valid:
        print("✅ Phone verified!")
```

### Email OTP

```python
from django_cfg import send_email_otp, verify_otp

# Send email OTP
success, message, otp_code = send_email_otp(
    "user@example.com",
    subject="Your Login Code"
)

if success:
    print(f"Email sent: {message}")
    
    # Verify email OTP
    user_code = input("Enter code from email: ")
    is_valid, result = verify_otp("user@example.com", user_code)
    
    if is_valid:
        print("✅ Email verified!")
```

### WhatsApp with SMS Fallback

```python
from django_cfg import send_whatsapp_otp

# Send WhatsApp OTP with automatic SMS fallback
success, message = send_whatsapp_otp(
    "+1234567890", 
    fallback_to_sms=True
)

if success:
    print(f"OTP sent: {message}")
```

### Async Usage

```python
import asyncio
from django_cfg.modules.django_twilio.service import DjangoTwilioService

async def send_otp_async():
    twilio = DjangoTwilioService()
    
    # Send OTP asynchronously
    success, message, channel = await twilio.asend_otp("+1234567890")
    
    if success:
        print(f"Async OTP sent via {channel.value}")
        
        # Verify asynchronously
        is_valid, result = await twilio.averify_otp("+1234567890", "123456")
        
        if is_valid:
            print("✅ Async verification successful!")

# Run async function
asyncio.run(send_otp_async())
```

## 🔧 Advanced Configuration

### Channel-Specific Configurations

```python
# SMS only
twilio: TwilioConfig = TwilioConfig(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    auth_token=SecretStr("your_token"),
    verify=TwilioVerifyConfig(
        service_sid="VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        default_channel=TwilioChannelType.SMS,
        fallback_channels=[TwilioChannelType.SMS],
    )
)

# Email only
twilio: TwilioConfig = TwilioConfig(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", 
    auth_token=SecretStr("your_token"),
    sendgrid=SendGridConfig(
        api_key=SecretStr("SG.your_key"),
        from_email="noreply@yourapp.com",
    )
)

# Multi-channel with priorities
twilio: TwilioConfig = TwilioConfig(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    auth_token=SecretStr("your_token"),
    verify=TwilioVerifyConfig(
        service_sid="VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        default_channel=TwilioChannelType.WHATSAPP,  # Try WhatsApp first
        fallback_channels=[
            TwilioChannelType.SMS,    # Then SMS
            TwilioChannelType.VOICE   # Finally voice call
        ],
    ),
    sendgrid=SendGridConfig(...),  # Email available separately
)
```

### Regional Configuration

```python
from django_cfg.modules.django_twilio.models import TwilioRegion

# Use Dublin region for EU compliance
twilio: TwilioConfig = TwilioConfig(
    account_sid="ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    auth_token=SecretStr("your_token"),
    region=TwilioRegion.DUBLIN,  # EU region
    verify=TwilioVerifyConfig(
        service_sid="VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    )
)
```

### Custom Email Templates

```python
# Using SendGrid dynamic templates
sendgrid=SendGridConfig(
    api_key=SecretStr("SG.your_key"),
    from_email="noreply@yourapp.com",
    from_name="Your App",
    otp_template_id="d-your_dynamic_template_id",
    custom_template_data={
        "company_name": "Your Company",
        "company_logo": "https://yourapp.com/logo.png",
        "support_email": "support@yourapp.com",
        "app_url": "https://yourapp.com",
    },
)
```

## 🧪 Testing

### Test Configuration

```python
from django_cfg import DjangoConfig, TwilioConfig
from django_cfg.modules.django_twilio.models import TwilioVerifyConfig, SendGridConfig
from pydantic import SecretStr

class TestConfig(DjangoConfig):
    project_name: str = "Test Project"
    secret_key: str = "test-secret-key-that-is-long-enough"
    debug: bool = True
    
    databases = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
    
    twilio: TwilioConfig = TwilioConfig(
        account_sid="ACtest" + "a" * 28,  # Test format
        auth_token=SecretStr("test_token_32_characters_long"),
        verify=TwilioVerifyConfig(
            service_sid="VAtest" + "b" * 28,
        ),
        sendgrid=SendGridConfig(
            api_key=SecretStr("SG.test_key_" + "c" * 50),
            from_email="test@example.com",
        ),
        test_mode=True,  # Important for testing
        debug_logging=True,
    )
```

### Running Tests

```bash
# Run all Twilio tests
pytest tests/twilio/ -v

# Run specific test categories
pytest tests/twilio/test_models.py -v      # Configuration tests
pytest tests/twilio/test_service.py -v     # Service tests  
pytest tests/twilio/test_integration.py -v # Integration tests

# Run with coverage
pytest tests/twilio/ --cov=django_cfg.modules.django_twilio
```

## 🚨 Error Handling

The module provides comprehensive error handling with specific exception types:

```python
from django_cfg.modules.django_twilio.exceptions import (
    TwilioConfigurationError,
    TwilioSendError,
    TwilioVerificationError,
    TwilioRateLimitError,
    TwilioNetworkError,
)

try:
    success, message, channel = twilio.send_otp("+1234567890")
    
except TwilioConfigurationError as e:
    print(f"Configuration error: {e}")
    print("Suggestions:")
    for suggestion in e.suggestions:
        print(f"  - {suggestion}")
        
except TwilioSendError as e:
    print(f"Send error: {e}")
    print(f"Channel: {e.context.get('channel')}")
    print(f"Error code: {e.error_code}")
    
except TwilioVerificationError as e:
    print(f"Verification error: {e}")
    attempts_left = e.context.get('attempts_remaining')
    if attempts_left:
        print(f"Attempts remaining: {attempts_left}")
        
except TwilioRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    retry_after = e.context.get('retry_after_seconds')
    if retry_after:
        print(f"Retry after {retry_after} seconds")
```

## 📋 API Reference

### Configuration Models

- **`TwilioConfig`**: Main configuration class
- **`TwilioVerifyConfig`**: Verify service configuration for SMS/WhatsApp/Voice
- **`SendGridConfig`**: SendGrid email service configuration
- **`TwilioChannelType`**: Enum for channel types (SMS, WHATSAPP, VOICE, EMAIL)
- **`TwilioRegion`**: Enum for Twilio regions (US, DUBLIN, SINGAPORE, SYDNEY)

### Service Classes

- **`DjangoTwilioService`**: Main service class with all features
- **`WhatsAppOTPService`**: WhatsApp OTP with SMS fallback
- **`EmailOTPService`**: Email OTP via SendGrid
- **`SMSOTPService`**: SMS OTP via Twilio Verify
- **`UnifiedOTPService`**: Multi-channel OTP with smart fallbacks

### Convenience Functions

- **`send_whatsapp_otp(phone, fallback_to_sms=True)`**: Send WhatsApp OTP
- **`send_email_otp(email, subject=None)`**: Send email OTP
- **`send_sms_otp(phone)`**: Send SMS OTP
- **`verify_otp(identifier, code)`**: Verify OTP for any channel

### Async Functions

All service methods have async equivalents with `a` prefix:
- **`asend_whatsapp_otp()`**, **`asend_email_otp()`**, **`asend_sms_otp()`**, **`averify_otp()`**

## 🔐 Security Best Practices

1. **Environment Variables**: Store credentials in environment variables
2. **Secret Management**: Use `SecretStr` for sensitive data
3. **Rate Limiting**: Configure appropriate rate limits
4. **Webhook Security**: Use webhook URL validation
5. **Test Mode**: Use test mode for development/testing
6. **Logging**: Enable debug logging only in development

## 🌍 Multi-Region Support

```python
from django_cfg.modules.django_twilio.models import TwilioRegion

# US (default)
region=TwilioRegion.US

# Europe (GDPR compliance)
region=TwilioRegion.DUBLIN

# Asia Pacific
region=TwilioRegion.SINGAPORE

# Australia
region=TwilioRegion.SYDNEY
```

## 📊 Monitoring and Health Checks

```python
# Get comprehensive service status
status = twilio_service.get_service_status()

print(f"Twilio configured: {status['twilio_configured']}")
print(f"Account SID: {status['account_sid']}")
print(f"Region: {status['region']}")
print(f"Enabled channels: {status['enabled_channels']}")

# Check individual services
verify_status = status['services']['verify']
print(f"Verify enabled: {verify_status['enabled']}")
print(f"Service SID: {verify_status['service_sid']}")

sendgrid_status = status['services']['sendgrid'] 
print(f"SendGrid enabled: {sendgrid_status['enabled']}")
print(f"From email: {sendgrid_status['from_email']}")
```

## 🤝 Contributing

1. Follow CRITICAL_REQUIREMENTS.md patterns
2. Use Pydantic v2 models for all data
3. Add comprehensive tests
4. Follow async/await patterns from DJANGO_ASYNC_COMPLETE.md
5. Maintain 100% type safety

## 📝 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ for django-cfg by the Unrealos Team**
