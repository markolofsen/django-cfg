/**
 * useQueryParams Hook
 * 
 * Safe hook to access URL query parameters without requiring Suspense boundary.
 * Works on client-side only, returns empty URLSearchParams during SSR/prerendering.
 * 
 * @example
 * ```tsx
 * const params = useQueryParams();
 * const flow = params.get('flow');
 * const hasFlow = params.has('flow');
 * const allTags = params.getAll('tags');
 * ```
 */

'use client';

import { usePathname } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';

/**
 * Hook to safely access URL query parameters without useSearchParams()
 * 
 * This hook reads query parameters directly from window.location.search,
 * avoiding the need for Suspense boundaries that useSearchParams() requires.
 * 
 * Automatically updates when URL changes (navigation, back/forward, etc.)
 * Uses pathname from Next.js to detect route changes and polls for query param changes.
 * 
 * Returns a URLSearchParams object with get(), getAll(), has(), etc.
 * 
 * @returns URLSearchParams object (empty during SSR)
 */
export function useQueryParams(): URLSearchParams {
  const pathname = usePathname();
  const [queryParams, setQueryParams] = useState<URLSearchParams>(() => {
    if (typeof window === 'undefined') {
      return new URLSearchParams();
    }
    return new URLSearchParams(window.location.search);
  });
  const lastSearchRef = useRef<string>('');

  useEffect(() => {
    if (typeof window === 'undefined') return;

    const updateQueryParams = () => {
      const currentSearch = window.location.search;
      if (currentSearch !== lastSearchRef.current) {
        lastSearchRef.current = currentSearch;
        setQueryParams(new URLSearchParams(currentSearch));
      }
    };

    // Sync on mount / pathname change (Next.js navigation).
    updateQueryParams();

    // back/forward navigation fires popstate natively.
    window.addEventListener('popstate', updateQueryParams);

    // Next.js router.push/replace updates the URL via history.pushState/replaceState,
    // which do NOT emit any event. Patch them to notify us, so we react to query-only
    // changes (same pathname) without polling. This replaces the old setInterval(100ms),
    // whose churning object reference helped drive the OTP auto-submit loop.
    const origPush = window.history.pushState;
    const origReplace = window.history.replaceState;
    window.history.pushState = function (...args) {
      const result = origPush.apply(this, args);
      updateQueryParams();
      return result;
    };
    window.history.replaceState = function (...args) {
      const result = origReplace.apply(this, args);
      updateQueryParams();
      return result;
    };

    return () => {
      window.removeEventListener('popstate', updateQueryParams);
      window.history.pushState = origPush;
      window.history.replaceState = origReplace;
    };
  }, [pathname]);

  return queryParams;
}

