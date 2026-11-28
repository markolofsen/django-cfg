'use client';

import { cva, type VariantProps } from 'class-variance-authority';

export const fpsVariants = cva(
  'z-50 flex shrink-0 items-center gap-2 rounded-sm border bg-background/80 px-3 py-1.5 font-mono text-foreground text-sm backdrop-blur-sm',
  {
    variants: {
      strategy: {
        fixed: 'fixed',
        absolute: 'absolute',
      },
      position: {
        'top-left': 'top-4 left-4',
        'top-right': 'top-4 right-4',
        'bottom-left': 'bottom-4 left-4',
        'bottom-right': 'right-4 bottom-4',
      },
      status: {
        good: 'text-primary',
        warning: 'text-warning',
        error: 'text-destructive',
      },
    },
    defaultVariants: {
      strategy: 'fixed',
      position: 'top-right',
      status: 'good',
    },
  }
);

export interface FpsProps
  extends React.ComponentProps<'div'>,
    Omit<VariantProps<typeof fpsVariants>, 'status'> {
  label?: string;
  updateInterval?: number;
  warningThreshold?: number;
  errorThreshold?: number;
  portalContainer?: Element | DocumentFragment | null;
  enabled?: boolean;
}
