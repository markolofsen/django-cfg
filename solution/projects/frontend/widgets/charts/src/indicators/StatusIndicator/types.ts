// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

/**
 * Operational status of a service or component.
 *
 * Each value maps to a semantic tone defined in {@link STATUS_TONE}. Custom
 * statuses can be passed by extending {@link STATUS_TONE} at the call site
 * (see `<StatusIndicator tone="..." />` escape hatch).
 */
export type Status =
  | 'operational'
  | 'degraded'
  | 'partial-outage'
  | 'major-outage'
  | 'maintenance'
  | 'incident'
  | 'unknown';

/**
 * Semantic tone used to colorize the dot and label.
 *
 * Maps 1:1 to status-surface tokens in `ui-core/styles` (success / warning /
 * destructive / info / muted). Themes / presets override these tokens —
 * never reference raw scales like `emerald-500`.
 */
export type StatusTone = 'success' | 'warning' | 'destructive' | 'info' | 'muted';

/**
 * Default Status → tone + label mapping. Override per-instance via the
 * `tone` and `label` props.
 */
export const STATUS_CONFIG: Record<Status, { label: string; tone: StatusTone }> = {
  operational: { label: 'Operational', tone: 'success' },
  degraded: { label: 'Degraded', tone: 'warning' },
  'partial-outage': { label: 'Partial Outage', tone: 'warning' },
  'major-outage': { label: 'Major Outage', tone: 'destructive' },
  maintenance: { label: 'Maintenance', tone: 'info' },
  incident: { label: 'Incident', tone: 'destructive' },
  unknown: { label: 'Unknown', tone: 'muted' },
};

/**
 * Tailwind classes per tone. All classes resolve to semantic tokens; no raw
 * color scales.
 *
 * The whole pill (background) uses the status-surface `bg-*-background`
 * token paired with the readable `text-*-foreground` token — that pair
 * is the one `ui-core/styles` specifically tunes for banner/pill use
 * (low-saturation surface + dark accent text). Stacking a red-on-pale-red
 * label over a `bg-card` pill, as the previous version did, dropped
 * contrast under 3:1 on light theme.
 *
 * The dot stays at the saturated accent color (`bg-*`) so it visually
 * pops against the muted surface.
 *
 * `destructive` has no `--destructive-foreground` tuned for surface use
 * (the existing token is the white-on-red filled-button text), so we use
 * the accent color itself — dark red on the pale-red surface still meets
 * AA contrast in both light and dark themes.
 */
export const TONE_CLASSES: Record<
  StatusTone,
  { dot: string; text: string; pill: string }
> = {
  success: {
    dot: 'bg-success',
    text: 'text-success-foreground',
    pill: 'bg-success-background',
  },
  warning: {
    dot: 'bg-warning',
    text: 'text-warning-foreground',
    pill: 'bg-warning-background',
  },
  destructive: {
    dot: 'bg-destructive',
    text: 'text-destructive',
    pill: 'bg-destructive-background',
  },
  info: {
    dot: 'bg-info',
    text: 'text-info-foreground',
    pill: 'bg-info-background',
  },
  muted: {
    dot: 'bg-muted-foreground/60',
    text: 'text-muted-foreground',
    pill: 'bg-muted',
  },
};

export const statusIndicatorVariants = cva(
  'inline-flex items-center gap-2 rounded-full border font-medium',
  {
    variants: {
      size: {
        sm: 'h-6 px-2.5 text-[11px] [&>[data-slot=status-dot]]:size-1.5',
        md: 'h-7 px-3 text-xs [&>[data-slot=status-dot]]:size-2',
        lg: 'h-8 px-3.5 text-sm [&>[data-slot=status-dot]]:size-2.5',
      },
    },
    defaultVariants: {
      size: 'md',
    },
  },
);

export type StatusIndicatorSize = NonNullable<
  VariantProps<typeof statusIndicatorVariants>['size']
>;

export interface StatusIndicatorProps
  extends Omit<React.ComponentProps<'span'>, 'children'>,
    VariantProps<typeof statusIndicatorVariants> {
  /** Current operational status. */
  status: Status;
  /** Custom label text. Auto-generated from status when omitted. */
  label?: string;
  /**
   * Override the tone (semantic color) used for dot + label. Defaults to
   * {@link STATUS_CONFIG}`[status].tone`.
   */
  tone?: StatusTone;
  /**
   * Enable the pulsing halo around the dot. Defaults to `true` for live
   * statuses (`incident`, `major-outage`, `partial-outage`, `degraded`)
   * and `false` for steady states.
   */
  pulse?: boolean;
}
