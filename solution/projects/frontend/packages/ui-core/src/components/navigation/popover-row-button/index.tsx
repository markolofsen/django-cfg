"use client"

import { Check } from 'lucide-react';
import * as React from 'react';

import { cn } from '../../../lib/utils';

/**
 * PopoverRowButton — a selectable list-row button, macOS picker style:
 *
 *   [ ✓ ] label…
 *
 * The canonical row for model / machine / provider pickers: full-width, left
 * aligned, with a trailing-leading check that fades in on `selected`. Replaces
 * the hand-rolled `<button className={cn("flex w-full items-center gap-2 px-3
 * py-1.5 …", active && "bg-muted/60")}>` copied across pickers.
 *
 * Plain `<button>` underneath — extend it with any native button prop. The
 * incoming `className` is merged last so callers can compose freely.
 */
export interface PopoverRowButtonProps
  extends React.ComponentProps<"button"> {
  /** Marks the row active — fills the background and shows the check. */
  selected?: boolean;
}

const PopoverRowButton = React.forwardRef<HTMLButtonElement, PopoverRowButtonProps>(
  ({ className, selected = false, type = "button", children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        type={type}
        className={cn(
          "flex w-full items-center gap-2 px-3 py-1.5 text-left text-xs",
          "hover:bg-muted disabled:cursor-not-allowed disabled:opacity-40",
          selected && "bg-muted/60",
          className,
        )}
        {...props}
      >
        <Check
          className={cn(
            "h-3.5 w-3.5 shrink-0 text-primary",
            selected ? "opacity-100" : "opacity-0",
          )}
        />
        {children}
      </button>
    );
  },
);
PopoverRowButton.displayName = "PopoverRowButton";

export { PopoverRowButton };
