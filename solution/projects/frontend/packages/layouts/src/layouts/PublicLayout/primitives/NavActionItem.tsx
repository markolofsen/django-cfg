/**
 * NavAction — shared CTA primitive used by every PublicLayout navbar.
 *
 * Previously lived on MinimalNavbar only. Promoted so Floating/Flush can accept
 * the same typed CTA pills (Book a demo / Get started …) without a fork.
 */

'use client';

import React, { type ReactNode } from 'react';

import { Link } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

export interface NavAction {
  label: string;
  href: string;
  /** Open in a new tab. @default false */
  external?: boolean;
  /**
   * Visual style.
   * - `link`    — plain text link
   * - `ghost`   — transparent pill, fills on hover (default)
   * - `outline` — bordered pill
   * - `secondary` — solid neutral pill (a real action, not the main CTA)
   * - `primary` — solid high-contrast pill (main CTA)
   * @default 'ghost'
   */
  variant?: 'link' | 'ghost' | 'outline' | 'secondary' | 'primary';
  /** Hide on screens below lg (useful for secondary CTAs). @default false */
  hideOnSmall?: boolean;
  /** Optional inline icon (use lucide-react or any ReactNode). */
  icon?: ReactNode;
  /** Custom click handler (still navigates via href unless preventDefault'd). */
  onClick?: (event: React.MouseEvent<HTMLAnchorElement>) => void;
}

const baseCls =
  'inline-flex shrink-0 items-center justify-center gap-1.5 rounded-full text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/35';

// Height is FIXED (`h-9`), not a `min-h-9` floor. With a minimum the pill grew
// past its neighbours as soon as it carried an icon — the navbar's own UserMenu
// login button is a ui-core `Button size="sm"` (a fixed `h-8`), so a growing CTA
// sat visibly taller than the control right next to it. A nav action is a
// control in a row of controls: its height must be a constant, and the label is
// already truncated rather than wrapped.
const variantCls: Record<NonNullable<NavAction['variant']>, string> = {
  link:
    'px-1.5 py-1 text-foreground/85 hover:text-foreground',
  ghost:
    'h-9 px-4 text-foreground/90 hover:bg-accent/55 hover:text-foreground',
  outline:
    'h-9 px-4 border border-border/70 text-foreground/90 hover:bg-accent/40 hover:text-foreground',
  // Filled but neutral — the middle rung between `outline` (which disappears
  // into a dark navbar) and `primary` (which competes with the one real CTA).
  // Uses the `secondary` token pair rather than a hand-mixed tint so it retunes
  // with the active preset.
  secondary:
    'h-9 px-4 bg-secondary text-secondary-foreground hover:bg-secondary/80 shadow-sm',
  primary:
    'h-9 px-4 bg-primary text-primary-foreground hover:bg-primary/90 shadow-sm',
};

interface NavActionItemProps {
  action: NavAction;
  className?: string;
}

export function NavActionItem({ action, className }: NavActionItemProps) {
  const variant = action.variant ?? 'ghost';
  const cls = cn(
    baseCls,
    variantCls[variant],
    action.hideOnSmall && 'hidden lg:inline-flex',
    className,
  );

  const content = (
    <>
      {action.icon && (
        <span className="inline-flex size-3.5 shrink-0 items-center justify-center" aria-hidden>
          {action.icon}
        </span>
      )}
      <span className="truncate">{action.label}</span>
    </>
  );

  if (action.external) {
    return (
      <a
        href={action.href}
        target="_blank"
        rel="noopener noreferrer"
        className={cls}
        onClick={action.onClick}
      >
        {content}
      </a>
    );
  }
  return (
    <Link href={action.href} className={cls} onClick={action.onClick}>
      {content}
    </Link>
  );
}
