/**
 * AuthLayout Constants
 *
 * Code lengths come from the shared single source of truth in
 * `@djangocfg/api/auth` (AUTH_CONSTANTS). Layout-only values (timings, sizes)
 * live here. Routes deliberately do NOT — they come resolved from
 * `useAuth().routes` so an app's AuthConfig override is honored everywhere.
 */

import { AUTH_CONSTANTS } from '@djangocfg/api/auth';

export const AUTH = {
  // Input lengths (re-exported from @djangocfg/api/auth)
  EMAIL_OTP_LENGTH: AUTH_CONSTANTS.EMAIL_OTP_LENGTH,
  TOTP_LENGTH: AUTH_CONSTANTS.TOTP_LENGTH,
  BACKUP_CODE_MAX_LENGTH: AUTH_CONSTANTS.BACKUP_CODE_MAX_LENGTH,

  // Timing (ms)
  /**
   * Where the brand mark links to — the way OUT of the sign-in screen.
   *
   * Sign-in is otherwise a dead end: a visitor who arrived by a direct link,
   * or who was bounced here by an expired session, has no in-page route back
   * and the browser's Back button has nowhere to return to.
   *
   * Not configurable, and the site ROOT rather than `redirectUrl` (which is
   * where a *successful* sign-in lands — often a private page that would
   * bounce a signed-out visitor straight back here). A localized app resolves
   * this through next-intl's `Link`, so `/ru/auth` returns to `/ru`.
   */
  HOME_URL: '/',
  ANIMATION_DURATION: 400,
  AUTO_SUBMIT_DELAY: 100,
  REDIRECT_DELAY: 1500,
  ANIMATION_START_DELAY: 50,
} as const;
