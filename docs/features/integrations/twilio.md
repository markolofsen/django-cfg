---
title: Twilio Integration
description: Django-CFG twilio feature guide. Production-ready twilio integration with built-in validation, type safety, and seamless Django integration.
sidebar_label: Twilio
sidebar_position: 3
keywords:
  - django-cfg twilio
  - django twilio
  - twilio django-cfg
---
# Twilio Integration


## Goal

Complete **multi-channel OTP authentication** system with **Twilio Verify API**, **WhatsApp**, **SMS**, and **SendGrid email** integration. Provides type-safe configuration, webhook handling, and comprehensive admin interface.

---

## 🚨 CRITICAL REQUIREMENTS

### Authentication Flow
- **Multi-channel OTP**: Email and Phone number support
- **Twilio Verify API**: Professional OTP management with built-in rate limiting
- **WhatsApp Primary**: WhatsApp OTP with SMS fallback
- **Email Fallback**: SendGrid → Django email system fallback
- **Webhook Integration**: Real-time delivery status tracking

### Security Requirements
- **Signature Validation**: All webhook requests validated
- **Rate Limiting**: Built into Twilio Verify API
- **Temporary Emails**: Phone users get `phone_{number}@yourdomain.com`
- **OTP Expiry**: Configurable TTL (default: 10 minutes)

---

## Modules

### django_cfg.modules.django_twilio

**Purpose**:
Complete Twilio integration with Verify API, WhatsApp, SMS, and SendGrid email services.

**Dependencies**:
- `twilio` (Twilio Python SDK)
- `pydantic` (Type-safe configuration)
- `django.core.mail` (Email fallback)

**Exports**:
- `send_whatsapp_otp(phone: str) -> Tuple[bool, str]`
- `send_sms_otp(phone: str) -> Tuple[bool, str]`  
- `send_otp_email(email: str) -> Tuple[bool, str, str]`
- `verify_otp(phone: str, code: str) -> Tuple[bool, str]`

**Used in**:
- `django_cfg.apps.accounts.services.otp_service`
- `django_cfg.apps.accounts.views.otp`
- `django_cfg.apps.accounts.views.webhook`

**Tags**: `twilio, otp, whatsapp, sms, email, verify-api, webhooks`


---

### django_cfg.apps.accounts.models

**Purpose**:
Database models for OTP secrets, user management, and Twilio response tracking.

**Key Models**:
- `OTPSecret`: Multi-channel OTP storage (`email`/`phone` channels)
- `TwilioResponse`: Complete Twilio API response and webhook tracking
- `CustomUser`: Extended user model with `phone_verified` field

**Used in**:
- `django_cfg.apps.accounts.admin`
- `django_cfg.apps.accounts.services`
- `django_cfg.apps.accounts.views`

**Tags**: `models, otp, twilio, user-management`

---



### send_otp_email(email: str) -> Tuple[bool, str, str]

**Sends email OTP with SendGrid fallback to Django email.**

```python
success, message, otp_code = send_otp_email("user@example.com")
if success:
    print(f"Email sent with OTP: {otp_code}")
```

### verify_otp(phone: str, code: str) -> Tuple[bool, str]

**Verifies phone OTP using Twilio Verify API.**

```python
success, message = verify_otp("+1234567890", "123456")
if success:
    print("OTP verified successfully")
```

%%END%%
````

---

## Data Models (Pydantic 2 & TypeScript)

### Pydantic 2 Models (Backend)

```python
from pydantic import BaseModel, SecretStr
from enum import Enum

class TwilioChannelType(str, Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"
    VOICE = "voice"
    EMAIL = "email"

class TwilioVerifyConfig(BaseModel):
    service_sid: str
    service_name: str = "Django CFG OTP"
    default_channel: TwilioChannelType = TwilioChannelType.WHATSAPP
    fallback_channels: list[TwilioChannelType] = [TwilioChannelType.SMS]
    code_length: int = 6
    ttl_seconds: int = 600  # 10 minutes
    max_attempts: int = 5

class SendGridConfig(BaseModel):
    api_key: SecretStr
    from_email: str
    from_name: str = "Django CFG"
    default_subject: str = "Your verification code"
    otp_template_id: str = ""

class TwilioConfig(BaseModel):
    account_sid: str
    auth_token: SecretStr
    test_mode: bool = False
    debug_logging: bool = False
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    verify: TwilioVerifyConfig | None = None
    sendgrid: SendGridConfig | None = None
```

