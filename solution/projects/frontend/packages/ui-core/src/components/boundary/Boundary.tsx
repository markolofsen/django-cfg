'use client';

import { AlertTriangle, RotateCcw } from 'lucide-react';
import {
  Component,
  createContext,
  useContext,
  type ComponentType,
  type ErrorInfo,
  type ReactNode,
} from 'react';

import { canAutoReloadForChunk, isChunkLoadError, reloadForChunkError } from '../../lib/chunk-reload';
import { isDev } from '../../lib/env';
import { cn } from '../../lib/utils';
import { Button } from '../forms/button';

export type BoundaryVariant = 'silent' | 'inline' | 'card' | 'fullscreen';

export interface BoundaryRenderProps {
  error: Error;
  errorInfo: ErrorInfo | null;
  reset: () => void;
}

export type BoundaryResetReason = 'imperative' | 'keys';

export interface BoundaryResetDetails {
  reason: BoundaryResetReason;
  prevResetKeys?: ReadonlyArray<unknown>;
  nextResetKeys?: ReadonlyArray<unknown>;
}

export interface BoundaryLogger {
  (message: string, error: Error, info: ErrorInfo | null): void;
}

export interface BoundaryProps {
  children: ReactNode;
  /**
   * Visual style of the fallback.
   * - silent: render nothing (good for non-critical widgets like a chat launcher)
   * - inline: compact one-line warning (good for inline blocks inside a page)
   * - card: bordered card with retry button (default; good for panels/features)
   * - fullscreen: centered fullscreen fallback (good for top-level layout)
   * @default 'card'
   */
  variant?: BoundaryVariant;
  /**
   * Custom fallback. Receives the caught error and a reset() function.
   * Overrides `variant` rendering when provided.
   * Takes precedence over `FallbackComponent`.
   */
  fallback?: ReactNode | ((props: BoundaryRenderProps) => ReactNode);
  /**
   * Custom fallback component. Use this form instead of `fallback` for
   * better memoization (no inline closures).
   */
  FallbackComponent?: ComponentType<BoundaryRenderProps>;
  /**
   * Auto-reset the boundary when any of these values change (shallow Object.is per index).
   * Common use: pass `[pathname]` to clear errors on route change.
   * AVOID passing volatile values like `Math.random()` or new object/array literals — causes reset loops.
   */
  resetKeys?: ReadonlyArray<unknown>;
  /**
   * Called when an error is caught.
   * Hook up Sentry / logging / @djangocfg/devtools here.
   * Use the wrapping `MonitorBoundary` from @djangocfg/layouts for automatic reporting.
   */
  onError?: (error: Error, info: ErrorInfo) => void;
  /**
   * Called when the boundary recovers (via Retry button or resetKeys change).
   * Use it to refetch data / invalidate caches (e.g. React Query queryClient.invalidateQueries).
   */
  onReset?: (details: BoundaryResetDetails) => void;
  /**
   * Optional label shown in dev console logs to help locate the source.
   */
  name?: string;
  /**
   * Extra className for the fallback wrapper (variant: inline / card / fullscreen).
   */
  className?: string;
  /**
   * Replace default dev console logger. Defaults to `console.error` in development, no-op in production.
   */
  logger?: BoundaryLogger;
}

