'use client';

import { Boundary } from '@djangocfg/ui-core/components';
import type {
  BoundaryProps,
  BoundaryResetDetails,
} from '@djangocfg/ui-core/components';
import { EventLevel, EventType, devtools } from '@djangocfg/devtools';
import { useCallback } from 'react';

import { reportRenderError } from './reportRenderError';
import type { ErrorInfo, ReactNode } from 'react';

export interface MonitorBoundaryProps extends Omit<BoundaryProps, 'onError' | 'onReset'> {
  /** Forwarded to devtools as `extra.source` so you can filter events by boundary. */
  name?: string;
  /** Additional render-error handler called alongside the monitor capture. */
  onError?: (error: Error, info: ErrorInfo) => void;
  /** Additional reset handler called alongside the monitor breadcrumb. */
  onReset?: (details: BoundaryResetDetails) => void;
  /** Disable monitor reporting (still catches and renders fallback). */
  reportToMonitor?: boolean;
  children: ReactNode;
}

function currentUrl(): string | undefined {
  return typeof window !== 'undefined' ? window.location.href : undefined;
}

function reportError(name: string | undefined, error: Error, info: ErrorInfo): void {
  reportRenderError(name ?? 'boundary', error, info);
}

function reportReset(name: string | undefined, details: BoundaryResetDetails): void {
  try {
    devtools.capture({
      event_type: EventType.ERROR,
      level: EventLevel.INFO,
      message: `Boundary recovered (${details.reason})`,
      url: currentUrl(),
      extra: {
        source: name ?? 'boundary',
        reason: details.reason,
      },
    });
  } catch {
    // ignore
  }
}

/**
 * `Boundary` + automatic reporting to `@djangocfg/devtools`.
 *
 * Use at page/layout level so unexpected render errors are captured in your backend.
 * For widgets you don't want to report (chat, embeds), use `Boundary` from ui-core directly.
 */
export function MonitorBoundary({
  name,
  onError,
  onReset,
  reportToMonitor = true,
  ...rest
}: MonitorBoundaryProps) {
  const handleError = useCallback(
    (error: Error, info: ErrorInfo) => {
      if (reportToMonitor) reportError(name, error, info);
      onError?.(error, info);
    },
    [name, onError, reportToMonitor],
  );

  const handleReset = useCallback(
    (details: BoundaryResetDetails) => {
      if (reportToMonitor) reportReset(name, details);
      onReset?.(details);
    },
    [name, onReset, reportToMonitor],
  );

  return <Boundary {...rest} name={name} onError={handleError} onReset={handleReset} />;
}