### TypeScript Interfaces (Frontend)

```typescript
export type ChannelEnum = 'email' | 'phone';

export interface OtpRequestRequest {
    identifier: string;
    channel: ChannelEnum;
    source_url?: string;
}

export interface OtpRequestResponse {
    message: string;
    channel: ChannelEnum;
    identifier: string;
    expires_in: number;
}

export interface OtpVerifyRequest {
    identifier: string;
    channel: ChannelEnum;
    code: string;
}

export interface OtpVerifyResponse {
    message: string;
    access_token?: string;
    refresh_token?: string;
    user?: UserProfile;
}

export interface TwilioWebhookPayload {
    MessageSid?: string;
    VerificationSid?: string;
    MessageStatus?: string;
    VerificationStatus?: string;
    To?: string;
    From?: string;
    ErrorCode?: string;
    ErrorMessage?: string;
}
```

---

## 🔁 Flows

### Multi-Channel OTP Request Flow

1. **Frontend** sends OTP request with `identifier` and `channel`
2. **OTPService** detects channel type (email/phone) automatically
3. **Phone Channel**: Uses `send_whatsapp_otp()` → Twilio Verify API
4. **Email Channel**: Uses `send_otp_email()` → SendGrid → Django fallback
5. **Response Logging**: All Twilio responses saved to `TwilioResponse` model
6. **Webhook Updates**: Real-time delivery status via Twilio webhooks

**Modules**:
- `django_cfg.apps.accounts.services.otp_service`
- `django_cfg.modules.django_twilio.twilio_service`
- `django_cfg.modules.django_twilio.sendgrid_service`

---

### OTP Verification Flow

1. **Frontend** sends verification with `identifier`, `channel`, and `code`
2. **Phone Channel**: Uses `verify_otp()` → Twilio Verify API
3. **Email Channel**: Database lookup and manual verification
4. **Success**: User authenticated, JWT tokens issued
5. **Phone Users**: `phone_verified` flag set, temporary email created
6. **Webhook Logging**: Verification status logged to `TwilioResponse`

---

### Webhook Processing Flow

1. **Twilio** sends webhook to `/api/accounts/webhook/message-status/`
2. **Signature Validation**: Request signature verified
3. **Response Logging**: Full payload saved to `TwilioResponse` model
4. **Status Updates**: Message/verification status updated
5. **Error Handling**: Failed deliveries logged with error codes
6. **Admin Notifications**: Critical errors sent via Telegram

---

## Configuration

### Environment Configuration (YAML)

```yaml
# === Admin Configuration ===
admin_emails:
  - "admin@yourdomain.com"
  - "support@yourdomain.com"

# === Application URLs ===
app:
  name: "Your App"
  api_url: "https://api.yourdomain.com"
  site_url: "https://yourdomain.com"

# === Twilio Configuration ===
twilio:
  account_sid: "AC..."  # Your Twilio Account SID
  auth_token: "..."     # Your Twilio Auth Token
  whatsapp_from: "+14155238886"  # WhatsApp sandbox number
  sms_from: "+1234567890"        # Your SMS number
  sendgrid_api_key: "SG...."     # SendGrid API key
  verify_service_sid: "VA..."    # Twilio Verify Service SID
```

### Django Configuration

```python
from django_cfg import DjangoConfig
from django_cfg.modules.django_twilio.models import TwilioConfig, TwilioVerifyConfig, SendGridConfig

class YourConfig(DjangoConfig):
    # Enable accounts app
    enable_accounts: bool = True
    
    # Admin emails from environment
    admin_emails: List[str] = env.admin_emails or ["admin@example.com"]
    
    # Twilio configuration
    twilio: TwilioConfig = TwilioConfig(
        account_sid=env.twilio.account_sid,
        auth_token=SecretStr(env.twilio.auth_token),
        verify=TwilioVerifyConfig(
            service_sid=env.twilio.verify_service_sid,
            default_channel=TwilioChannelType.WHATSAPP,
            fallback_channels=[TwilioChannelType.SMS],
        ),
        sendgrid=SendGridConfig(
            api_key=SecretStr(env.twilio.sendgrid_api_key),
            from_email="hello@yourdomain.com",
        ) if env.twilio.sendgrid_api_key else None,
    ) if env.twilio.account_sid else None
```

