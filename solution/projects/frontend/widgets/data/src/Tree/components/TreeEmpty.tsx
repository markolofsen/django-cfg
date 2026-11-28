'use client';

import { cn } from '@djangocfg/ui-core/lib';

export interface TreeEmptyProps {
  children: React.ReactNode;
  className?: string;
}

export function TreeEmpty({ children, className }: TreeEmptyProps) {
  return (
    <div
      role="status"
      className={cn(
        'flex h-full min-h-32 items-center justify-center px-4 py-6 text-sm text-muted-foreground',
        className,
      )}
    >
      {children}
    </div>
  );
}
