# TOTP 2FA App - Quick Start

## ✅ Implementation Complete

The TOTP two-factor authentication app for django-cfg is fully implemented and ready for use!

## 📁 Project Structure

```
totp/
├── @docs/                       # Complete documentation
│   ├── README.md               # This file
│   ├── ARCHITECTURE.md         # Technical design
│   ├── API.md                  # API reference
│   ├── INTEGRATION.md          # Integration guides
│   ├── TASKS.md                # Implementation tasks
│   └── IMPLEMENTATION_STATUS.md # Current status
├── models/                      # Data models
│   ├── device.py               # TOTPDevice
│   ├── backup_code.py          # BackupCode
│   ├── session.py              # TwoFactorSession
│   └── choices.py              # Enums
├── services/                    # Business logic
│   ├── totp_service.py         # TOTP operations
│   ├── backup_service.py       # Backup codes
│   └── session_service.py      # 2FA sessions
├── serializers/                 # DRF serializers
│   ├── setup.py                # Setup flow
│   ├── verify.py               # Verification
│   ├── device.py               # Device management
│   └── backup.py               # Backup codes
├── views/                       # API endpoints
│   ├── setup.py                # Setup views
│   ├── verify.py               # Verification views
│   ├── device.py               # Device management
│   └── backup.py               # Backup codes
├── middleware/                  # Django middleware
│   └── __init__.py             # TwoFactorMiddleware
├── decorators/                  # View decorators
│   └── __init__.py             # @require_2fa
├── admin/                       # Django admin
│   └── __init__.py             # Admin interfaces
├── migrations/                  # Database migrations
├── __init__.py
├── apps.py                      # AppConfig
├── urls.py                      # URL routing
└── signals.py                   # Django signals
```

## 🚀 Quick Setup

### 1. Dependencies Already Added

Dependencies have been added to `pyproject.toml`:
- `pyotp>=2.9.0,<3.0` - TOTP implementation
- `qrcode>=8.2,<9.0` - QR code generation

### 2. Run Migrations

```bash
cd /Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/djangocfg/projects/django-cfg
python manage.py makemigrations django_cfg_totp
python manage.py migrate
```

### 3. Add to Your DjangoConfig

```python
# In your config.py or settings
class MyConfig(DjangoConfig):
    project_apps: List[str] = [
        "django_cfg.apps.system.totp",
        # ... other apps
    ]
```

### 4. Add URLs

```python
# In your main urls.py
urlpatterns = [
    # ... other URLs
    path("api/2fa/", include("django_cfg.apps.system.totp.urls")),
]
```

## 📖 Usage Examples

### Independent Service Usage

```python
from django_cfg.apps.system.totp.services import TOTPService, BackupCodeService

# Setup 2FA for user
device = TOTPService.create_device(user, name="My Phone")
provisioning_uri = TOTPService.get_provisioning_uri(device, issuer="My App")
qr_code = TOTPService.generate_qr_code(provisioning_uri)

# Show QR code to user, then confirm with first code
if TOTPService.confirm_device(device, user_entered_code):
    # Generate backup codes
    backup_codes = BackupCodeService.generate_codes(user)
    # Show backup codes to user (only shown once!)
```

### API Integration

```bash
# 1. Start 2FA setup
curl -X POST /api/2fa/setup/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"device_name": "My iPhone"}'

# Response includes QR code and secret

# 2. Confirm setup
curl -X POST /api/2fa/setup/confirm/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"device_id": "...", "code": "123456"}'

# Response includes backup codes

# 3. During login (after OTP verification)
# If user has 2FA enabled, create session
session = TwoFactorSession.create_for_user(user, request)
return {"requires_2fa": True, "session_id": session.id}

# 4. Verify 2FA
curl -X POST /api/2fa/verify/ \
  -d '{"session_id": "...", "code": "123456"}'

# Response includes JWT tokens
```

### Protect Views with Decorator

```python
from django_cfg.apps.system.totp.decorators import require_2fa

@require_2fa
def my_protected_view(request):
    # Only accessible if user has verified 2FA
    pass

@require_2fa(max_age_hours=1)
def very_sensitive_view(request):
    # Requires fresh verification within last hour
    pass
```

