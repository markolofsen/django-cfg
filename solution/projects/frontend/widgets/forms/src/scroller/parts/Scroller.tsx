'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from 'lucide-react';
import { ScrollerProvider, useScrollerContext } from '../context';
import type {
  ScrollerProps,
  ScrollerItemProps,
  ScrollerIndicatorProps,
  SnapAlign,
} from '../types';

/**
 * Static map of literal snap-align classes.
 *
 * Tailwind only compiles classes it can see, so a runtime-built
 * `snap-${snapAlign}` is never emitted — the item carried a
 * `data-snap-align` attribute that made it look wired up while no snap
 * class existed. Same rule, same fix as `GRID_COL_CLASS` in
 * `json-form/templates/ObjectFieldTemplate.tsx`.
 */
const SNAP_ALIGN_CLASS: Record<Exclude<SnapAlign, 'none'>, string> = {
  start: 'snap-start',
  center: 'snap-center',
  end: 'snap-end',
};

export function Scroller({
  children,
  orientation = 'horizontal',
  snap = false,
  snapAlign = 'start',
  showIndicators = false,
  hideScrollbar = true,
  className,
  ...props
}: ScrollerProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [canScrollPrev, setCanScrollPrev] = React.useState(false);
  const [canScrollNext, setCanScrollNext] = React.useState(false);

  const checkScroll = React.useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    if (orientation === 'horizontal') {
      setCanScrollPrev(el.scrollLeft > 0);
      setCanScrollNext(el.scrollLeft + el.clientWidth < el.scrollWidth - 1);
    } else {
      setCanScrollPrev(el.scrollTop > 0);
      setCanScrollNext(el.scrollTop + el.clientHeight < el.scrollHeight - 1);
    }
  }, [orientation]);

  React.useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    checkScroll();
    el.addEventListener('scroll', checkScroll, { passive: true });
    window.addEventListener('resize', checkScroll);
    return () => {
      el.removeEventListener('scroll', checkScroll);
      window.removeEventListener('resize', checkScroll);
    };
  }, [checkScroll]);

  const scrollBy = React.useCallback(
    (direction: 'prev' | 'next') => {
      const el = containerRef.current;
      if (!el) return;
      const amount =
        orientation === 'horizontal' ? el.clientWidth * 0.8 : el.clientHeight * 0.8;
      const delta = direction === 'next' ? amount : -amount;
      if (orientation === 'horizontal') {
        el.scrollBy({ left: delta, behavior: 'smooth' });
      } else {
        el.scrollBy({ top: delta, behavior: 'smooth' });
      }
    },
    [orientation]
  );

  const snapStyle = snap
    ? {
        scrollSnapType: `${orientation === 'horizontal' ? 'x' : 'y'} mandatory`,
      } as React.CSSProperties
    : undefined;

  const value = React.useMemo(
    () => ({ containerRef, orientation, snapAlign }),
    [orientation, snapAlign]
  );

  return (
    <ScrollerProvider value={value}>
      <div
        data-slot="scroller"
        data-orientation={orientation}
        className={cn('relative group', className)}
        {...props}
      >
        <div
          ref={containerRef}
          data-slot="scroller-viewport"
          className={cn(
            'flex',
            orientation === 'horizontal'
              ? 'flex-row overflow-x-auto'
              : 'flex-col overflow-y-auto',
            hideScrollbar && 'scrollbar-hide',
            // The axis has to follow `orientation`: a vertical scroller was
            // asking to snap on x, which is the axis it does not scroll.
            snap &&
              (orientation === 'horizontal'
                ? 'snap-x snap-mandatory'
                : 'snap-y snap-mandatory')
          )}
          style={snapStyle}
        >
          {children}
        </div>
        {showIndicators && canScrollPrev && (
          <ScrollerIndicator
            direction={orientation === 'horizontal' ? 'prev' : 'prev'}
            onClick={() => scrollBy('prev')}
            disabled={!canScrollPrev}
            className={cn(
              'absolute z-10',
              orientation === 'horizontal'
                ? 'left-2 top-1/2 -translate-y-1/2'
                : 'top-2 left-1/2 -translate-x-1/2'
            )}
          />
        )}
        {showIndicators && canScrollNext && (
          <ScrollerIndicator
            direction={orientation === 'horizontal' ? 'next' : 'next'}
            onClick={() => scrollBy('next')}
            disabled={!canScrollNext}
            className={cn(
              'absolute z-10',
              orientation === 'horizontal'
                ? 'right-2 top-1/2 -translate-y-1/2'
                : 'bottom-2 left-1/2 -translate-x-1/2'
            )}
          />
        )}
      </div>
    </ScrollerProvider>
  );
}
Scroller.displayName = 'Scroller';

export function ScrollerItem({
  children,
  snapAlign,
  className,
  ...props
}: ScrollerItemProps) {
  const { orientation, snapAlign: inherited } = useScrollerContext();
  // No default in the signature: `undefined` is what "inherit" looks like, and
  // defaulting here would make every item override the parent with `'start'`.
  const resolved = snapAlign ?? inherited;
  return (
    <div
      data-slot="scroller-item"
      data-snap-align={resolved}
      className={cn(
        'shrink-0',
        resolved !== 'none' && SNAP_ALIGN_CLASS[resolved],
        orientation === 'horizontal' ? 'w-fit' : 'h-fit',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
ScrollerItem.displayName = 'ScrollerItem';

function ScrollerIndicator({
  direction,
  onClick,
  disabled,
  className,
}: ScrollerIndicatorProps) {
  const { orientation } = useScrollerContext();
  const Icon =
    orientation === 'horizontal'
      ? direction === 'prev'
        ? ChevronLeft
        : ChevronRight
      : direction === 'prev'
        ? ChevronUp
        : ChevronDown;

  return (
    <button
      type="button"
      data-slot="scroller-indicator"
      data-direction={direction}
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'flex h-8 w-8 items-center justify-center rounded-full',
        'bg-background/90 text-foreground shadow-md backdrop-blur-sm',
        'border border-border/50 transition-opacity hover:bg-background',
        'disabled:opacity-0',
        className
      )}
    >
      <Icon className="h-4 w-4" />
    </button>
  );
}
ScrollerIndicator.displayName = 'ScrollerIndicator';
