'use client';

import { APIError } from '../../runtime/errors';

/**
 * Shared internals for the 2FA hook family (verify / setup / status).
 *
 * Before consolidation each of the three hooks re-implemented error extraction
 * and 6-digit validation slightly differently — three copies that drifted. This
 * module is the single source for both, so every 2FA verb reports errors and
 * validates codes identically.
 *
 * Error extraction itself now lives one level up, in `utils/errors`: this
 * module's own copy was the second of three spellings of the same chain across
 * the auth layer, and the one that could not tell a status code from prose.
 */

const TOTP_CODE_LENGTH = 6;

/** The one field the shared resolver does not read for us. */
interface TwoFactorErrorBody {
  attempts_remaining?: unknown;
}

/** Pull `attempts_remaining` off an APIError body, or null if absent. */
export function extractAttemptsRemaining(err: unknown): number | null {
  if (err instanceof APIError) {
    const body = (err.response ?? null) as TwoFactorErrorBody | null;
    if (typeof body?.attempts_remaining === 'number') return body.attempts_remaining;
  }
  return null;
}

/** True when `code` is a well-formed 6-digit TOTP code. */
export function isValidTotpCode(code: string): boolean {
  return !!code && code.length === TOTP_CODE_LENGTH;
}

export { TOTP_CODE_LENGTH };
