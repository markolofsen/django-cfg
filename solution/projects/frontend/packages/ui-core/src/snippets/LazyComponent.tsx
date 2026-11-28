/**
 * LazyComponent - Universal lazy loading wrapper
 *
 * Provides consistent Suspense handling for lazy-loaded components
 * Works in any React environment: Next.js, Vite, Wails, CRA
 */

'use client';

import React, { Suspense, ReactNode, ComponentType, LazyExoticComponent, lazy } from 'react';

// Default loading spinner
export const DefaultLoader = () => (
  <div className="flex items-center justify-center p-8">
    <div className="flex flex-col items-center gap-2">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-muted border-t-primary" />
      <span className="text-sm text-muted-foreground">Loading...</span>
    </div>
  </div>
);

// Minimal loader for inline components
export const InlineLoader = () => (
  <span className="inline-flex items-center gap-1">
    <span className="h-3 w-3 animate-spin rounded-full border-2 border-muted border-t-primary" />
    <span className="text-xs text-muted-foreground">Loading...</span>
  </span>
);

// Full-screen loader
export const FullScreenLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent" />
      <p className="mt-4 text-sm text-muted-foreground">Loading...</p>
    </div>
  </div>
);

export interface LazyWrapperProps {
  children: ReactNode;
  fallback?: ReactNode;
}

/**
 * Suspense wrapper with default fallback
 */
export function LazyWrapper({ children, fallback }: LazyWrapperProps) {
  return (
    <Suspense fallback={fallback ?? <DefaultLoader />}>
      {children}
    </Suspense>
  );
}

/**
 * Create a lazy-loaded component with Suspense wrapper built-in
 *
 * @example
 * ```tsx
 * const HeavyComponent = createLazyComponent(
 *   () => import('./HeavyComponent'),
 *   <CustomLoader />
 * );
 *
 * // Usage - no need to wrap in Suspense
 * <HeavyComponent someProps={value} />
 * ```
 */
export function createLazyComponent<P extends object>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  fallback?: ReactNode
) {
  const LazyComponent = lazy(importFn);

  return function WrappedLazyComponent(props: P) {
    return (
      <Suspense fallback={fallback ?? <DefaultLoader />}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };
}

/**
 * Create a lazy-loaded component from a named export
 *
 * @example
 * ```tsx
 * const NamedComponent = createLazyNamedComponent(
 *   () => import('./module'),
 *   'NamedExport',
 *   <CustomLoader />
 * );
 * ```
 */
export function createLazyNamedComponent<
  P extends object,
  K extends string = string
>(
  importFn: () => Promise<Record<K, ComponentType<P>>>,
  exportName: K,
  fallback?: ReactNode
) {
  const LazyComponent: LazyExoticComponent<ComponentType<P>> = lazy(() =>
    importFn().then((mod) => ({ default: mod[exportName] }))
  );

  return function WrappedLazyComponent(props: P) {
    return (
      <Suspense fallback={fallback ?? <DefaultLoader />}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };
}
