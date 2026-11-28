"use client"

import * as React from 'react';
import { Drawer as DrawerPrimitive } from 'vaul';

import { cn } from '../../../lib/utils';
import { useIsMobile } from '../../../hooks/media/useMobile';

type DrawerDirection = 'bottom' | 'right' | 'left' | 'top';

// Context lets <DrawerContent /> inherit what the Root was configured with,
// without callers having to pass it twice (a frequent rebase / refactor
// footgun). `snapPoints` matters to the content because the two own the panel's
// geometry differently — see the note where it is read.
const DrawerRootContext = React.createContext<{
  direction?: DrawerDirection;
  hasSnapPoints: boolean;
}>({ hasSnapPoints: false });

/** @internal — used by DrawerContent to inherit `direction` from the Root. */
export const useDrawerDirection = () => React.useContext(DrawerRootContext).direction;

/** @internal — true when the Root was given `snapPoints`. */
const useDrawerHasSnapPoints = () => React.useContext(DrawerRootContext).hasSnapPoints;

const Drawer = ({
  shouldScaleBackground,
  direction = 'bottom',
  ...props
}: React.ComponentProps<typeof DrawerPrimitive.Root> & { direction?: DrawerDirection }) => {
  // vaul's body-scale animation is a mobile-bottom-sheet effect by design.
  // Applying it to side drawers (right/left) keeps the <body> transformed for
  // ~300ms during open, which on heavy pages stalls the main thread *before*
  // any data fetch the consumer kicks off in response to opening — so the
  // network panel shows the request appearing only after the scale finishes.
  // Default to enabled only for bottom sheets; callers can still override.
  const resolvedScale = shouldScaleBackground ?? direction === 'bottom';

  const hasSnapPoints = Boolean(props.snapPoints?.length);
  const rootValue = React.useMemo(
    () => ({ direction, hasSnapPoints }),
    [direction, hasSnapPoints]
  );

  // Dim and blur the page from the FIRST snap point, not the last.
  //
  // vaul hides the overlay entirely below `fadeFromIndex`, which defaults to
  // the last snap point — so a sheet resting at 0.5 sat over a page that was
  // neither dimmed nor blurred (`opacity: 0` on the overlay, while its own
  // `backdrop-filter: blur(5px)` and 60% scrim were already correct and simply
  // never visible). That reads as a panel floating over live content rather
  // than a sheet in front of it. A caller that wants the page to stay legible
  // until the sheet is expanded can still pass its own index.
  // vaul types `fadeFromIndex` as a discriminated union against `snapPoints`
  // (`number` with them, `never` without), which no spread can satisfy
  // conditionally — hence one assembled object and a single cast at the seam.
  const rootProps = {
    ...props,
    ...(hasSnapPoints &&
    (props as { fadeFromIndex?: number }).fadeFromIndex === undefined
      ? { fadeFromIndex: 0 }
      : null),
  } as React.ComponentProps<typeof DrawerPrimitive.Root>;

  return (
    <DrawerRootContext.Provider value={rootValue}>
      <DrawerPrimitive.Root
        shouldScaleBackground={resolvedScale}
        direction={direction}
        {...rootProps}
      />
    </DrawerRootContext.Provider>
  );
};
Drawer.displayName = "Drawer"

const DrawerTrigger = DrawerPrimitive.Trigger

const DrawerPortal = DrawerPrimitive.Portal

const DrawerClose = DrawerPrimitive.Close

const DrawerOverlay = React.forwardRef<
  React.ElementRef<typeof DrawerPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DrawerPrimitive.Overlay>
>(({ className, style, ...props }, ref) => (
  <DrawerPrimitive.Overlay
    ref={ref}
    className={cn("fixed inset-0 z-500 bg-overlay transition-opacity duration-200", className)}
    style={style}
    {...props}
  />
))
DrawerOverlay.displayName = DrawerPrimitive.Overlay.displayName

