import { useRouter } from 'next/router';
import { useEffect } from 'react';

export interface UseAutoAuthOptions {
  onOTPDetected?: (otp: string) => void;
  cleanupUrl?: boolean;
}

/**
 * Hook for automatic authentication from URL query parameters
 * Detects OTP from URL and triggers callback
 */
export const useAutoAuth = (options: UseAutoAuthOptions = {}) => {
  const { onOTPDetected, cleanupUrl = true } = options;
  const router = useRouter();

  useEffect(() => {
    if (!router.isReady) return;

    const queryOtp = router.query.otp as string;

    // Handle OTP detection
    if (queryOtp && typeof queryOtp === 'string' && queryOtp.length === 6) {
      console.log('[useAutoAuth] OTP detected in URL:', queryOtp);
      onOTPDetected?.(queryOtp);
    }

    // Clean up URL to remove sensitive params for security
    if (cleanupUrl && queryOtp) {
      const { otp: _, ...cleanQuery } = router.query;
      router.replace({
        pathname: router.pathname,
        query: cleanQuery
      }, undefined, { shallow: true });
    }
  }, [router.isReady, router.query, router.pathname, onOTPDetected, cleanupUrl]);

  return {
    isReady: router.isReady,
    hasOTP: !!(router.query.otp),
  };
};