---

## 🧪 Testing

### Management Command

```bash
# Test all Twilio services
python manage.py test_twilio --mode=all

# Test specific service
python manage.py test_twilio --mode=test-whatsapp --phone="+1234567890"

# Setup mode (configuration check)
python manage.py test_twilio --mode=setup

# Interactive mode
python manage.py test_twilio --interactive
```

### Unit Tests

```python
from django.test import TestCase
from django_cfg.modules.django_twilio import send_whatsapp_otp, verify_otp

class TwilioOTPTestCase(TestCase):
    def test_whatsapp_otp_send(self):
        success, message = send_whatsapp_otp("+1234567890")
        self.assertTrue(success)
        self.assertIn("sent", message.lower())
    
    def test_otp_verification(self):
        # First send OTP
        success, _ = send_whatsapp_otp("+1234567890")
        self.assertTrue(success)
        
        # Then verify with correct code
        success, message = verify_otp("+1234567890", "123456")
        # Note: Will fail in test without real Twilio verification
```

---

## 🚨 Common Issues & Solutions

### Issue: WhatsApp sends SMS instead
**Solution**: Check Twilio Console → Verify → Service → Channels. Enable WhatsApp channel.

### Issue: Email OTP not received
**Solution**: Check SendGrid configuration and Django email fallback settings.

### Issue: Webhook signature validation fails
**Solution**: Ensure `TWILIO_AUTH_TOKEN` matches webhook configuration in Twilio Console.

### Issue: OTP expires too quickly
**Solution**: Adjust `ttl_seconds` in `TwilioVerifyConfig` (default: 600 seconds).

---

## Admin Interface

The Django admin interface provides comprehensive management:

### OTP & Messaging Section
- **OTP Secrets**: View all OTP codes, expiry, and usage status
- **Twilio Responses**: Complete delivery logs with error codes
- **User Activities**: Login attempts, registration, and verification events

### Key Features
- **Real-time Status**: Live webhook updates
- **Error Tracking**: Failed deliveries with Twilio error codes
- **Search & Filter**: By phone, email, status, date ranges
- **Bulk Operations**: Mass OTP cleanup and user management

---

## Related Documentation

- **Phone OTP Authentication**: `@docs/auth/PHONE_OTP_AUTHENTICATION.md`
- **Webhook Configuration**: `@dotwilio#webhook-setup`
- **SendGrid Integration**: `@docs/twilio/SENDGRID_SETUP.md`
- **Testing Guide**: `@docs/twilio/TESTING_GUIDE.md`

TAGS: twilio, otp, whatsapp, sms, email, verify-api, webhooks, authentication

## Webhook Setup


## Goal

Configure **Twilio webhooks** for real-time delivery status tracking of WhatsApp, SMS, and Verify API responses. Includes **signature validation**, **ngrok setup**, and **production deployment**.

---

## 🚨 CRITICAL REQUIREMENTS

### Security Requirements
- **Signature Validation**: All webhook requests MUST be validated
- **HTTPS Only**: Webhooks only work with HTTPS endpoints
- **Request Timeout**: Handle Twilio's 15-second timeout limit
- **Error Handling**: Graceful handling of malformed payloads

### Webhook Types
- **Message Status**: WhatsApp/SMS delivery status updates
- **Verification Status**: Twilio Verify API status updates
- **Delivery Reports**: Failed/successful delivery notifications

---

## Webhook Endpoints

### django_cfg.apps.accounts.views.webhook

**Purpose**:
DRF ViewSet for handling Twilio webhook callbacks with signature validation.

**Endpoints**:
- `POST /api/accounts/webhook/message-status/` - Message delivery status
- `POST /api/accounts/webhook/verification-status/` - Verify API status

