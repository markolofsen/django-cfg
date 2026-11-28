'use client';

import { usePathname } from 'next/navigation';
import { useEffect, useRef } from 'react';

import { AUTH_CONSTANTS } from '../constants';
import { authLogger } from '../utils/logger';
import { isAllowedAuthPath } from '../utils/path';
import { useCfgRouter } from './useCfgRouter';
import { useQueryParams } from './useQueryParams';

export interface UseAutoAuthOptions {
  /** Called with the OTP from the URL, plus the optional `email` query param if present. */
  onOTPDetected?: (otp: string, email?: string) => void;
  cleanupUrl?: boolean;
  /** Paths where auto-auth should be active. Default: ['/auth'] */
  allowedPaths?: string[];
}

/**
 * Hook for automatic authentication from URL query parameters
 * Detects OTP from URL and triggers callback.
 * (Path normalization / allow-list matching live in ../utils/path so they can
 * be unit-tested independently of the hook.)
 */
export const useAutoAuth = (options: UseAutoAuthOptions = {}) => {
  const { onOTPDetected, cleanupUrl = true, allowedPaths = ['/auth'] } = options;
  const queryParams = useQueryParams();
  const pathname = usePathname();
  const router = useCfgRouter();

  // Check if current path is in allowed paths, ignoring the locale prefix
  // (next-intl may keep it in the URL, e.g. /ru/auth) and trailing slashes.
  const isAllowedPath = isAllowedAuthPath(pathname, allowedPaths);

  const queryOtp = queryParams.get('otp') || '';
  const queryEmail = queryParams.get('email') || undefined;
  const hasOTP = !!queryOtp;
  const isReady = !!pathname && hasOTP && isAllowedPath;
  const otpValid = queryOtp.length === AUTH_CONSTANTS.EMAIL_OTP_LENGTH;

  // Keep the latest callback in a ref so its (unstable) identity never lands in
  // the effect deps below. Otherwise a parent that passes an inline function
  // re-runs this effect on every render and re-fires the OTP submission.
  const onOTPDetectedRef = useRef(onOTPDetected);
  onOTPDetectedRef.current = onOTPDetected;

  // Detect OTP and notify the parent. Keyed on the OTP *value* (a string), not
  // on the `queryParams` object reference — so the effect fires once per code,
  // not on every poll tick / re-render.
  useEffect(() => {
    if (!isReady || !otpValid) return;
    // Only on allowed paths to avoid conflicts with other pages
    // (e.g., /dashboard/device uses ?otp= for device authorization, not user auth)
    authLogger.info('OTP detected in URL on auth page:', queryOtp);
    onOTPDetectedRef.current?.(queryOtp, queryEmail);
  }, [isReady, otpValid, queryOtp, queryEmail]);

  // Clean up URL to remove sensitive params for security. Separate effect so it
  // does not depend on `onOTPDetected` and cannot re-trigger the submission.
  // Use window.location.pathname to preserve the locale prefix (e.g. /ru/auth)
  // because usePathname() strips the locale, and router.push('/auth') would cause
  // next-intl middleware to redirect back to /ru/auth — triggering a full page reload
  // that loses the in-flight OTP submission.
  useEffect(() => {
    if (!isReady || !cleanupUrl || !queryOtp) return;
    const cleanQuery = Object.fromEntries(queryParams.entries());
    delete cleanQuery.otp;
    delete cleanQuery.email;
    const queryString = new URLSearchParams(cleanQuery).toString();
    const realPathname = typeof window !== 'undefined' ? window.location.pathname : pathname;
    router.replace(queryString ? `${realPathname}?${queryString}` : realPathname);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isReady, cleanupUrl, queryOtp]);

  return {
    isReady,
    hasOTP,
    isAllowedPath,
  };
};