/** Drawer size preset. Maps to width for left/right, height for top/bottom. */
export type DrawerSize = 'sm' | 'md' | 'lg' | 'xl' | 'full'

const horizontalSizePresets: Record<DrawerSize, string> = {
  sm: 'min(100vw, 360px)',
  md: 'min(100vw, 480px)',
  lg: 'min(100vw, 640px)',
  xl: 'min(100vw, 800px)',
  full: '100vw',
};

const verticalSizePresets: Record<DrawerSize, string> = {
  sm: 'min(var(--app-height, 100dvh), 240px)',
  md: 'min(var(--app-height, 100dvh), 360px)',
  lg: 'min(var(--app-height, 100dvh), 480px)',
  xl: 'min(var(--app-height, 100dvh), 640px)',
  full: 'var(--app-height, 100dvh)',
};

// Numeric fallbacks used as initial size when resize starts and the
// user has not provided an explicit width/height. We can't read the
// CSS `min(100vw, …px)` value reliably before the first paint, so we
// take the px portion as a baseline.
const horizontalSizePx: Record<DrawerSize, number> = {
  sm: 360,
  md: 480,
  lg: 640,
  xl: 800,
  full: 1200,
};

const verticalSizePx: Record<DrawerSize, number> = {
  sm: 240,
  md: 360,
  lg: 480,
  xl: 640,
  full: 900,
};

const directionStyles = {
  // `max-h-[85dvh]` belongs to the panel, not to a caller: with `height:auto`
  // a tall panel would otherwise run off the top of a phone. A caller's own
  // `max-h` cannot do this job — as a flex column the panel FILLS it, so the
  // cap becomes a fixed height around short content.
  bottom: "inset-x-0 bottom-0 mt-24 max-h-[min(85dvh,calc(var(--app-height,100dvh)-var(--safe-top,0px)-1rem))] rounded-t-lg border-t",
  top: "inset-x-0 top-0 mb-24 rounded-b-lg border-b",
  right: "inset-y-0 right-0 h-auto border-l",
  left: "inset-y-0 left-0 h-auto border-r",
} as const;

// The snap-point variant of the above. A snapped panel is FULL height and vaul
// slides it to the active point by transform, so the `max-h` and the top margin
// that keep an auto-height sheet on screen are exactly wrong here: they shorten
// the panel while vaul keeps translating by the full distance, and the sheet
// lands past the bottom edge. Height comes from the height:100% below, never
// from a preset.
const snapDirectionStyles = {
  bottom: "inset-x-0 bottom-0 h-full rounded-t-lg border-t",
  top: "inset-x-0 top-0 h-full rounded-b-lg border-b",
  right: "inset-y-0 right-0 h-full border-l",
  left: "inset-y-0 left-0 h-full border-r",
} as const;

const toCssLength = (value: string | number | undefined): string | undefined => {
  if (value == null) return undefined;
  return typeof value === 'number' ? `${value}px` : value;
};

const parseInitialPx = (value: string | number | undefined, fallback: number): number => {
  if (typeof value === 'number') return value;
  if (typeof value === 'string') {
    const match = value.match(/(-?\d+(?:\.\d+)?)/);
    if (match) return Number(match[1]);
  }
  return fallback;
};

const clamp = (value: number, min: number, max: number) =>
  Math.min(Math.max(value, min), max);

