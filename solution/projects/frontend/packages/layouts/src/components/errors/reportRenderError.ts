import type { ErrorInfo } from 'react';

import { EventLevel, EventType, devtools } from '@djangocfg/devtools';

/**
 * Send a render error caught by an error boundary to the backend monitor.
 *
 * A boundary swallows the error: React renders the fallback and the exception
 * never reaches `window.onerror`, so devtools' global capture cannot see it. This
 * is the one place that reports it. It queues the event and flushes at once (the
 * fallback's "Reload" can unload the page before the 5 s timer fires); the flush
 * on `visibilitychange: hidden` still goes out with keepalive.
 *
 * Never throws: monitoring must not crash the boundary.
 */
export function reportRenderError(source: string, error: Error, info?: ErrorInfo): void {
  try {
    devtools.capture({
      event_type: EventType.ERROR,
      level: EventLevel.ERROR,
      message: error.message || 'Unhandled React render error',
      stack_trace: error.stack,
      url: typeof window !== 'undefined' ? window.location.href : undefined,
      extra: {
        source,
        componentStack: info?.componentStack,
        errorName: error.name,
      },
    });
    devtools.flush();
  } catch {
    // ignore
  }
}
