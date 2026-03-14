# Accounts Module

Complete user authentication and management system built on `django-cfg`.

- OTP (One-Time Password) email authentication
- OAuth2 via GitHub
- 2FA via TOTP (optional)
- Per-email brute-force and abuse protection
- Registration source tracking
- JWT-based sessions (access + refresh tokens)
- Soft-delete with GDPR anonymization and partial unique email constraint

---

## Authentication Flows

### OTP Login

```
POST /cfg/accounts/otp/request/   — send 6-digit code to email
POST /cfg/accounts/otp/verify/    — exchange code for JWT tokens
```

### OAuth (GitHub)

```
POST /cfg/accounts/oauth/github/authorize/   — get authorization URL
POST /cfg/accounts/oauth/github/callback/    — exchange code → JWT tokens
GET  /cfg/accounts/oauth/connections/        — list connected providers
POST /cfg/accounts/oauth/disconnect/         — remove connection
```

### Token management

```
POST /cfg/accounts/token/refresh/   — refresh access token
```

---

## Brute-Force & Abuse Protection

All protection is in `services/brute_force_service.py` using Django's cache framework (Redis in production, locmem in tests).

### OTP Request Throttle (`OTPRequestThrottle`)

Prevents email bombing and SMTP exhaustion.

| Protection | Default | Setting |
|------------|---------|---------|
| Resend cooldown | 60 s | `OTP_RESEND_COOLDOWN_SECONDS` |
| Hourly limit per email | 5 | `OTP_HOURLY_LIMIT` |
| Daily limit per email | 10 | `OTP_DAILY_LIMIT` |

`check_email(email)` → `(allowed: bool, reason: str, retry_after: int)`
`record_sent(email)` — call after successful OTP send.

### OTP Verify Throttle (`OTPVerifyThrottle`)

Prevents brute-forcing 6-digit OTP codes (10^6 space).

| Protection | Default | Setting |
|------------|---------|---------|
| Max failed attempts | 5 | `OTP_MAX_VERIFY_ATTEMPTS` |
| Lockout duration | 900 s (15 min) | `OTP_VERIFY_LOCKOUT_SECONDS` |

`is_locked(email)` → `(locked: bool, retry_after: int)`
`record_failure(email)` → `(just_locked: bool, remaining: int)`
`record_success(email)` — clears both failure counter and lockout.

### Cache Key Privacy

All email addresses are SHA-256 hashed (first 16 hex chars) before use as cache keys — no PII in Redis.

```python
from django_cfg.apps.system.accounts.services.brute_force_service import _hash_identifier
key = f"otp:cooldown:{_hash_identifier(email)}"
```

### View-level Rate Limiting

IP-based rate limits via `django-ratelimit` (returns 429 if exceeded):

| Endpoint | IP limit |
|----------|---------|
| `POST otp/request/` | 10/min |
| `POST otp/verify/` | 20/min |
| `POST oauth/github/authorize/` | 20/min |
| `POST oauth/github/callback/` | 10/min |

### Anti-Enumeration

All `verify_otp` failure paths return identical HTTP 401 + `{"error": "Authentication failed"}` regardless of whether the user exists or the OTP is wrong. Detailed reason is logged server-side only.

---

## Models

| Model | Purpose |
|-------|---------|
| `CustomUser` | Extended `AbstractUser` with email as primary identifier |
| `OTPSecret` | 6-digit OTP with 10-minute TTL |
| `RegistrationSource` | Tracks where users register from |
| `UserRegistrationSource` | Links users to sources (M2M) |
| `OAuthConnection` | Stores OAuth provider connections |

### Soft Delete

`CustomUser` supports soft-delete with GDPR anonymization. Email is **preserved intact** — uniqueness is enforced only among active accounts via a partial unique constraint.

```python
user.soft_delete()   # is_active=False, deleted_at=now(), clears name/phone/company
user.restore()       # is_active=True, deleted_at=None — raises ValueError if email taken
user.is_deleted      # property: deleted_at is not None
```