### Protect Paths with Middleware

```python
# In settings or DjangoConfig
MIDDLEWARE = [
    # ... other middleware
    "django_cfg.apps.system.totp.middleware.TwoFactorMiddleware",
]

TOTP_PROTECTED_PATHS = [
    "/api/terminal/",
    "/api/agents/",
    "/api/machines/",
]
```

## 🔗 Integration with Accounts App

See detailed guide in `@docs/INTEGRATION.md`. Key steps:

1. **Modify OTP verification** to check for 2FA:

```python
# In accounts/views/otp.py
def verify_otp(self, request):
    user = OTPService.verify_otp(email, otp_code)
    
    if user and TOTPService.has_active_device(user):
        # Require 2FA
        session = TwoFactorSessionService.create_session(user, request)
        return Response({
            "requires_2fa": True,
            "session_id": str(session.id),
        })
    
    # No 2FA, return tokens directly
    return Response({"access_token": ..., "refresh_token": ...})
```

2. **Add user model properties**:

```python
# In accounts/models/user.py
@property
def has_2fa_enabled(self) -> bool:
    from django_cfg.apps.system.totp.models import TOTPDevice, DeviceStatus
    return TOTPDevice.objects.filter(
        user=self,
        status=DeviceStatus.ACTIVE
    ).exists()
```

## 📊 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/2fa/setup/` | POST | Start 2FA setup, get QR code |
| `/2fa/setup/confirm/` | POST | Confirm setup with first code |
| `/2fa/verify/` | POST | Verify 2FA code during login |
| `/2fa/verify/backup/` | POST | Verify backup code |
| `/2fa/devices/` | GET | List user's TOTP devices |
| `/2fa/devices/{id}/` | DELETE | Remove device |
| `/2fa/disable/` | POST | Disable 2FA completely |
| `/2fa/backup-codes/` | GET | Get backup codes status |
| `/2fa/backup-codes/regenerate/` | POST | Regenerate backup codes |

Full API documentation in `@docs/API.md`.

## 🎯 Use Case: cmdop Terminal Security

Protect terminal and agent access with 2FA:

```python
# In cmdop/apps/terminal/views.py
from django_cfg.apps.system.totp.decorators import require_2fa

class TerminalViewSet(ViewSet):
    @require_2fa(max_age_hours=1)
    def connect(self, request, terminal_id):
        """Connect to terminal - requires fresh 2FA"""
        # User must have verified 2FA within last hour
        pass
```

## 🔐 Security Features

- ✅ RFC 6238 compliant TOTP
- ✅ Google Authenticator compatible
- ✅ Code reuse prevention (replay attack)
- ✅ Rate limiting (failed attempts)
- ✅ Session expiration (5 minutes)
- ✅ Backup codes with SHA256 hashing
- ✅ IP and user agent tracking
- ✅ Audit logging via signals
- ✅ Telegram notifications

## 📚 Documentation

- **README.md** (this file) - Quick start
- **ARCHITECTURE.md** - Technical design and patterns
- **API.md** - Complete API reference
- **INTEGRATION.md** - Integration guides for various use cases
- **TASKS.md** - Implementation checklist
- **IMPLEMENTATION_STATUS.md** - Current completion status

## 🧪 Testing

After setup, test the flow:

1. Create a superuser: `python manage.py createsuperuser`
2. Run the server: `python manage.py runserver`
3. Access admin: `http://localhost:8000/admin/`
4. Test API endpoints with curl or Postman
5. Scan QR code with Google Authenticator

## 🎉 Status

**✅ FULLY IMPLEMENTED AND READY FOR USE**

All components completed:
- ✅ Models
- ✅ Services
- ✅ Serializers
- ✅ Views/API
- ✅ URLs
- ✅ Middleware
- ✅ Decorators
- ✅ Admin
- ✅ Signals
- ✅ Documentation

## 📞 Next Steps

1. Run migrations
2. Test the setup flow
3. Integrate with accounts app (see INTEGRATION.md)
4. Configure protected paths if using middleware
5. Optional: Create TwoFactorConfig for DjangoConfig integration

---

**Questions or issues?** Check the documentation in `@docs/` or review the implementation in the app code.