**URL Names**:
- `cfg_accounts:webhook-message-status`
- `cfg_accounts:webhook-verification-status`

**Used by**:
- Twilio WhatsApp/SMS services
- Twilio Verify API
- Admin interface (response logging)

**Tags**: `webhooks, twilio, drf, signature-validation`


---

## 🧾 Webhook Configuration


### 2. Get webhook URLs
```bash
# Display webhook URLs with ngrok
python manage.py list_urls --webhook
python manage.py test_twilio --mode=setup
```

### 3. Configure Twilio Console

**For WhatsApp/SMS (Messaging Service):**
1. Go to Twilio Console → Messaging → Services
2. Select your Messaging Service
3. Add webhook URL: `https://YOUR_NGROK_URL/api/accounts/webhook/message-status/`
4. Select events: `delivered`, `failed`, `sent`, `undelivered`

**For Verify API:**
1. Go to Twilio Console → Verify → Services
2. Select your Verify Service
3. Add webhook URL: `https://YOUR_NGROK_URL/api/accounts/webhook/verification-status/`
4. Select events: `approved`, `denied`, `canceled`

## Production Setup

### 1. Configure production webhooks
```python
# In your production settings
TWILIO_WEBHOOK_URLS = {
    'message_status': 'https://api.yourdomain.com/api/accounts/webhook/message-status/',
    'verification_status': 'https://api.yourdomain.com/api/accounts/webhook/verification-status/',
}
```

### 2. Update Twilio Console
- Replace ngrok URLs with production URLs
- Ensure HTTPS is enabled
- Test webhook delivery

%%END%%
````

---

## Webhook Data Models

### TwilioResponse Model

```python
class TwilioResponse(models.Model):
    RESPONSE_TYPES = [
        ('api_send', 'API Send Request'),
        ('api_verify', 'API Verify Request'),
        ('webhook_status', 'Webhook Status Update'),
        ('webhook_delivery', 'Webhook Delivery Report'),
    ]
    
    SERVICE_TYPES = [
        ('whatsapp', 'WhatsApp'),
        ('sms', 'SMS'),
        ('voice', 'Voice'),
        ('email', 'Email'),
        ('verify', 'Verify API'),
    ]
    
    response_type = models.CharField(max_length=20, choices=RESPONSE_TYPES)
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPES)
    message_sid = models.CharField(max_length=34, blank=True)
    verification_sid = models.CharField(max_length=34, blank=True)
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    status = models.CharField(max_length=20, blank=True)
    error_code = models.CharField(max_length=10, blank=True)
    error_message = models.TextField(blank=True)
    to_number = models.CharField(max_length=20, blank=True)
    from_number = models.CharField(max_length=20, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    price_unit = models.CharField(max_length=3, blank=True)
    twilio_created_at = models.DateTimeField(null=True, blank=True)
    otp_secret = models.ForeignKey('OTPSecret', on_delete=models.SET_NULL, null=True, blank=True)
```

### Webhook Payload Examples

**Message Status Webhook:**
```json
{
    "MessageSid": "SM...",
    "MessageStatus": "delivered",
    "To": "+1234567890",
    "From": "whatsapp:+14155238886",
    "ErrorCode": null,
    "ErrorMessage": null,
    "Price": "0.0055",
    "PriceUnit": "USD"
}
```

**Verification Status Webhook:**
```json
{
    "VerificationSid": "VE...",
    "VerificationStatus": "approved",
    "To": "+1234567890",
    "Channel": "whatsapp",
    "Valid": "true"
}
```

---

## 🔁 Webhook Processing Flow

### Message Status Webhook Flow

1. **Twilio** sends POST to `/api/accounts/webhook/message-status/`
2. **Signature Validation**: `TwilioWebhookViewSet` validates request signature
3. **Payload Parsing**: Extract `MessageSid`, `MessageStatus`, error codes
4. **Database Logging**: Create/update `TwilioResponse` record
5. **OTP Linking**: Link to related `OTPSecret` if found
6. **Error Notifications**: Send Telegram alerts for failures
7. **Response**: Return HTTP 200 to acknowledge receipt

