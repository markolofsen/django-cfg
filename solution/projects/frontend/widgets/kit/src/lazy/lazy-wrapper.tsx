'use client';

import * as React from 'react';
import { Suspense, type ReactNode, type ComponentType } from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { lazyCopy } from './copy';

// ============================================================================
// Loading Fallback Components
// ============================================================================

export interface LoadingFallbackProps {
  /** Minimum height of the loading container */
  minHeight?: string | number;
  /** Show loading text */
  showText?: boolean;
  /** Custom loading text */
  text?: string;
  /** Additional CSS classes */
  className?: string;
}

/**
 * Spinner - Simple spinning loader.
 *
 * Compact by default: a 16px ring at 2px weight, `currentColor` (inherits the
 * parent's text color) so a caller sets tone with a `text-*` class. This is the
 * quiet, component-level size — a dynamic-import placeholder, not a page event.
 * Override the size/weight via `className` when a larger disc is wanted.
 */
export function Spinner({ className }: { className?: string }) {
  const { loadingLabel } = lazyCopy();

  return (
    <div
      className={cn(
        'inline-block size-4 animate-spin rounded-full',
        'border-2 border-solid border-current border-r-transparent',
        'align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]',
        className
      )}
      role="status"
      aria-label={loadingLabel}
    />
  );
}

/**
 * InlineLoadingFallback — placeholder for a lazy editor that occupies an
 * INPUT-sized slot (the chat composer, an inline field), not a panel.
 *
 * Deliberately smaller and quieter than `LoadingFallback`, which is sized for
 * a page-level panel (200–320px block, 32px disc, caption underneath). Dropped
 * into a one-line composer that reads as a component that failed to appear.
 * Here the placeholder should be barely noticeable and occupy exactly the room
 * the field will take, so nothing shifts when TipTap mounts:
 *   - no filled block, no caption — the spinner alone says "a moment";
 *   - 14px ring at 2px, the weight of a caret rather than a page spinner;
 *   - `muted-foreground`, not `primary`: this is not an event the user asked
 *     for or can act on.
 *
 * `label` is for assistive tech only; pass `text` to also show it (rarely
 * wanted at this size).
 */
export function InlineLoadingFallback({
  text,
  className,
}: {
  /** Optional visible caption. Omit for the bare spinner. */
  text?: string;
  className?: string;
}) {
  const label = text ?? lazyCopy().loading;

  return (
    <div
      className={cn('flex items-center gap-2 px-2 py-1.5 text-muted-foreground', className)}
      role="status"
      aria-label={text ? undefined : label}
    >
      <Spinner className="h-3.5 w-3.5 border-2 text-muted-foreground/70" />
      {text && <span className="text-sm">{text}</span>}
    </div>
  );
}

/**
 * LoadingFallback — default loading state for lazy (dynamic-import) components.
 *
 * Quiet by design: a compact 16px `muted-foreground` spinner with the caption
 * on the SAME line, centered, on a bare surface (no filled `bg-muted` block).
 * A dynamic import resolving is not an event the user asked for or can act on,
 * so the placeholder should barely register and not paint a colored panel where
 * the real component will land. `minHeight` defaults small (96px) so it reserves
 * just enough room without a tall empty box; pass a larger value for a
 * page-level panel.
 */
export function LoadingFallback({
  minHeight = 96,
  showText = true,
  text,
  className,
}: LoadingFallbackProps) {
  const loadingText = text ?? lazyCopy().loading;
  const height = typeof minHeight === 'number' ? `${minHeight}px` : minHeight;

  return (
    <div
      className={cn('flex items-center justify-center', className)}
      style={{ minHeight: height }}
      role="status"
      aria-label={showText ? undefined : loadingText}
    >
      <div className="flex items-center gap-2 text-muted-foreground">
        <Spinner className="size-4" />
        {showText && <span className="text-sm">{loadingText}</span>}
      </div>
    </div>
  );
}

/**
 * CardLoadingFallback - Loading state styled as a card
 */