interface BoundaryState {
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

interface BoundaryContextValue {
  /** Programmatically push an error into the nearest boundary (use for async / event handler errors). */
  showBoundary: (error: unknown) => void;
  /** Programmatically clear the boundary (same as the Retry button). */
  resetBoundary: () => void;
}

const BoundaryContext = createContext<BoundaryContextValue | null>(null);

/**
 * Access the nearest `<Boundary>` programmatically.
 * Lets you funnel errors from async code / event handlers into the boundary
 * (regular React error boundaries don't catch those automatically).
 *
 * @example
 * const { showBoundary } = useBoundary();
 * useEffect(() => {
 *   fetchData().catch(showBoundary);
 * }, [showBoundary]);
 */
export function useBoundary(): BoundaryContextValue {
  const ctx = useContext(BoundaryContext);
  if (!ctx) {
    throw new Error('useBoundary must be used inside <Boundary>');
  }
  return ctx;
}

function arraysShallowEqual(a: ReadonlyArray<unknown>, b: ReadonlyArray<unknown>): boolean {
  if (a.length !== b.length) return false;
  for (let i = 0; i < a.length; i++) {
    if (!Object.is(a[i], b[i])) return false;
  }
  return true;
}

function toError(value: unknown): Error {
  if (value instanceof Error) return value;
  if (typeof value === 'string') return new Error(value);
  try {
    return new Error(JSON.stringify(value));
  } catch {
    return new Error('Unknown error');
  }
}

const defaultLogger: BoundaryLogger = (message, error, info) => {
  if (!isDev) return;
  console.error(message, error, info ?? '');
};

export class Boundary extends Component<BoundaryProps, BoundaryState> {
  override state: BoundaryState = { error: null, errorInfo: null };

  /** Stable context value identity — recreated only when error/reset functions change (i.e. on mount). */
  private contextValue: BoundaryContextValue = {
    showBoundary: (error: unknown) => this.showBoundary(error),
    resetBoundary: () => this.reset('imperative'),
  };

  /** Prevents `onError` from firing twice for the same error instance. */
  private lastReportedError: Error | null = null;

  /** True once a stale-chunk auto-reload was triggered; the fallback stays hidden meanwhile. */
  private chunkReloading = false;

  static getDerivedStateFromError(error: unknown): BoundaryState {
    return { error: toError(error), errorInfo: null };
  }

  override componentDidCatch(error: Error, info: ErrorInfo) {
    const normalized = toError(error);
    // Stale chunk after a deploy: one guarded hard reload instead of the crash screen.
    if (isChunkLoadError(normalized) && reloadForChunkError()) this.chunkReloading = true;
    this.setState({ errorInfo: info });

    if (this.lastReportedError === normalized) return;
    this.lastReportedError = normalized;

    try {
      this.props.onError?.(normalized, info);
    } catch (callbackErr) {
      // Never let user's onError crash the boundary.
      (this.props.logger ?? defaultLogger)(
        `[Boundary${this.props.name ? `:${this.props.name}` : ''}] onError handler threw`,
        toError(callbackErr),
        null,
      );
    }

    const tag = this.props.name ? `[Boundary:${this.props.name}]` : '[Boundary]';
    (this.props.logger ?? defaultLogger)(`${tag} caught error`, normalized, info);
  }

  override componentDidUpdate(prevProps: BoundaryProps) {
    if (!this.state.error) return;
    const prevKeys = prevProps.resetKeys;
    const nextKeys = this.props.resetKeys;
    if (prevKeys && nextKeys && !arraysShallowEqual(prevKeys, nextKeys)) {
      this.reset('keys', prevKeys, nextKeys);
    }
  }

  /** Imperatively raise an error from async code / event handlers via `useBoundary()`. */
  showBoundary = (raw: unknown) => {
    const error = toError(raw);
    this.setState({ error, errorInfo: null });
  };

  reset = (
    reason: BoundaryResetReason = 'imperative',
    prevResetKeys?: ReadonlyArray<unknown>,
    nextResetKeys?: ReadonlyArray<unknown>,
  ) => {
    // Clear state BEFORE calling onReset — otherwise an error thrown
    // inside onReset would re-trigger the boundary before state is cleared.
    this.lastReportedError = null;
    this.setState({ error: null, errorInfo: null });

    // Defer onReset to a microtask so the state clear is flushed first.
    queueMicrotask(() => {
      try {
        this.props.onReset?.({ reason, prevResetKeys, nextResetKeys });
      } catch (err) {
        (this.props.logger ?? defaultLogger)(
          `[Boundary${this.props.name ? `:${this.props.name}` : ''}] onReset handler threw`,
          toError(err),
          null,
        );
      }
    });
  };

