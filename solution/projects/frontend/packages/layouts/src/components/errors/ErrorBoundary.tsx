/**
 * ErrorBoundary — the i18n'd, support-email fallback for Next app layouts.
 *
 * Thin wrapper over the ui-core `Boundary` primitive: ui-core owns the catch
 * machinery (getDerivedStateFromError / componentDidCatch / reset), this layer
 * only supplies a localized fullscreen fallback + an optional support email.
 * One catch implementation across the stack — UiProviders' built-in boundary,
 * MonitorBoundary, and this all build on the same ui-core Boundary.
 */

'use client';

import { useMemo, type ComponentType, type ErrorInfo, type ReactNode } from 'react';

import { Boundary, type BoundaryRenderProps } from '@djangocfg/ui-core/components';
import { AppErrorFallback } from './AppErrorFallback';

interface ErrorBoundaryProps {
  children: ReactNode;
  supportEmail?: string;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

export function ErrorBoundary({ children, supportEmail, onError }: ErrorBoundaryProps) {
  // Memoize so the boundary's FallbackComponent identity is stable across
  // renders (no remount churn).
  const Fallback = useMemo<ComponentType<BoundaryRenderProps>>(
    () => function ErrorFallback() {
      return <AppErrorFallback supportEmail={supportEmail} />;
    },
    [supportEmail],
  );
  return (
    <Boundary
      variant="fullscreen"
      name="layouts-error-boundary"
      onError={onError}
      FallbackComponent={Fallback}
    >
      {children}
    </Boundary>
  );
}
