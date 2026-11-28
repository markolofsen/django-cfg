import type { ReactNode } from "react";

import { cn } from "@djangocfg/ui-core/lib";
import { TooltipHint } from "@djangocfg/ui-core";

export interface JumpToLatestProps {
  readonly onClick: () => void;
  /** Accessible name. The button is icon-only, so nothing else names it. */
  readonly label: string;
  /**
   * Replies that arrived since the reader left, or null when there is nothing
   * honest to show. Null renders no badge — an empty one claims a count.
   */
  readonly missed?: number | null;
  readonly icon: ReactNode;
  readonly className?: string;
}

/**
 * The return-to-bottom control.
 *
 * An overlay, unlike the message toolbar: it belongs to the viewport rather
 * than to any message, so it must not sit in the transcript's flow and scroll
 * away with the content it is offering to leave.
 *
 * Rendering is gated by `Transcript`, which shows this only while unpinned —
 * this component must not decide its own visibility, or two owners would
 * disagree about where the viewport is.
 */
export function JumpToLatest({ onClick, label, missed, icon, className }: JumpToLatestProps) {
  const hasBadge = missed !== null && missed !== undefined && missed > 0;
  // A pill when it carries a count, a disc when it does not — the shape says
  // whether there is something to come back TO before the number is read.
  const shape = hasBadge ? "h-8 ps-2 pe-3" : "size-8 justify-center";
  const count = hasBadge ? (
    <span className="text-xs font-medium tabular-nums">{missed}</span>
  ) : null;
  const classes = cn(
    // Anchored to the zero-height strip Transcript places at the scroller's
    // lower edge, so it floats just above the last message and clear of the
    // composer below.
    "absolute bottom-2 left-1/2 z-20 -translate-x-1/2",
    "inline-flex items-center gap-1.5 rounded-full",
    // Blurred backdrop rather than an opaque fill: the control sits over live
    // text, and a solid disc reads as a hole punched in the reply.
    "bg-background/70 shadow-md backdrop-blur-md",
    "border border-border",
    shape,
    "text-muted-foreground transition-colors",
    "hover:bg-secondary hover:text-foreground",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
    className,
  );

  return (
    <TooltipHint tooltip={label}>
      <button type="button" onClick={onClick} aria-label={label} className={classes}>
        {icon}
        {count}
      </button>
    </TooltipHint>
  );
}
