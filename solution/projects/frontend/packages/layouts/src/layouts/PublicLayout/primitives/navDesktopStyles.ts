import { cn } from '@djangocfg/ui-core/lib';

// Corners come from ui-core's radius tokens, never raw Tailwind steps —
// presets (`dense`, `windows`) retune those variables, and a hardcoded
// `rounded-lg` would opt this navbar out of the active theme.
//
// Radius is chosen per element KIND, not unified across the bar: nav rows and
// menu items take `rounded-control` (--radius-control, the token documented for
// "nav items, inputs, chips"), their popover takes --radius-popover, while
// BUTTONS stay pills like every other button in the product. Making the rows
// pills too is what produced capsules floating inside a soft-cornered popover.
export const navItemCls = cn(
  'inline-flex min-h-9 pointer-coarse:min-h-11 items-center justify-center gap-1 rounded-control border border-transparent px-4 py-1.5 text-sm !font-medium',
  'ring-0 focus-visible:ring-0',
  'text-foreground/90 transition-colors',
  'surface-hover hover:text-foreground',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/35',
);

export const navItemActiveCls =
  'border-transparent bg-accent text-foreground shadow-sm dark:bg-muted dark:shadow-none';

export const labelCls = 'min-w-0 max-w-[11rem] truncate sm:max-w-[13rem]';

export function subMenuLinkCls(active: boolean) {
  return cn(
    'flex min-h-9 pointer-coarse:min-h-11 min-w-0 max-w-[min(17rem,calc(100vw-5rem))] items-center rounded-control border-0 px-3 py-2 text-sm font-medium transition-colors',
    'surface-hover',
    active
      ? 'border-0 bg-accent font-semibold text-foreground shadow-sm dark:bg-muted/90 dark:shadow-none'
      : 'border-0 text-foreground/90',
  );
}

// Real glass: low-opacity surface so the blur actually shows the page behind
// it. The package-level nav-dropdown-glass utility keeps the frosted effect
// present even when the consuming app does not scan layout sources.
export const popoverCls =
  'absolute left-0 top-full mt-1 z-[1200] min-w-[14.5rem] rounded-[var(--radius-popover)] border border-border/70 nav-dropdown-glass p-1.5 shadow-[0_1px_2px_rgba(0,0,0,0.05),0_8px_28px_rgba(0,0,0,0.18)] dark:shadow-[0_8px_30px_rgba(0,0,0,0.45)]';

export const portalPopoverCls =
  'fixed z-[1200] min-w-[14.5rem] rounded-[var(--radius-popover)] border border-border/70 nav-dropdown-glass backdrop-blur-[5px] backdrop-saturate-150 p-1.5 shadow-[0_1px_2px_rgba(0,0,0,0.05),0_8px_28px_rgba(0,0,0,0.18)] dark:shadow-[0_8px_30px_rgba(0,0,0,0.45)]';
