"use client"

import * as React from 'react';

import { cn } from '../../../lib/utils';

/**
 * PopoverActionButton — the full-width icon+label list/footer row, macOS style:
 *
 *   [ icon ] label…
 *
 * The canonical "jump to settings" / footer-link control inside popovers and
 * menus (e.g. "Connection settings…", "Manage providers…"). Replaces the
 * hand-rolled `<button className="flex w-full items-center gap-2 rounded px-2
 * py-1.5 …">` that was copied across popover footers.
 *
 * Plain `<button>` underneath — extend it with any native button prop. The
 * incoming `className` is merged last, so callers can still add layout tweaks
 * (`mt-1`, etc.) without re-stating the base styling.
 */
export interface PopoverActionButtonProps
  extends React.ComponentProps<"button"> {
  /** Icon rendered before the label, in a fixed `h-3.5 w-3.5` slot. */
  icon?: React.ReactNode;
}

const PopoverActionButton = React.forwardRef<HTMLButtonElement, PopoverActionButtonProps>(
  ({ className, icon, type = "button", children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        type={type}
        className={cn(
          "flex w-full items-center gap-2 rounded-[var(--radius-sm)] px-2 py-1.5 text-left text-xs text-muted-foreground hover:bg-muted hover:text-foreground",
          className,
        )}
        {...props}
      >
        {icon != null && <span className="h-3.5 w-3.5 shrink-0">{icon}</span>}
        {children}
      </button>
    );
  },
);
PopoverActionButton.displayName = "PopoverActionButton";

export { PopoverActionButton };
