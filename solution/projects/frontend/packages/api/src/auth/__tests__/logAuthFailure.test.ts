import { describe, expect, it, vi } from 'vitest';

import { logAuthFailure } from '../utils/errors';

/**
 * A mistyped OTP must not page anyone.
 *
 * `@djangocfg/devtools` captures `console.error` as an ERROR event, so every
 * error-level auth log became a production alert. A customer fat-fingering
 * their one-time code raised "❌ Error" in Telegram — with consola's `%c` CSS
 * in the message body, because the capture takes the console string verbatim.
 * Real faults are unfindable in that.
 */

const sink = () => ({ warn: vi.fn(), error: vi.fn() });

describe('logAuthFailure', () => {
  describe('the user got it wrong — warn, no alert', () => {
    it.each([400, 401, 403, 404, 429, 499])('treats %i as a warning', (statusCode) => {
      const log = sink();
      logAuthFailure(log, 'Verify OTP failed:', { statusCode });
      expect(log.warn).toHaveBeenCalledOnce();
      expect(log.error).not.toHaveBeenCalled();
    });

    it('reads `status` too, for a rejection that skipped the interceptor', () => {
      const log = sink();
      logAuthFailure(log, 'Verify OTP failed:', { status: 401 });
      expect(log.warn).toHaveBeenCalledOnce();
      expect(log.error).not.toHaveBeenCalled();
    });

    it('passes the message and the error through unchanged', () => {
      const log = sink();
      const error = { statusCode: 401 };
      logAuthFailure(log, 'Verify OTP failed:', error);
      expect(log.warn).toHaveBeenCalledWith('Verify OTP failed:', error);
    });
  });

  describe('something is actually broken — error, raise the alert', () => {
    it.each([500, 502, 503, 504])('treats %i as an error', (statusCode) => {
      const log = sink();
      logAuthFailure(log, 'Verify OTP failed:', { statusCode });
      expect(log.error).toHaveBeenCalledOnce();
      expect(log.warn).not.toHaveBeenCalled();
    });

    it('keeps a network failure at error — it carries no status at all', () => {
      const log = sink();
      logAuthFailure(log, 'Verify OTP failed:', new TypeError('Failed to fetch'));
      expect(log.error).toHaveBeenCalledOnce();
      expect(log.warn).not.toHaveBeenCalled();
    });

    it.each([null, undefined, 'a string', 42, { statusCode: 'nonsense' }])(
      'keeps an unreadable error (%s) at error rather than silencing it',
      (error) => {
        const log = sink();
        logAuthFailure(log, 'Verify OTP failed:', error);
        expect(log.error).toHaveBeenCalledOnce();
        expect(log.warn).not.toHaveBeenCalled();
      },
    );
  });

  describe('the boundaries', () => {
    it('399 is not a client error', () => {
      const log = sink();
      logAuthFailure(log, 'x', { statusCode: 399 });
      expect(log.error).toHaveBeenCalledOnce();
    });

    it('500 is not a client error', () => {
      const log = sink();
      logAuthFailure(log, 'x', { statusCode: 500 });
      expect(log.error).toHaveBeenCalledOnce();
    });

    it('prefers statusCode when both fields disagree', () => {
      /* `statusCode` is the field APIError declares; `status` is the fallback
         for a foreign shape, so it must not override the real one. */
      const log = sink();
      logAuthFailure(log, 'x', { statusCode: 401, status: 500 });
      expect(log.warn).toHaveBeenCalledOnce();
      expect(log.error).not.toHaveBeenCalled();
    });
  });
});
