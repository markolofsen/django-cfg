'use client';

/**
 * The lazy seam, inlined rather than imported.
 *
 * Upstream this is `@djangocfg/widget-kit/lazy`, and the map used exactly two
 * of its exports. Depending on the whole module for those two would pull in
 * its i18n copy layer and five placeholder variants sized for editors and chat
 * composers — surfaces this package does not have. Thirty lines is the smaller
 * seam, and it keeps `widgets/map` dependent on `ui-core` alone.
 *
 * `MapLoadingFallback` is deliberately a plain block, not upstream's spinner
 * over a pin glyph: the map mounts behind a `LazyMapContainer` inside a fixed
 * canvas, so the placeholder's only job is to hold the space without drawing
 * the eye to a load the visitor did not ask for.
 */

import * as React from 'react';
import { Suspense, type ComponentType, type ReactNode } from 'react';
import { cn } from '@djangocfg/ui-core/lib';

export function MapLoadingFallback({
  minHeight = 400,
  className,
}: {
  minHeight?: string | number;
  className?: string;
}) {
  const height = typeof minHeight === 'number' ? `${minHeight}px` : minHeight;

  return (
    <div
      className={cn('bg-muted/50 relative overflow-hidden rounded-lg', className)}
      style={{ minHeight: height }}
      role="status"
      aria-label="Loading map"
    />
  );
}

type CreateLazyComponentOptions<P> = {
  displayName?: string;
  fallback?: ReactNode | ((props: P) => ReactNode);
};

export function createLazyComponent<P extends object>(
  loader: () => Promise<{ default: ComponentType<P> }>,
  options: CreateLazyComponentOptions<P> = {},
): ComponentType<P> {
  const LazyComponent = React.lazy(loader);

  const WrappedComponent = (props: P) => {
    const fallback =
      typeof options.fallback === 'function'
        ? options.fallback(props)
        : (options.fallback ?? <MapLoadingFallback />);

    return (
      <Suspense fallback={fallback}>
        <LazyComponent {...props} />
      </Suspense>
    );
  };

  WrappedComponent.displayName = options.displayName ?? 'LazyComponent';

  return WrappedComponent;
}
