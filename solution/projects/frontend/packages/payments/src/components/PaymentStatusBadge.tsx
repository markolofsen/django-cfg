'use client';

// ============================================================================
// @djangocfg/payments — PaymentStatusBadge
// ============================================================================
// Stripe-like status pill: a colored dot + label on a subtle tinted chip.
// Self-contained (no ui-core Badge) so the dot tone and chip tint stay in sync.

import React from 'react';

import type { PaymentStatus } from '../domain/types';

export interface PaymentStatusBadgeProps {
  status: PaymentStatus;
  /** Optional label override (host supplies translated text). */
  label?: string;
  className?: string;
}

interface StatusStyle {
  /** Tailwind classes for the chip (bg tint + text). */
  chip: string;
  /** Tailwind class for the dot. */
  dot: string;
  defaultLabel: string;
}

// ui-core semantic status tokens (success/warning/info/destructive
// background+foreground pairs) — contrast-tuned per theme, unlike raw
// palette tints which wash out on light backgrounds. Borderless by design:
// tint + toned text carry the state (Stripe-dashboard style).
const STATUS_STYLES: Record<PaymentStatus, StatusStyle> = {
  idle: {
    chip: 'bg-muted text-muted-foreground',
    dot: 'bg-muted-foreground/50',
    defaultLabel: 'Not started',
  },
  creating: {
    chip: 'bg-muted text-muted-foreground',
    dot: 'bg-muted-foreground/60',
    defaultLabel: 'Preparing',
  },
  requires_payment: {
    chip: 'bg-warning-background text-warning-foreground',
    dot: 'bg-warning',
    defaultLabel: 'Awaiting payment',
  },
  processing: {
    chip: 'bg-info-background text-info-foreground',
    dot: 'bg-info animate-pulse',
    defaultLabel: 'Processing',
  },
  requires_action: {
    chip: 'bg-warning-background text-warning-foreground',
    dot: 'bg-warning',
    defaultLabel: 'Action required',
  },
  succeeded: {
    chip: 'bg-success-background text-success-foreground',
    dot: 'bg-success',
    defaultLabel: 'Paid',
  },
  failed: {
    // NB: --destructive-foreground is near-white (text on SOLID destructive),
    // not a chip foreground like the success/warning/info triples — use the
    // base --destructive tone for text on the pale background.
    chip: 'bg-destructive-background text-destructive',
    dot: 'bg-destructive',
    defaultLabel: 'Failed',
  },
  canceled: {
    chip: 'bg-muted text-muted-foreground',
    dot: 'bg-muted-foreground/50',
    defaultLabel: 'Canceled',
  },
};

export function PaymentStatusBadge({ status, label, className }: PaymentStatusBadgeProps) {
  const style = STATUS_STYLES[status];
  return (
    <span
      className={[
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium',
        style.chip,
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${style.dot}`} />
      {label ?? style.defaultLabel}
    </span>
  );
}