Multiple deleted accounts may share the same email address (historical archive). Re-registration with a previously deleted email creates a **new** account — the archived one is untouched.

**DB constraint:** `unique_active_email` — `UNIQUE(email) WHERE deleted_at IS NULL` (PostgreSQL partial index).

---

## Services

| Service | File | Purpose |
|---------|------|---------|
| `OTPService` | `services/otp_service.py` | OTP generate, send, verify (includes throttle checks) |
| `OTPRequestThrottle` | `services/brute_force_service.py` | Request flood protection |
| `OTPVerifyThrottle` | `services/brute_force_service.py` | Brute-force lockout |
| `GitHubOAuthService` | `services/github_service.py` | GitHub OAuth flow |
| `AccountNotifications` | `utils/notifications.py` | Email + Telegram notifications |
| `cleanup_expired_otps` | `services/cleanup_service.py` | RQ: delete expired OTP secrets (every 10 min) |
| `cleanup_jwt_blacklist` | `services/cleanup_service.py` | RQ: flush simplejwt blacklist (daily 03:00 UTC) |

---

## Configuration

```python
# Optional Django settings (all have defaults)
OTP_RESEND_COOLDOWN_SECONDS = 60     # seconds between resend requests per email
OTP_HOURLY_LIMIT = 5                 # max OTP sends per email per hour
OTP_DAILY_LIMIT = 10                 # max OTP sends per email per day
OTP_MAX_VERIFY_ATTEMPTS = 5          # failed attempts before lockout
OTP_VERIFY_LOCKOUT_SECONDS = 900     # lockout duration (15 min)
OTP_EXPIRY_MINUTES = 10              # OTP validity window
```

---

## JWT Token Security

Token rotation is enabled by default:

- `ROTATE_REFRESH_TOKENS = True` — each `/token/refresh/` issues a new refresh token
- `BLACKLIST_AFTER_ROTATION = True` — old token is immediately blacklisted
- `rest_framework_simplejwt.token_blacklist` added to `INSTALLED_APPS` automatically

---

## Tests

```bash
# From solution/django
uv run python manage.py test django_cfg.apps.system.accounts.tests
```

| File | Coverage |
|------|---------|
| `tests/test_brute_force.py` | 18 unit tests — `OTPRequestThrottle`, `OTPVerifyThrottle`, `_hash_identifier` (no Redis) |
| `tests/test_views.py` | OTP endpoint tests, throttle integration, anti-enumeration checks |
| `tests/test_oauth_views.py` | GitHub OAuth flow tests |

All brute-force tests use `@override_settings(CACHES=LOCMEM_CACHE)` — no Redis dependency.
Non-throttle test classes use `@override_settings(RATELIMIT_ENABLE=False)`.

---

## IP Spoofing Protection

`AXES_IPWARE_META_PRECEDENCE_ORDER` trusts Cloudflare's `CF-Connecting-IP` header first:

```python
# models/django/axes.py
ipware_meta_precedence_order = [
    'HTTP_CF_CONNECTING_IP',   # Cloudflare (most trusted)
    'HTTP_X_FORWARDED_FOR',
    'HTTP_X_REAL_IP',
    'REMOTE_ADDR',
]
```

---

## Cleanup Jobs (RQ)

Registered automatically when RQ is enabled (`DjangoRQConfig.enabled=True`):

| Job | Schedule | Queue | Purpose |
|-----|----------|-------|---------|
| `cleanup_expired_otps` | `*/10 * * * *` | low | Delete expired/used `OTPSecret` rows |
| `cleanup_jwt_blacklist` | `0 3 * * *` | low | Flush expired `token_blacklist` entries |

Jobs owned by `services/cleanup_service.py::get_rq_schedules()`, loaded by `DjangoRQConfig._collect_module_schedules()`.

---

## See Also

- [`@docs/README.md`](./@docs/README.md) — full API reference and integration guide
- [`@docs/SECURITY.md`](./@docs/SECURITY.md) — brute-force protection internals
