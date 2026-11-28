"use client"

/**
 * Disclosure — a light "line in the flow" that expands.
 *
 *   [icon] label ·································· [fact]  [chevron]
 *   └────────────── whole row is the expand target (one <button>) ──────────────┘
 *   [ body — rendered only when open, indented, NO card frame ]
 *
 * The gap `SettingsBlock` leaves open. `SettingsBlock` renders a section HEADING
 * (`uppercase font-semibold` title) plus its summary/body as a **sibling `<div>`
 * under the header** — so a collapsed block is always ≥2 full-width rows and
 * reads with the weight of a section. That is correct for a settings surface and
 * wrong for a feed of short items (chat tool-call cards): there, a collapsed item
 * should be ONE line that reads as a list row, not a heading.
 *
 * `Disclosure` is that one-line disclosure:
 *  - collapsed = exactly one row (`label` + right-aligned `fact` on the SAME line);
 *  - `tone` names the weight ('row' = list line, default; 'section' = heading) —
 *    weight is derived from intent, never a density preference/toggle;
 *  - the leading `icon` is a fixed `size-4` slot, so a spinner→dot swap
 *    (running→done) causes no reflow, and `open` only mounts the body below —
 *    the header height is stable across running → done → open;
 *  - `open` is controllable, so a host can pin a failed item open forever while
 *    it still reads as a light, frameless line.
 *
 * Additive: `SettingsBlock` / `SettingRow` are unchanged. See
 * `packages/@dev/active/disclosure-row-primitive/`.
 */

import { ChevronDown } from 'lucide-react';
import * as React from 'react';

import { cn } from '../../../lib/utils';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '../collapsible';

export type DisclosureTone = 'row' | 'section';
export type DisclosureSize = 'sm' | 'default';

export interface DisclosureProps {
  /** Fixed-size leading slot (spinner / status dot / glyph). Rendered in a size-4 box. */
  icon?: React.ReactNode;
  /** Primary label on the header line (e.g. a tool name). */
  label: React.ReactNode;
  /** Right-aligned summary on the SAME header line. Absent → the row stays one line. */
  fact?: React.ReactNode;
  /** Weight. 'row' = light list line (default). 'section' = heading weight. */
  tone?: DisclosureTone;
  /** Density. 'sm' (default) matches a transcript; 'default' is roomier. */
  size?: DisclosureSize;
  /** Controlled open. Host pins failures open (never auto-collapse a failure). */
  open?: boolean;
  /** Uncontrolled initial open. Ignored when `open` is provided. */
  defaultOpen?: boolean;
  onOpenChange?: (open: boolean) => void;
  /** Disable the trigger — e.g. a body-less running row that shouldn't invite a click. */
  disabled?: boolean;
  /** Body, mounted only while open. */
  children?: React.ReactNode;
  /** Extra classes on the root. */
  className?: string;
  /** Extra classes on the header button. */
  headerClassName?: string;
}

const HEADER_BASE =
  'group flex w-full items-center gap-2 text-left transition-colors ' +
  'hover:bg-muted/60 disabled:cursor-default disabled:opacity-60 ' +
  'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring';

const SIZE_HEADER: Record<DisclosureSize, string> = {
  sm: 'px-2.5 py-1.5 text-xs',
  default: 'px-3 py-2 text-sm',
};

const SIZE_BODY: Record<DisclosureSize, string> = {
  sm: 'px-2.5 pb-1.5 text-[11px]',
  default: 'px-3 pb-2 text-xs',
};

// 'row' reads as a line in the flow; 'section' reproduces SettingsBlock's
// BLOCK_TITLE weight so a caller wanting a heading needn't reach for it.
const TONE_LABEL: Record<DisclosureTone, string> = {
  row: 'min-w-0 truncate text-foreground/90',
  section: 'min-w-0 truncate font-semibold uppercase tracking-wide text-muted-foreground',
};

/**
 * A body that keeps the collapsed row to a single line stays light; the reveal
 * animation classes come from `tailwindcss-animate` and are cosmetic — if a
 * consumer omits that plugin the body still shows/hides, it just snaps. Height
 * stability comes from the fixed header, not the animation.
 */
const BODY_ANIM =
  'overflow-hidden data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down';

export const Disclosure = React.forwardRef<HTMLDivElement, DisclosureProps>(
  (
    {
      icon,
      label,
      fact,
      tone = 'row',
      size = 'sm',
      open,
      defaultOpen,
      onOpenChange,
      disabled = false,
      children,
      className,
      headerClassName,
    },
    ref,
  ) => {
    const hasBody = children != null && children !== false;

    return (
      <Collapsible
        ref={ref}
        open={open}
        defaultOpen={defaultOpen}
        onOpenChange={onOpenChange}
        className={cn('min-w-0', className)}
      >
        <CollapsibleTrigger
          type="button"
          disabled={disabled || !hasBody}
          className={cn(HEADER_BASE, SIZE_HEADER[size], 'rounded-control', headerClassName)}
        >
          {/* Fixed-size leading slot: spinner↔dot swap here never reflows the row. */}
          {icon != null ? (
            <span className="flex size-4 shrink-0 items-center justify-center">{icon}</span>
          ) : null}

          <span className={TONE_LABEL[tone]}>{label}</span>

          {/* Right-aligned fact on the SAME line; absent → collapses, row stays 1 line. */}
          {fact != null ? (
            <span className="ml-auto shrink-0 text-muted-foreground">{fact}</span>
          ) : null}

          {/* Chevron only when there is a body to reveal. Pushed to the end;
              when `fact` is absent `ml-auto` here keeps it right-aligned. */}
          {hasBody ? (
            <ChevronDown
              aria-hidden
              className={cn(
                'size-3.5 shrink-0 opacity-60 transition-transform duration-200',
                'group-data-[state=open]:rotate-180',
                fact == null && 'ml-auto',
              )}
            />
          ) : null}
        </CollapsibleTrigger>

        {hasBody ? (
          <CollapsibleContent className={BODY_ANIM}>
            {/* Indented, frameless body — no card, no border box → stays light
                even when a failed item is pinned open. */}
            <div className={cn('pt-1', SIZE_BODY[size])}>{children}</div>
          </CollapsibleContent>
        ) : null}
      </Collapsible>
    );
  },
);
Disclosure.displayName = 'Disclosure';
