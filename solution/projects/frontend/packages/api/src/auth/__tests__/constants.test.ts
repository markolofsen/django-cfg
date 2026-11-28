/**
 * Auth constants invariants (auth/constants.ts).
 *
 * These lengths gate OTP/TOTP/backup-code validation across the form. A silent
 * change here (e.g. bumping EMAIL_OTP_LENGTH) would desync the frontend from the
 * backend's code length and break login, so pin them explicitly. useAutoAuth
 * also compares the URL OTP against EMAIL_OTP_LENGTH before auto-submitting.
 */

import { describe, expect, it } from 'vitest';

import { AUTH_CONSTANTS } from '../constants';

describe('AUTH_CONSTANTS', () => {
  it('email OTP length is 4 (matches backend numeric OTP)', () => {
    expect(AUTH_CONSTANTS.EMAIL_OTP_LENGTH).toBe(4);
  });
  it('TOTP length is 6 (RFC 6238)', () => {
    expect(AUTH_CONSTANTS.TOTP_LENGTH).toBe(6);
  });
  it('backup code max length is 12', () => {
    expect(AUTH_CONSTANTS.BACKUP_CODE_MAX_LENGTH).toBe(12);
  });
  it('all lengths are positive integers', () => {
    for (const v of Object.values(AUTH_CONSTANTS)) {
      expect(Number.isInteger(v)).toBe(true);
      expect(v).toBeGreaterThan(0);
    }
  });
});
