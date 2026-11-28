/**
 * Suspense Wrapper Component
 * 
 * Reusable Suspense component with consistent loading fallback
 * Used for wrapping layouts that may use useSearchParams or other async hooks
 */

'use client';

import { ReactNode, Suspense as ReactSuspense } from 'react';

interface SuspenseProps {
  children: ReactNode;
  fallback?: ReactNode;
}

const defaultFallback = (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
      <p className="mt-4 text-sm text-muted-foreground">Loading...</p>
    </div>
  </div>
);

export function Suspense({ children, fallback = defaultFallback }: SuspenseProps) {
  return <ReactSuspense fallback={fallback}>{children}</ReactSuspense>;
}

