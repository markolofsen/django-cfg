# TOTP 2FA Module

Two-factor authentication for django-cfg. RFC 6238 compliant, Google Authenticator compatible.

- **TOTP devices** — QR code setup, multiple devices per user, primary device
- **Backup codes** — SHA256-hashed recovery codes, one-time use
- **2FA sessions** — 5-min verification window, attempt limiting
- **Middleware & decorators** — protect paths and views
- **Audit** — signals + Telegram for all 2FA events

## Flows

```
Setup:    POST /cfg/2fa/setup/  →  scan QR  →  POST /cfg/2fa/setup/confirm/  →  backup codes
Login:    OTP verified  →  { requires_2fa, session_id }  →  POST /cfg/2fa/verify/  →  JWT
Recovery: POST /cfg/2fa/verify/backup/  →  JWT (warning if low codes)
```

## API

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/cfg/2fa/setup/` | JWT | Start setup, get QR code + secret |
| POST | `/cfg/2fa/setup/confirm/` | JWT | Confirm with first TOTP code |
| POST | `/cfg/2fa/verify/` | — | Verify TOTP during login |
| POST | `/cfg/2fa/verify/backup/` | — | Verify backup code during login |
| GET | `/cfg/2fa/devices/` | JWT | List devices |
| DELETE | `/cfg/2fa/devices/<id>/` | JWT | Remove device |
| POST | `/cfg/2fa/disable/` | JWT | Disable all 2FA (requires code) |
| GET | `/cfg/2fa/backup-codes/` | JWT | Backup codes status |
| POST | `/cfg/2fa/backup-codes/regenerate/` | JWT | Regenerate codes (requires code) |

## Services

| Service | Purpose |
|---------|---------|
| `TOTPService` | Device CRUD, code verification, QR generation |
| `BackupCodeService` | Generate, verify, invalidate recovery codes |
| `TwoFactorSessionService` | Session lifecycle, verification state |

## Tests

```bash
uv run python manage.py test django_cfg.apps.system.totp.tests -v 2
```

## Docs

| File | Content |
|------|---------|
| [`@docs/api.md`](@docs/api.md) | API reference with request/response examples |
| [`@docs/security.md`](@docs/security.md) | Replay protection, hashing, rate limiting |
| [`@docs/models.md`](@docs/models.md) | TOTPDevice, BackupCode, TwoFactorSession |
| [`@docs/services.md`](@docs/services.md) | Service layer usage and integration |
| [`@docs/integration.md`](@docs/integration.md) | Middleware, decorators, accounts app integration |