export function CardLoadingFallback({
  title,
  description,
  minHeight = 200,
  className,
}: {
  title?: string;
  description?: string;
  minHeight?: string | number;
  className?: string;
}) {
  const cardTitle = title ?? lazyCopy().loadingLabel;
  const height = typeof minHeight === 'number' ? `${minHeight}px` : minHeight;

  return (
    <div
      className={cn(
        'relative bg-card rounded-lg border border-border overflow-hidden',
        className
      )}
    >
      <div className="p-4 border-b border-border bg-muted/50">
        <h6 className="text-sm font-semibold text-foreground">{cardTitle}</h6>
        {description && (
          <p className="text-xs text-muted-foreground mt-1">{description}</p>
        )}
      </div>
      <div className="p-4">
        <div
          className="flex justify-center items-center"
          style={{ minHeight: height }}
        >
          <Spinner className="text-primary" />
        </div>
      </div>
    </div>
  );
}

/**
 * MapLoadingFallback - Loading state for map components
 */
export function MapLoadingFallback({
  minHeight = 400,
  className,
}: {
  minHeight?: string | number;
  className?: string;
}) {
  const loadingText = lazyCopy().loading;
  const height = typeof minHeight === 'number' ? `${minHeight}px` : minHeight;

  return (
    <div
      className={cn(
        'relative bg-muted/50 rounded-lg overflow-hidden',
        'flex items-center justify-center',
        className
      )}
      style={{ minHeight: height }}
    >
      <div className="text-center">
        <div className="relative">
          <Spinner className="text-primary h-10 w-10" />
          <div className="absolute inset-0 flex items-center justify-center">
            <svg
              className="h-5 w-5 text-muted-foreground"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
          </div>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">{loadingText}</p>
      </div>
    </div>
  );
}

// ============================================================================
// Lazy Wrapper
// ============================================================================

export interface LazyWrapperProps {
  children: ReactNode;
  /** Custom fallback component */
  fallback?: ReactNode;
  /** Use card-style fallback */
  card?: boolean;
  /** Card title (when card=true) */
  cardTitle?: string;
  /** Card description (when card=true) */
  cardDescription?: string;
  /** Minimum height for fallback */
  minHeight?: string | number;
  /** Additional CSS classes for fallback */
  className?: string;
}

/**
 * LazyWrapper - Suspense wrapper with configurable fallbacks
 *
 * @example
 * // Basic usage
 * <LazyWrapper>
 *   <LazyComponent />
 * </LazyWrapper>
 *
 * @example
 * // Card style fallback
 * <LazyWrapper card cardTitle="Diagram" minHeight={300}>
 *   <Mermaid chart={...} />
 * </LazyWrapper>
 *
 * @example
 * // Custom fallback
 * <LazyWrapper fallback={<MyCustomLoader />}>
 *   <HeavyComponent />
 * </LazyWrapper>
 */
export function LazyWrapper({
  children,
  fallback,
  card = false,
  cardTitle,
  cardDescription,
  minHeight = 200,
  className,
}: LazyWrapperProps) {
  const defaultFallback = card ? (
    <CardLoadingFallback
      title={cardTitle}
      description={cardDescription}
      minHeight={minHeight}
      className={className}
    />
  ) : (
    <LoadingFallback minHeight={minHeight} className={className} />
  );

  return <Suspense fallback={fallback ?? defaultFallback}>{children}</Suspense>;
}

// ============================================================================
// Lazy Component Factory
// ============================================================================

export interface CreateLazyComponentOptions<P> {
  /** Loading fallback component */
  fallback?: ReactNode | ((props: P) => ReactNode);
  /** Display name for the component */
  displayName?: string;
}

/**
 * createLazyComponent - Factory for creating lazy-loaded components
 *
 * @example
 * const LazyMermaid = createLazyComponent(
 *   () => import('./Mermaid.client'),
 *   {
 *     displayName: 'Mermaid',
 *     fallback: <CardLoadingFallback title="Diagram" />,
 *   }
 * );
 */
export function createLazyComponent<P extends object>(
  loader: () => Promise<{ default: ComponentType<P> }>,
  options: CreateLazyComponentOptions<P> = {}
): ComponentType<P> {
  const LazyComponent = React.lazy(loader);

  const WrappedComponent = (props: P) => {
    const fallback =
      typeof options.fallback === 'function'
        ? options.fallback(props)
        : options.fallback ?? <LoadingFallback />;

    return (
      <Suspense fallback={fallback}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };

  WrappedComponent.displayName = options.displayName ?? 'LazyComponent';

  return WrappedComponent;
}
