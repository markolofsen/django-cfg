'use client';

import { cn } from '@djangocfg/ui-core/lib';

export interface TreeSkeletonProps {
  rows?: number;
  className?: string;
}

export function TreeSkeleton({ rows = 6, className }: TreeSkeletonProps) {
  return (
    <div className={cn('flex flex-col gap-1 p-2', className)} aria-hidden>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex items-center gap-2" style={{ paddingLeft: (i % 3) * 16 }}>
          <span className="size-4 shrink-0 animate-pulse rounded bg-muted" />
          <span className="size-4 shrink-0 animate-pulse rounded bg-muted" />
          <span className="h-3 flex-1 animate-pulse rounded bg-muted" />
        </div>
      ))}
    </div>
  );
}
