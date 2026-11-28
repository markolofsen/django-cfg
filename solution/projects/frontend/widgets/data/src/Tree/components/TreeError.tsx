'use client';

import { AlertCircle } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';

export interface TreeErrorProps {
  children: React.ReactNode;
  className?: string;
}

export function TreeError({ children, className }: TreeErrorProps) {
  return (
    <div
      className={cn(
        'flex items-start gap-2 rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive',
        className,
      )}
      role="alert"
    >
      <AlertCircle aria-hidden className="mt-0.5 size-4 shrink-0" />
      <span>{children}</span>
    </div>
  );
}
