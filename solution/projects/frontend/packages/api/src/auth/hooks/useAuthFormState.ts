"use client"

import { useCallback, useEffect, useRef, useState } from 'react';

import type { AuthFormState, AuthFormStateHandlers, AuthStep, WebmailLink } from '../types';

const formatCountdown = (s: number): string => {
  if (s <= 0) return '';
  const m = Math.floor(s / 60);
  return m > 0 ? `${m}:${String(s % 60).padStart(2, '0')}` : `${s}s`;
};

const useCountdown = () => {
  const [seconds, setSeconds] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const start = useCallback((from: number) => {
    if (timerRef.current) clearInterval(timerRef.current);
    setSeconds(from);
    timerRef.current = setInterval(() => {
      setSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(timerRef.current!);
          timerRef.current = null;
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, []);

  useEffect(() => () => {
    if (timerRef.current) clearInterval(timerRef.current);
  }, []);

  return { seconds, start };
};

export interface UseAuthFormStateReturn extends AuthFormState, AuthFormStateHandlers {}

/**
 * Hook for auth form state management.
 * Pure state - no side effects, no API calls.
 */
export const useAuthFormState = (
  initialIdentifier = '',
): UseAuthFormStateReturn => {
  const [identifier, setIdentifier] = useState(initialIdentifier);
  const [otp, setOtp] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [acceptedTerms, setAcceptedTerms] = useState(true);
  // null until the marketing-consent feature (if enabled) resolves its
  // jurisdiction-aware default — the layout owns that decision.
  const [marketingConsent, setMarketingConsent] = useState<boolean | null>(null);
  const [step, setStep] = useState<AuthStep>('identifier');
  const [error, setError] = useState('');
  const [webmail, setWebmail] = useState<WebmailLink | null>(null);

  const rateLimit = useCountdown();
  const resend = useCountdown();

  const clearError = useCallback(() => setError(''), []);

  return {
    // State
    identifier,
    otp,
    password,
    isLoading,
    acceptedTerms,
    marketingConsent,
    step,
    error,
    rateLimitSeconds: rateLimit.seconds,
    isRateLimited: rateLimit.seconds > 0,
    rateLimitLabel: formatCountdown(rateLimit.seconds),
    resendSeconds: resend.seconds,
    resendLabel: formatCountdown(resend.seconds),
    webmail,
    // Handlers
    setIdentifier,
    setOtp,
    setPassword,
    setAcceptedTerms,
    setMarketingConsent,
    setError,
    clearError,
    setStep,
    setIsLoading,
    startRateLimitCountdown: rateLimit.start,
    startResendCountdown: resend.start,
    setWebmail,
  };
};
