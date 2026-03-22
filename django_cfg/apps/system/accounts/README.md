# Accounts Module

Passwordless authentication system for django-cfg.

- **OTP** — 6-digit email codes, 10-min TTL, single-use
- **OAuth** — GitHub (extensible)
- **2FA** — optional TOTP layer (see `totp` app)
- **JWT** — access + refresh with rotation & blacklist
- **Login alerts** — Apple-style email on new device/IP
- **Soft delete** — GDPR anonymization with partial unique email

## Auth Flows

```
OTP:     POST /cfg/otp/request/  →  POST /cfg/otp/verify/  →  JWT
OAuth:   POST /cfg/oauth/github/authorize/  →  callback/   →  JWT
2FA:     ...verified → { requires_2fa, session_id } → POST /cfg/totp/verify/ → JWT
```

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/cfg/otp/request/` | — | Send OTP to email |
| POST | `/cfg/otp/verify/` | — | Verify OTP → JWT or 2FA session |
| POST | `/cfg/token/refresh/` | — | Refresh access token |
| GET | `/cfg/profile/` | JWT | Get profile |
| PATCH | `/cfg/profile/partial/` | JWT | Update profile |
| POST | `/cfg/profile/avatar/` | JWT | Upload avatar |
| POST | `/cfg/profile/delete/` | JWT | Soft-delete account |
| GET | `/cfg/oauth/providers/` | — | List OAuth providers |
| POST | `/cfg/oauth/github/authorize/` | — | Start GitHub OAuth |
| POST | `/cfg/oauth/github/callback/` | — | Complete GitHub OAuth |
| GET | `/cfg/oauth/connections/` | JWT | List connected providers |
| POST | `/cfg/oauth/disconnect/` | JWT | Remove connection |

## Services

| Service | Purpose |
|---------|---------|
| `OTPService` | OTP generate, send, verify |
| `LoginAlertService` | New-device login emails |
| `OTPRequestThrottle` | Per-email cooldown + hourly/daily limits |
| `OTPVerifyThrottle` | Failed-attempt lockout |
| `GitHubOAuthService` | GitHub OAuth flow |
| `ActivityService` | User activity audit log |
| `AccountNotifications` | Email + Telegram notifications |
| `validate_email_address` | 5-layer email validation |

## Tests

```bash
uv run python manage.py test django_cfg.apps.system.accounts.tests -v 2
```

## Docs

| File | Content |
|------|---------|
| [`@docs/api.md`](@docs/api.md) | API reference with request/response examples |
| [`@docs/security.md`](@docs/security.md) | Threat model, rate limits, Redis keys |
| [`@docs/models.md`](@docs/models.md) | Data models, soft delete, constraints |
| [`@docs/services.md`](@docs/services.md) | OTP, login alerts, email validation |
| [`@docs/notifications.md`](@docs/notifications.md) | Email templates, Telegram, login alerts |
| [`@docs/configuration.md`](@docs/configuration.md) | Settings, JWT, background jobs |