  /** Wraps fallback rendering so errors in the fallback itself can't crash the boundary. */
  private safeRenderFallback(): ReactNode {
    const { error, errorInfo } = this.state;
    if (!error) return null;
    if (isChunkLoadError(error) && (this.chunkReloading || canAutoReloadForChunk())) return null;

    const { fallback, FallbackComponent, variant = 'card', className } = this.props;

    try {
      if (typeof fallback === 'function') {
        return fallback({ error, errorInfo, reset: () => this.reset('imperative') });
      }
      if (fallback !== undefined) {
        return fallback;
      }
      if (FallbackComponent) {
        return (
          <FallbackComponent
            error={error}
            errorInfo={errorInfo}
            reset={() => this.reset('imperative')}
          />
        );
      }
      return renderVariant(variant, error, () => this.reset('imperative'), className);
    } catch (fallbackError) {
      // Last-resort static fallback — prevents infinite loops if user fallback throws.
      (this.props.logger ?? defaultLogger)(
        `[Boundary${this.props.name ? `:${this.props.name}` : ''}] fallback render threw`,
        toError(fallbackError),
        null,
      );
      return (
        <div
          role="alert"
          aria-live="assertive"
          className="p-2 text-sm text-destructive border border-destructive/40 rounded"
        >
          Something went wrong, and the error fallback also failed to render.
        </div>
      );
    }
  }

  override render() {
    if (this.state.error) {
      return this.safeRenderFallback();
    }
    return (
      <BoundaryContext.Provider value={this.contextValue}>
        {this.props.children}
      </BoundaryContext.Provider>
    );
  }
}

function renderVariant(
  variant: BoundaryVariant,
  error: Error,
  reset: () => void,
  className?: string,
): ReactNode {
  if (variant === 'silent') return null;

  const message = isDev ? error.message : null;

  if (variant === 'inline') {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className={cn(
          'flex items-center gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive',
          className,
        )}
      >
        <AlertTriangle className="h-4 w-4 shrink-0" />
        <span className="flex-1 truncate">{message ?? 'Something went wrong.'}</span>
        <button
          type="button"
          onClick={reset}
          className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-xs font-medium underline-offset-2 hover:underline"
        >
          <RotateCcw className="h-3 w-3" />
          Retry
        </button>
      </div>
    );
  }

  if (variant === 'fullscreen') {
    return (
      <div
        role="alert"
        aria-live="assertive"
        className={cn('flex min-h-[var(--app-height,100dvh)] items-center justify-center bg-background p-4', className)}
      >
        <div className="max-w-md w-full space-y-4 text-center">
          <AlertTriangle className="mx-auto h-10 w-10 text-destructive" />
          <h1 className="text-2xl font-bold text-foreground">Something went wrong</h1>
          <p className="text-muted-foreground">
            We&apos;re sorry, but something unexpected happened. Please try refreshing the page.
          </p>
          {message && (
            <pre className="text-left text-xs text-muted-foreground bg-muted rounded p-2 overflow-auto max-h-40">
              {message}
            </pre>
          )}
          <div className="flex justify-center gap-2">
            <Button variant="outline" onClick={reset}>
              <RotateCcw className="mr-2 h-4 w-4" />
              Try again
            </Button>
            <Button onClick={() => window.location.reload()}>Refresh page</Button>
          </div>
        </div>
      </div>
    );
  }

  // card (default)
  return (
    <div
      role="alert"
      aria-live="assertive"
      className={cn(
        'rounded-[var(--radius)] border border-destructive/40 bg-destructive/5 p-4 text-sm',
        className,
      )}
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
        <div className="flex-1 space-y-2">
          <p className="font-medium text-destructive">Something went wrong</p>
          {message && <p className="text-xs text-muted-foreground break-words">{message}</p>}
          <Button size="sm" variant="outline" onClick={reset}>
            <RotateCcw className="mr-2 h-3 w-3" />
            Try again
          </Button>
        </div>
      </div>
    </div>
  );
}