export interface DrawerContentProps
  extends React.ComponentPropsWithoutRef<typeof DrawerPrimitive.Content> {
  direction?: 'bottom' | 'right' | 'left' | 'top';
  /** Preset size (default `'md'`). Width for horizontal, height for vertical. */
  size?: DrawerSize;
  /** CSS length for width — applies to left/right drawers. Overrides `size`. */
  width?: string | number;
  /** CSS length for height — applies to top/bottom drawers. Overrides `size`. */
  height?: string | number;
  /**
   * Render children directly, with no grab handle and no padded scroll wrapper. For app-shell surfaces
   * (the sidebar drawer) that lay out their own header / scrolling body / footer inside the panel.
   */
  bare?: boolean;
  /** Allow user to resize the drawer by dragging its inner edge. */
  resizable?: boolean;
  /** Disable resize on mobile viewports (< 768px). Default `true`. */
  resizableOnDesktopOnly?: boolean;
  /** Min size in px when `resizable`. Width for horizontal, height for vertical. */
  minSize?: number;
  /** Max size in px when `resizable`. Width for horizontal, height for vertical. */
  maxSize?: number;
  /**
   * Controlled current size in px. Pair with `onSizeChange` for external
   * persistence (see `useDrawerSize` hook). When `undefined`, the drawer
   * is uncontrolled and size lives in local state.
   */
  resizedSize?: number;
  /** Called once on pointer-up with the final resized size in px. */
  onSizeChange?: (size: number) => void;
}

const DrawerContent = React.forwardRef<
  React.ElementRef<typeof DrawerPrimitive.Content>,
  DrawerContentProps
