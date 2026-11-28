"use client"

import { useCallback, useEffect, useRef } from 'react';

import { AUTH_CONSTANTS } from '../constants';
import { useAuth } from '../context';
import { authLogger } from '../utils/logger';
import { useAuthFormState } from './useAuthFormState';
import { useAuthValidation } from './useAuthValidation';
import { useAutoAuth } from './useAutoAuth';
import { beginTwoFactorChallenge } from './useTwoFactorChallenge';

import type { AuthFormReturn, UseAuthFormOptions } from '../types';
/**
 * Complete auth form hook.
 * Composes smaller hooks for state, validation, and submission.
 */
export const useAuthForm = (options: UseAuthFormOptions): AuthFormReturn => {
  const {
    onIdentifierSuccess,
    onOTPSuccess,
    onError,
    sourceUrl,
    redirectUrl,
    requireTermsAcceptance = false,
    marketingConsent: marketingConsentOption,
    authPath = '/auth',
  } = options;

  // Compose smaller hooks
  const formState = useAuthFormState();
  const validation = useAuthValidation();

  // Ref to track auto-submit from URL
  const isAutoSubmitFromUrlRef = useRef(false);
  // Remembers the exact `identifier:otp` we already attempted from a magic-link
  // URL. We verify a given code at most ONCE — even if it turns out invalid or
  // expired — so re-renders never re-fire the request. Without this, the auto
  // submit loops and hammers /verify/ until the backend returns 429.
  const processedOtpKeyRef = useRef<string | null>(null);

  // Auth context for API calls and storage
  const {
    requestOTP,
    verifyOTP,
    login,
    getSavedEmail,
    saveEmail,
  } = useAuth();

  // Destructure for convenience
  const {
    identifier,
    otp,
    password,
    acceptedTerms,
    marketingConsent,
    setIdentifier,
    setOtp,
    setStep,
    setError,
    setIsLoading,
    clearError,
    startRateLimitCountdown,
    startResendCountdown,
    setWebmail,
  } = formState;

  const { validateIdentifier } = validation;

  // ─────────────────────────────────────────────────────────────────────────
  // Storage Helper
  // ─────────────────────────────────────────────────────────────────────────

  const saveIdentifierToStorage = useCallback((id: string) => {
    saveEmail(id);
  }, [saveEmail]);

  // ─────────────────────────────────────────────────────────────────────────
  // Effects
  // ─────────────────────────────────────────────────────────────────────────

  // Load saved identifier on mount
  useEffect(() => {
    const savedEmail = getSavedEmail();
    if (savedEmail) {
      setIdentifier(savedEmail);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ─────────────────────────────────────────────────────────────────────────
  // Submit Handlers
  // ─────────────────────────────────────────────────────────────────────────

  const handleIdentifierSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!identifier) {
      const msg = 'Please enter your email address';
      setError(msg);
      onError?.(msg);
      return;
    }

    if (!validateIdentifier(identifier)) {
      const msg = 'Please enter a valid email address';
      setError(msg);
      onError?.(msg);
      return;
    }

    if (requireTermsAcceptance && !acceptedTerms) {
      const msg = 'Please accept the Terms of Service and Privacy Policy';
      setError(msg);
      onError?.(msg);
      return;
    }

    clearError();
    setOtp('');
    setWebmail(null);
    // Optimistic: the code screen opens now; a failed request rolls back to the identifier step.
    setStep('otp');

    const rollBack = (msg: string) => {
      setStep('identifier');
      setError(msg);
      onError?.(msg);
    };

    try {
      // Only apps that opted in send consent fields — absent option ⇒ body unchanged.
      const consent = marketingConsentOption
        ? { marketingConsent: marketingConsent === true, disclosureVersion: marketingConsentOption.disclosureVersion }
        : undefined;
      const result = await requestOTP(identifier, sourceUrl, consent);

      if (result.success) {
        saveIdentifierToStorage(identifier);
        setWebmail(result.webmail ?? null);
        startResendCountdown(result.resendIn ?? AUTH_CONSTANTS.RESEND_COOLDOWN_SECONDS);
        onIdentifierSuccess?.(identifier);
      } else if (result.retryAfter) {
        setStep('identifier');
        startRateLimitCountdown(result.retryAfter);
      } else {
        rollBack(result.message);
      }
    } catch {
      rollBack('An unexpected error occurred');
    }
  }, [
    identifier, acceptedTerms, requireTermsAcceptance,
    marketingConsent, marketingConsentOption,
    validateIdentifier, requestOTP, saveIdentifierToStorage,
    setError, setOtp, setStep, clearError, setWebmail,
    startRateLimitCountdown, startResendCountdown, onIdentifierSuccess, onError, sourceUrl,
  ]);

  // Core OTP submit - accepts explicit values to avoid stale closures
  const submitOTP = useCallback(async (
    submitIdentifier: string,
    submitOtp: string,
  ): Promise<boolean> => {
    if (!submitOtp || submitOtp.length < AUTH_CONSTANTS.EMAIL_OTP_LENGTH) {
      const msg = `Please enter the ${AUTH_CONSTANTS.EMAIL_OTP_LENGTH}-digit verification code`;
      setError(msg);
      onError?.(msg);
      return false;
    }

    setIsLoading(true);
    clearError();

    try {
      // Skip redirect - we'll show success screen first
      const result = await verifyOTP(submitIdentifier, submitOtp, sourceUrl, redirectUrl, true);

      if (result.requires_2fa && result.session_id) {
        authLogger.info('2FA required after OTP verification');
        beginTwoFactorChallenge({ sessionId: result.session_id });
        saveIdentifierToStorage(submitIdentifier);
        return true; // OTP was successful, now need 2FA
      }

      if (result.success) {
        saveIdentifierToStorage(submitIdentifier);

        authLogger.info('OTP verification successful, showing success screen');
        setStep('success');
        onOTPSuccess?.();
        return true;
      } else {
        setError(result.message);
        onError?.(result.message);
        return false;
      }
    } catch {
      const msg = 'An unexpected error occurred';
      setError(msg);
      onError?.(msg);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [verifyOTP, saveIdentifierToStorage, setError, setIsLoading, clearError, onOTPSuccess, onError, sourceUrl, redirectUrl, setStep]);

  const handleOTPSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    await submitOTP(identifier, otp);
  }, [identifier, otp, submitOTP]);

  // ─────────────────────────────────────────────────────────────────────────
  // Password Submit
  // ─────────────────────────────────────────────────────────────────────────

  // The password credential lands on the same outcomes as the OTP code:
  // a 2FA challenge or 'success'.
  const submitPassword = useCallback(async (
    submitIdentifier: string,
    submitPassword_: string,
  ): Promise<boolean> => {
    if (!submitIdentifier || !validateIdentifier(submitIdentifier)) {
      const msg = 'Please enter a valid email address';
      setError(msg);
      onError?.(msg);
      return false;
    }

    if (!submitPassword_) {
      const msg = 'Please enter your password';
      setError(msg);
      onError?.(msg);
      return false;
    }

    setIsLoading(true);
    clearError();

    try {
      // Skip redirect - we'll show success screen first
      const result = await login(submitIdentifier, submitPassword_, {
        redirectUrl,
        skipRedirect: true,
      });

      if (result.requires_2fa && result.session_id) {
        authLogger.info('2FA required after password login');
        beginTwoFactorChallenge({ sessionId: result.session_id });
        saveIdentifierToStorage(submitIdentifier);
        return true; // Password was accepted, now need 2FA
      }

      if (result.success) {
        saveIdentifierToStorage(submitIdentifier);
        authLogger.info('Password login successful, showing success screen');
        setStep('success');
        onOTPSuccess?.();
        return true;
      }

      // A lockout (429) carries a retry-after; show the countdown instead of a
      // message the user can only re-trigger.
      if (result.retryAfter) {
        startRateLimitCountdown(result.retryAfter);
        clearError();
      } else {
        setError(result.message);
        onError?.(result.message);
      }
      return false;
    } catch {
      const msg = 'An unexpected error occurred';
      setError(msg);
      onError?.(msg);
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [
    login, validateIdentifier, saveIdentifierToStorage, setError, setIsLoading,
    clearError, startRateLimitCountdown, onOTPSuccess, onError, redirectUrl,
    setStep,
  ]);

  const handlePasswordSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    await submitPassword(identifier, password);
  }, [identifier, password, submitPassword]);

  const handleResendOTP = useCallback(async () => {
    setIsLoading(true);
    clearError();

    try {
      // Resend repeats the same OTP request — carry the same consent state so
      // the backend never sees a consent-less duplicate of an opted-in request.
      const consent = marketingConsentOption
        ? { marketingConsent: marketingConsent === true, disclosureVersion: marketingConsentOption.disclosureVersion }
        : undefined;
      const result = await requestOTP(identifier, sourceUrl, consent);

      if (result.success) {
        saveIdentifierToStorage(identifier);
        setWebmail(result.webmail ?? null);
        startResendCountdown(result.resendIn ?? AUTH_CONSTANTS.RESEND_COOLDOWN_SECONDS);
        setOtp('');
      } else {
        if (result.retryAfter) {
          startRateLimitCountdown(result.retryAfter);
          clearError(); // countdown in rateLimitLabel is enough feedback
        } else {
          setError(result.message);
          onError?.(result.message);
        }
      }
    } catch {
      const msg = 'Failed to resend verification code';
      setError(msg);
      onError?.(msg);
    } finally {
      setIsLoading(false);
    }
  }, [identifier, marketingConsent, marketingConsentOption, requestOTP, saveIdentifierToStorage, setOtp, setError, setIsLoading, clearError, startRateLimitCountdown, startResendCountdown, setWebmail, onError, sourceUrl]);

  const handleBackToIdentifier = useCallback(() => {
    setStep('identifier');
    clearError();
  }, [setStep, clearError]);

  const forceOTPStep = useCallback(() => {
    setStep('otp');
    clearError();
  }, [setStep, clearError]);

  // ─────────────────────────────────────────────────────────────────────────
  // Auto-auth from URL
  // ─────────────────────────────────────────────────────────────────────────

  const handleOTPFromUrl = useCallback((detectedOtp: string, detectedEmail?: string) => {
    // Prefer the email from the magic-link URL (works on a fresh browser/device),
    // fall back to the one saved from a previous request on this browser.
    const autoIdentifier = detectedEmail || getSavedEmail() || '';

    if (!autoIdentifier) {
      authLogger.warn('No identifier found for auto-submit (no email in URL or storage)');
      return;
    }

    // Verify each magic-link code at most once. A re-render must never re-fire
    // the request — a failed/expired code that retried in a loop is exactly what
    // drove the /verify/ spam and the backend's 429 lockout.
    const otpKey = `${autoIdentifier}:${detectedOtp}`;
    if (processedOtpKeyRef.current === otpKey) return;
    if (isAutoSubmitFromUrlRef.current) return;

    processedOtpKeyRef.current = otpKey;
    isAutoSubmitFromUrlRef.current = true;

    authLogger.info('OTP detected from URL, auto-submitting');

    // Update UI state
    setIdentifier(autoIdentifier);
    setOtp(detectedOtp);
    setStep('otp');

    // Submit with explicit values
    setTimeout(async () => {
      try {
        await submitOTP(autoIdentifier, detectedOtp);
      } finally {
        isAutoSubmitFromUrlRef.current = false;
      }
    }, 100);
  }, [getSavedEmail, setIdentifier, setOtp, setStep, submitOTP]);

  useAutoAuth({
    allowedPaths: [authPath],
    onOTPDetected: handleOTPFromUrl,
    cleanupUrl: true,
  });

  // ─────────────────────────────────────────────────────────────────────────
  // Return
  // ─────────────────────────────────────────────────────────────────────────

  return {
    // State
    ...formState,

    // Submit handlers
    handleIdentifierSubmit,
    handleOTPSubmit,
    handlePasswordSubmit,
    handleResendOTP,
    handleBackToIdentifier,
    forceOTPStep,

    // Validation
    ...validation,

    // Auto-submit ref
    isAutoSubmittingFromUrl: isAutoSubmitFromUrlRef,
  };
};

// Re-export types for convenience
export type { AuthFormReturn, UseAuthFormOptions } from '../types';