### Verification Status Webhook Flow

1. **Twilio Verify** sends POST to `/api/accounts/webhook/verification-status/`
2. **Signature Validation**: Verify webhook authenticity
3. **Status Processing**: Handle `approved`, `denied`, `canceled` statuses
4. **User Updates**: Update `phone_verified` flag on approval
5. **Activity Logging**: Record verification attempt in `UserActivity`
6. **Database Logging**: Save full webhook payload
7. **Response**: Return HTTP 200 to Twilio

---

## Configuration

### Django Settings

```python
# settings.py
TWILIO_WEBHOOK_VALIDATION = True  # Enable signature validation
TWILIO_WEBHOOK_TIMEOUT = 10       # Request timeout in seconds
```

### Environment Variables

```yaml
# config.dev.yaml
twilio:
  account_sid: "AC..."
  auth_token: "..."  # Used for signature validation
  webhook_validation: true

# Ngrok configuration
ngrok:
  enabled: true
  auth:
    authtoken: "YOUR_NGROK_TOKEN"
  tunnel:
    schemes: ["https"]  # HTTPS required for webhooks
```

---

## 🧪 Testing Webhooks

### Using test_twilio Command

```bash
# Show webhook URLs and configuration
python manage.py test_twilio --mode=setup

# Test webhook endpoints manually
curl -X POST https://your-ngrok-url/api/accounts/webhook/message-status/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "MessageSid=SM123&MessageStatus=delivered&To=%2B1234567890"
```

### Using Twilio Console

1. Go to Twilio Console → Webhooks → Debugger
2. Find your webhook requests
3. Check response codes and timing
4. Review payload and errors

### Local Testing

```python
# Test webhook view directly
from django.test import Client
from django_cfg.apps.accounts.views.webhook import TwilioWebhookViewSet

client = Client()
response = client.post('/api/accounts/webhook/message-status/', {
    'MessageSid': 'SM123',
    'MessageStatus': 'delivered',
    'To': '+1234567890',
    'From': 'whatsapp:+14155238886'
})
assert response.status_code == 200
```

---

## 🚨 Common Issues & Solutions

### Issue: Webhook signature validation fails
**Solution**: 
- Verify `TWILIO_AUTH_TOKEN` matches Twilio Console
- Check webhook URL matches exactly (trailing slash matters)
- Ensure HTTPS is used

### Issue: Webhooks not received
**Solution**:
- Check ngrok tunnel is running
- Verify webhook URL in Twilio Console
- Check firewall/proxy settings

### Issue: Webhook timeouts
**Solution**:
- Optimize database queries in webhook handler
- Use async processing for heavy operations
- Return HTTP 200 quickly, process in background

### Issue: Duplicate webhook processing
**Solution**:
- Use `MessageSid`/`VerificationSid` for idempotency
- Check existing records before creating new ones
- Handle race conditions with database constraints

---

## Monitoring & Debugging

### Admin Interface
- **Twilio Responses**: View all webhook payloads
- **Filter by Status**: Find failed deliveries
- **Search by SID**: Track specific messages
- **Error Analysis**: Group by error codes

### Logging
```python
import logging
logger = logging.getLogger('django_cfg.twilio.webhooks')

# Webhook received
logger.info(f"Webhook received - MessageSid: {message_sid}, Status: {status}")

# Signature validation failed  
logger.error(f"Invalid webhook signature from {request.META.get('REMOTE_ADDR')}")

# Processing error
logger.error(f"Error processing webhook: {e}", exc_info=True)
```

### Metrics
- **Delivery Rates**: Track successful vs failed deliveries
- **Response Times**: Monitor webhook processing speed
- **Error Patterns**: Identify common failure causes
- **Volume Tracking**: Monitor OTP usage patterns

---

## Related Documentation

- **Twilio Integration**: `@dotwilio`
- **Testing Guide**: `@docs/twilio/TESTING_GUIDE.md`
- **Production Deployment**: `@docs/deployment/TWILIO_PRODUCTION.md`

TAGS: webhooks, twilio, signature-validation, ngrok, production, monitoring
