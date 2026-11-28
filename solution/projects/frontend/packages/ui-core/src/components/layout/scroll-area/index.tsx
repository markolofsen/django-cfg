"use client"

import * as React from 'react';

import * as ScrollAreaPrimitive from '@radix-ui/react-scroll-area';

import { cn } from '../../../lib/utils';

/**
 * ScrollArea imperative handle for programmatic control
 */
export interface ScrollAreaHandle {
  /** Scroll to bottom of the content */
  scrollToBottom: (behavior?: ScrollBehavior) => void;
  /** Scroll to top of the content */
  scrollToTop: (behavior?: ScrollBehavior) => void;
  /** Scroll to a specific position */
  scrollTo: (options: ScrollToOptions) => void;
  /** Get the viewport element */
  getViewport: () => HTMLDivElement | null;
}

export type ScrollAreaOrientation = 'vertical' | 'horizontal' | 'both';

export interface ScrollAreaProps
  extends React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.Root> {
  /** Ref to access the viewport element directly */
  viewportRef?: React.RefObject<HTMLDivElement | null>;
  /** Additional className for the viewport */
  viewportClassName?: string;
  /** Scroll orientation: vertical (default), horizontal, or both */
  orientation?: ScrollAreaOrientation;
  /** Control horizontal overflow on the viewport (default: auto) */
  overflowX?: 'auto' | 'hidden' | 'scroll';
}

const ScrollArea = React.forwardRef<ScrollAreaHandle, ScrollAreaProps>(
  ({ className, children, viewportRef, viewportClassName, orientation = 'vertical', overflowX, ...props }, ref) => {
    const internalViewportRef = React.useRef<HTMLDivElement>(null);
    const actualViewportRef = viewportRef || internalViewportRef;

    // Expose imperative methods
    React.useImperativeHandle(ref, () => ({
      scrollToBottom: (behavior: ScrollBehavior = 'smooth') => {
        const viewport = actualViewportRef.current;
        if (viewport) {
          viewport.scrollTo({
            top: viewport.scrollHeight,
            behavior,
          });
        }
      },
      scrollToTop: (behavior: ScrollBehavior = 'smooth') => {
        const viewport = actualViewportRef.current;
        if (viewport) {
          viewport.scrollTo({
            top: 0,
            behavior,
          });
        }
      },
      scrollTo: (options: ScrollToOptions) => {
        actualViewportRef.current?.scrollTo(options);
      },
      getViewport: () => actualViewportRef.current,
    }), [actualViewportRef]);

    const showVerticalBar = orientation === 'vertical' || orientation === 'both';
    const showHorizontalBar = orientation === 'horizontal' || orientation === 'both';

    return (
      <ScrollAreaPrimitive.Root
        className={cn("relative overflow-hidden", className)}
        {...props}
      >
        <ScrollAreaPrimitive.Viewport
          ref={actualViewportRef as React.RefObject<HTMLDivElement>}
          className={cn(
            "h-full w-full rounded-[inherit]",
            overflowX === 'hidden' && "!overflow-x-hidden",
            overflowX === 'scroll' && "!overflow-x-scroll",
            viewportClassName,
          )}
        >
          {children}
        </ScrollAreaPrimitive.Viewport>
        {showVerticalBar && <ScrollBar orientation="vertical" />}
        {showHorizontalBar && <ScrollBar orientation="horizontal" />}
        <ScrollAreaPrimitive.Corner />
      </ScrollAreaPrimitive.Root>
    );
  }
);
ScrollArea.displayName = "ScrollArea"

const ScrollBar = React.forwardRef<
  React.ElementRef<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>,
  React.ComponentPropsWithoutRef<typeof ScrollAreaPrimitive.ScrollAreaScrollbar>
>(({ className, orientation = "vertical", ...props }, ref) => (
  <ScrollAreaPrimitive.ScrollAreaScrollbar
    ref={ref}
    orientation={orientation}
    className={cn(
      "flex touch-none select-none transition-colors",
      orientation === "vertical" &&
        "h-full w-2.5 border-l border-l-transparent p-[1px]",
      orientation === "horizontal" &&
        "h-2.5 flex-col border-t border-t-transparent p-[1px]",
      className
    )}
    {...props}
  >
    <ScrollAreaPrimitive.ScrollAreaThumb className="relative flex-1 rounded-full bg-border" />
  </ScrollAreaPrimitive.ScrollAreaScrollbar>
))
ScrollBar.displayName = ScrollAreaPrimitive.ScrollAreaScrollbar.displayName

export { ScrollArea, ScrollBar }
