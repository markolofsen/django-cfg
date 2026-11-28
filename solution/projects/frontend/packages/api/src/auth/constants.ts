/**
 * Auth-related constants shared across the frontend.
 * Single source of truth — do not redefine these elsewhere.
 */

export const AUTH_CONSTANTS = {
  /** Email OTP code length (numeric). */
  EMAIL_OTP_LENGTH: 4,
  /** TOTP code length (RFC 6238 — authenticator apps). */
  TOTP_LENGTH: 6,
  /** Backup code max length. */
  BACKUP_CODE_MAX_LENGTH: 12,
  /** Resend cooldown (s) when the server does not state one. Mirrors the backend per-email cooldown. */
  RESEND_COOLDOWN_SECONDS: 30,
} as const;

// Route conventions are NOT exported here on purpose. The '/auth' and '/'
// defaults are applied in exactly one place — AuthProvider's route resolution
// — and every consumer reads the resolved values from `useAuth().routes`.
// Exporting route constants invites components to default to them directly,
// which silently diverges from an app's AuthConfig.routes override.