>(({
  className,
  children,
  direction: directionProp,
  size = 'md',
  bare = false,
  width,
  height,
  style,
  resizable = false,
  resizableOnDesktopOnly = true,
  minSize,
  maxSize,
  resizedSize,
  onSizeChange,
  ...props
}, ref) => {
  // Inherit direction from the Drawer Root when not explicitly overridden.
  // This avoids the common bug where `<Drawer direction="right">` is paired
  // with a `<DrawerContent />` that silently falls back to "bottom".
  const inherited = useDrawerDirection();
  const direction = directionProp ?? inherited ?? 'bottom';
  const isVertical = direction === 'bottom' || direction === 'top';
  const isMobile = useIsMobile();
  const resizeEnabled = resizable && (!resizableOnDesktopOnly || !isMobile);
  const hasSnapPoints = useDrawerHasSnapPoints();

  const defaultMin = isVertical ? 200 : 280;
  const defaultMax = isVertical ? 800 : 960;
  const minPx = minSize ?? defaultMin;
  const maxPx = maxSize ?? defaultMax;

  const presetPx = isVertical
    ? parseInitialPx(height, verticalSizePx[size])
    : parseInitialPx(width, horizontalSizePx[size]);

  // Uncontrolled: track size locally. Controlled: caller owns it via `resizedSize`.
  const isControlled = resizedSize !== undefined;
  const [internalPx, setInternalPx] = React.useState<number | null>(null);
  const currentPx = isControlled ? clamp(resizedSize!, minPx, maxPx) : internalPx;

  // Reset uncontrolled state if direction or enabled flag flips, so we
  // don't carry a horizontal width into a vertical drawer.
  React.useEffect(() => {
    if (!isControlled) setInternalPx(null);
  }, [direction, resizeEnabled, isControlled]);

  const dragStateRef = React.useRef<{
    startCoord: number;
    startSize: number;
    lastSize: number;
  } | null>(null);

  const handlePointerDown = React.useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    if (!resizeEnabled) return;
    e.preventDefault();
    e.stopPropagation();
    (e.currentTarget as HTMLElement).setPointerCapture?.(e.pointerId);
    const startSize = currentPx ?? presetPx;
    dragStateRef.current = {
      startCoord: isVertical ? e.clientY : e.clientX,
      startSize,
      lastSize: startSize,
    };
  }, [resizeEnabled, isVertical, currentPx, presetPx]);

  const handlePointerMove = React.useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    const drag = dragStateRef.current;
    if (!drag) return;
    e.preventDefault();
    const current = isVertical ? e.clientY : e.clientX;
    const delta = current - drag.startCoord;
    const sign = direction === 'right' || direction === 'bottom' ? -1 : 1;
    const next = clamp(drag.startSize + sign * delta, minPx, maxPx);
    drag.lastSize = next;
    if (!isControlled) setInternalPx(next);
    // Note: onSizeChange fires on pointer-up only — avoids hammering
    // localStorage / external stores during drag. For live feedback
    // during drag, render from `currentPx` (uncontrolled) or from your
    // own state synced separately.
  }, [direction, isVertical, minPx, maxPx, isControlled]);

  const handlePointerUp = React.useCallback((e: React.PointerEvent<HTMLDivElement>) => {
    const drag = dragStateRef.current;
    if (!drag) return;
    (e.currentTarget as HTMLElement).releasePointerCapture?.(e.pointerId);
    dragStateRef.current = null;
    onSizeChange?.(drag.lastSize);
  }, [onSizeChange]);

  // Viewport clamp — keeps the drawer inside the window on narrow screens.
  // Without this, a fixed `width: 720px` on a 600px-wide window paints the
  // drawer 120px past the right edge (off-screen for `direction="right"`).
  // Applied to BOTH the resized px value and the initial preset so user-
  // dragged widths can't overflow either. CSS `min()` is cheap and the
  // browser re-evaluates on every viewport change, so window resize works
  // for free.
  const rawWidth = !isVertical
    ? (currentPx != null ? `${currentPx}px` : (toCssLength(width) ?? horizontalSizePresets[size]))
    : undefined;
  // With snap points the PANEL is full-height and vaul positions it by
  // transform, reading back how far it may travel. A height of our own makes
  // the two disagree: at snap point 0.4 vaul translated a 360px panel by 532px
  // and pushed it entirely off the bottom of the screen — the drawer opened
  // into nothing. So when the Root has snap points, the height is vaul's.
  const rawHeight = isVertical && !hasSnapPoints
    ? (currentPx != null ? `${currentPx}px` : (toCssLength(height) ?? verticalSizePresets[size]))
    : undefined;
  const resolvedWidth = rawWidth ? `min(100vw, ${rawWidth})` : undefined;
  const resolvedHeight = rawHeight ? `min(var(--app-height, 100dvh), ${rawHeight})` : undefined;

  const handlePosition: Record<typeof direction, string> = {
    right: 'left-0 top-0 h-full w-1.5 -translate-x-1/2 cursor-ew-resize',
    left: 'right-0 top-0 h-full w-1.5 translate-x-1/2 cursor-ew-resize',
    bottom: 'top-0 left-0 w-full h-1.5 -translate-y-1/2 cursor-ns-resize',
    top: 'bottom-0 left-0 w-full h-1.5 translate-y-1/2 cursor-ns-resize',
  };

  return (
    <DrawerPortal>
      <DrawerOverlay />
      <DrawerPrimitive.Content
        ref={ref}
        aria-describedby={undefined}
        className={cn(
          "fixed z-500 flex flex-col bg-background",
          hasSnapPoints ? snapDirectionStyles[direction] : directionStyles[direction],
          className
        )}
        style={{
          // With snap points vaul drives `transform` AND the transition that
          // animates it, writing both to this element imperatively. A
          // `transition` of ours in the style object is re-applied by React on
          // every render and wipes that inline `transform` with it, so the
          // sheet stays parked at its closed offset: measured
          // `--snap-point-height: 415.5px` (correct) against `transform:
          // translate3d(0, 831px, 0)` (fully off-screen). The resize handle's
          // own animation is what this exists for, and resize does not apply
          // to a snapped sheet.
          ...(hasSnapPoints
            ? null
            : {
                transition: dragStateRef.current
                  ? 'none'
                  : 'transform 300ms cubic-bezier(0.32, 0.72, 0, 1)',
              }),
          ...(resolvedWidth ? { width: resolvedWidth } : {}),
          ...(resolvedHeight ? { height: resolvedHeight } : {}),
          ...style,
        }}
        {...props}
      >
        {resizeEnabled && (
          <div
            role="separator"
            aria-orientation={isVertical ? 'horizontal' : 'vertical'}
            onPointerDown={handlePointerDown}
            onPointerMove={handlePointerMove}
            onPointerUp={handlePointerUp}
            onPointerCancel={handlePointerUp}
            className={cn(
              "absolute z-10 select-none touch-none bg-transparent hover:bg-border/60 transition-colors",
              handlePosition[direction]
            )}
          />
        )}
        {/* Everything the reader can see lives inside this column when the
            sheet is snapped: the panel itself extends past the bottom of the
            window, so a footer pinned to the PANEL is pinned off-screen.
            `.drawer-snap-viewport` is the visible slice; without snap points
            there is no slice to take and the panel is the column. */}
        <div className={hasSnapPoints ? "drawer-snap-viewport" : "contents"}>
        {/* The grab handle. `bg-muted` is a SURFACE token — on a light theme it
            is nearly the panel's own colour, so the handle read as a smudge.
            `bg-border` is the token for a line drawn ON a surface and is the
            one that keeps its contrast in both themes. Slimmer and narrower
            than before, which is what the platform sheets use: the handle is an
            affordance, not an element of the design.
            `aria-hidden` because the drag it hints at is not a keyboard
            affordance — Escape and the close button are. */}
        {isVertical && !bare && (
          <div
            aria-hidden
            className="mx-auto mt-3 h-1.5 w-10 shrink-0 rounded-full bg-border"
          />
        )}
        {/*
          Content padding lives HERE, not on each caller. `DialogContent` has
          its own; this did not, so every surface that renders as a Dialog on
          desktop and a Drawer on a phone lost its inset at the breakpoint —
          section headings and values sat flush against the panel edge and read
          as clipped. A default each caller must remember is a default nobody
          applies.

          The bottom inset is larger than the sides on purpose: it is what tells
          a reader whether the list has ended or continues under the edge, and
          on a phone it also clears the home indicator.

          It owns the SCROLL but never the height: `flex-1` here filled the
          panel and left the last row hundreds of pixels above the edge. Only
          the panel's own `max-h` decides how tall the drawer gets.

          With snap points that reasoning inverts. The panel is full-height by
          then and vaul slides it, so a scroller sized to its content would
          leave the rest of the sheet empty and unscrollable — there `flex-1`
          is what makes the body fill the snapped height.
        */}
        {bare ? children : (
        <div
          className={cn(
            "min-h-0 overflow-y-auto overscroll-contain px-5 pb-[max(1.25rem,var(--safe-bottom,env(safe-area-inset-bottom,0px)))]",
            hasSnapPoints && "flex-1"
          )}
        >
          {children}
        </div>
        )}
        </div>
      </DrawerPrimitive.Content>
    </DrawerPortal>
  );
})
DrawerContent.displayName = "DrawerContent"

const DrawerHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("grid gap-1.5 p-4 text-center sm:text-left", className)}
    {...props}
  />
)
DrawerHeader.displayName = "DrawerHeader"

const DrawerFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn("mt-auto flex flex-col gap-2 p-4", className)}
    {...props}
  />
)
DrawerFooter.displayName = "DrawerFooter"

const DrawerTitle = React.forwardRef<
  React.ElementRef<typeof DrawerPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DrawerPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DrawerPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DrawerTitle.displayName = DrawerPrimitive.Title.displayName

const DrawerDescription = React.forwardRef<
  React.ElementRef<typeof DrawerPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DrawerPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DrawerPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DrawerDescription.displayName = DrawerPrimitive.Description.displayName

export {
  Drawer,
  DrawerPortal,
  DrawerOverlay,
  DrawerTrigger,
  DrawerClose,
  DrawerContent,
  DrawerHeader,
  DrawerFooter,
  DrawerTitle,
  DrawerDescription,
}

export { useDrawerSize } from './useDrawerSize';
export type { UseDrawerSizeOptions, UseDrawerSizeResult } from './useDrawerSize';
