'use client';

/**
 * Shared popover triggers for the date/time fields, so the two large click
 * targets (leading icon + trailing chevron) look and behave identically across
 * all three fields. Both are `PopoverTrigger asChild` children, so the shell's
 * `focus-within` ring covers them.
 *
 * Why two targets: the CENTRE of the field is the native `<input>` (for typing),
 * so the popover can't open from there without stealing keyboard entry. The
 * icon and the chevron are the two edges that DON'T type, so both open the
 * picker — the icon in particular is a big, obvious left-edge target, far easier
 * to hit than a lone chevron.
 */

import { ChevronDown } from 'lucide-react';
import * as React from 'react';

import { cn } from '../../../lib/utils';

export const PopoverChevron = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }
>(({ className, label = 'Open picker', ...props }, ref) => (
  <button
    ref={ref}
    type="button"
    aria-label={label}
    className={cn(
      'flex size-6 shrink-0 items-center justify-center rounded-[var(--radius-sm)] text-muted-foreground',
      'transition-colors hover:bg-accent hover:text-foreground',
      'focus-visible:outline-none disabled:pointer-events-none',
      className,
    )}
    {...props}
  >
    <ChevronDown className="size-4" aria-hidden />
  </button>
));
PopoverChevron.displayName = 'PopoverChevron';

/**
 * IconTrigger — the leading icon rendered as a real, comfortably-sized popover
 * button. It hugs the left edge (`-ml-1` reclaims the shell's px-3) and carries
 * a generous padded hit area so the target is far bigger than the glyph itself.
 */
export const IconTrigger = React.forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement> & { label?: string }
>(({ className, label = 'Open picker', children, ...props }, ref) => (
  <button
    ref={ref}
    type="button"
    aria-label={label}
    className={cn(
      '-ml-1 flex h-8 shrink-0 items-center rounded-[var(--radius-sm)] px-1.5 text-muted-foreground',
      'transition-colors hover:bg-accent hover:text-foreground',
      'focus-visible:outline-none disabled:pointer-events-none [&_svg]:size-4',
      className,
    )}
    {...props}
  >
    {children}
  </button>
));
IconTrigger.displayName = 'IconTrigger';
