'use client';

import { useCallback, useState } from 'react';

import { auth } from '../../runtime/auth';
import { cfgTotpVerifyBackupCreate, cfgTotpVerifyCreate } from '../../_api/endpoints';
import type { TotpVerifyUser, VerifyResponse } from '../../_api/models';
import { Analytics, AnalyticsCategory, AnalyticsEvent } from '../utils/analytics';
import { authLogger } from '../utils/logger';
import { formatAuthError, logAuthFailure } from '../utils/errors';
import { consumeSavedRedirect } from './useAuthRedirect';
import { useCfgRouter } from './useCfgRouter';
import { extractAttemptsRemaining, isValidTotpCode } from './twoFactor.shared';
import { authTrace } from '../trace';

export interface UseTwoFactorVerifyOptions {
  /** Callback on successful 2FA verification */
  onSuccess?: (user: TotpVerifyUser) => void;
  /** Callback on error */
  onError?: (error: string) => void;
  /** URL to redirect after successful verification */
  redirectUrl?: string;
  /** Skip automatic redirect after success (caller handles navigation) */
  skipRedirect?: boolean;
}

export interface UseTwoFactorVerifyReturn {
  /** Loading state */
  isLoading: boolean;
  /** Error message */
  error: string | null;
  /** Warning message (e.g., low backup codes) */
  warning: string | null;
  /** Remaining backup codes (if backup code was used) */
  remainingBackupCodes: number | null;
  /** Remaining verification attempts before lockout */
  attemptsRemaining: number | null;
  /** Verify TOTP code */
  verifyTOTP: (sessionId: string, code: string) => Promise<boolean>;
  /** Verify backup code */
  verifyBackupCode: (sessionId: string, backupCode: string) => Promise<boolean>;
  /** Clear error */
  clearError: () => void;
}

/**
 * 2FA verification during login (internal — composed by {@link useTwoFactor}).
 *
 * After OTP/OAuth verification returns requires_2fa=true and a session_id,
 * collect the TOTP (or backup) code and call verifyTOTP/verifyBackupCode to
 * complete authentication.
 */
export const useTwoFactorVerify = (
  options: UseTwoFactorVerifyOptions = {},
): UseTwoFactorVerifyReturn => {
  const { onSuccess, onError, redirectUrl, skipRedirect = false } = options;
  const router = useCfgRouter();

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [remainingBackupCodes, setRemainingBackupCodes] = useState<number | null>(null);
  const [attemptsRemaining, setAttemptsRemaining] = useState<number | null>(null);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // `VerifyResponse` is the generated shape of this endpoint, so the hand-written
  // copy it replaces cannot drift from the server contract any more.
  const handleSuccess = useCallback((response: VerifyResponse) => {
    // Save tokens — the ONE write path (atomic pair + session notification).
    // Storage is always localStorage; session length is the server's call.
    // See AccountsContext.verifyOTP.
    authTrace('2fa.session');
    auth.setSession({ access: response.access_token, refresh: response.refresh_token });

    if (response.warning) {
      setWarning(response.warning);
    }
    if (response.remaining_backup_codes !== undefined) {
      setRemainingBackupCodes(response.remaining_backup_codes);
    }

    Analytics.event(AnalyticsEvent.AUTH_LOGIN_SUCCESS, {
      category: AnalyticsCategory.AUTH,
      label: '2fa',
    });
    if (response.user?.id) {
      Analytics.setUser(String(response.user.id));
    }

    onSuccess?.(response.user);

    // Redirect (unless skipRedirect). Priority: saved back-url > option > default.
    if (!skipRedirect) {
      const finalRedirectUrl = consumeSavedRedirect() || redirectUrl || '/private';
      authLogger.info('2FA successful, redirecting to:', finalRedirectUrl);
      router.hardPush(finalRedirectUrl);
    }
  }, [onSuccess, redirectUrl, router, skipRedirect]);

  const verifyTOTP = useCallback(async (sessionId: string, code: string): Promise<boolean> => {
    if (!sessionId) {
      const msg = 'Missing 2FA session ID';
      setError(msg);
      onError?.(msg);
      return false;
    }
    if (!isValidTotpCode(code)) {
      const msg = 'Please enter a 6-digit code';
      setError(msg);
      onError?.(msg);
      return false;
    }

    setIsLoading(true);
    setError(null);

    try {
      authLogger.info('Verifying TOTP code...');

      const response = await cfgTotpVerifyCreate({ session_id: sessionId, code });

      if (!response.access_token || !response.refresh_token) {
        throw new Error('Invalid response from 2FA verification');
      }

      handleSuccess(response);
      return true;
    } catch (err) {
      logAuthFailure(authLogger, '2FA TOTP verification failed:', err);
      const errorMessage = formatAuthError(err, 'Invalid verification code');
      const attempts = extractAttemptsRemaining(err);
      if (attempts !== null) setAttemptsRemaining(attempts);
      setError(errorMessage);
      onError?.(errorMessage);

      Analytics.event(AnalyticsEvent.AUTH_OTP_VERIFY_FAIL, {
        category: AnalyticsCategory.AUTH,
        label: '2fa-totp',
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [handleSuccess, onError]);

  const verifyBackupCode = useCallback(async (sessionId: string, backupCode: string): Promise<boolean> => {
    if (!sessionId) {
      const msg = 'Missing 2FA session ID';
      setError(msg);
      onError?.(msg);
      return false;
    }
    if (!backupCode || backupCode.length < 8) {
      const msg = 'Please enter your backup code';
      setError(msg);
      onError?.(msg);
      return false;
    }

    setIsLoading(true);
    setError(null);

    try {
      authLogger.info('Verifying backup code...');

      const response = await cfgTotpVerifyBackupCreate({
        session_id: sessionId,
        backup_code: backupCode.replace(/\s+/g, ''),
      });

      if (!response.access_token || !response.refresh_token) {
        throw new Error('Invalid response from backup code verification');
      }

      handleSuccess(response);
      return true;
    } catch (err) {
      logAuthFailure(authLogger, '2FA backup code verification failed:', err);
      const errorMessage = formatAuthError(err, 'Invalid backup code');
      const attempts = extractAttemptsRemaining(err);
      if (attempts !== null) setAttemptsRemaining(attempts);
      setError(errorMessage);
      onError?.(errorMessage);

      Analytics.event(AnalyticsEvent.AUTH_OTP_VERIFY_FAIL, {
        category: AnalyticsCategory.AUTH,
        label: '2fa-backup',
      });
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [handleSuccess, onError]);

  return {
    isLoading,
    error,
    warning,
    remainingBackupCodes,
    attemptsRemaining,
    verifyTOTP,
    verifyBackupCode,
    clearError,
  };
};
