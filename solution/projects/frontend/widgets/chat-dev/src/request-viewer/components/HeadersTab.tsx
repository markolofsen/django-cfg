// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { ArrowDown, ArrowUp, type LucideIcon } from 'lucide-react';
import { cn } from '@djangocfg/ui-core/lib';
import type { HeaderEntry, NetworkRequest } from '../types';
import { EmptyState } from './EmptyState';

function HeadersTable({
  title,
  headers,
  icon: Icon,
}: {
  title: string;
  headers: HeaderEntry[];
  icon: LucideIcon;
}) {
  if (headers.length === 0) return null;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-1.5">
        <Icon className="size-3.5 text-muted-foreground" />
        <h4 className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {title}
        </h4>
      </div>
      <div className="overflow-hidden rounded-lg border border-border/60">
        {headers.map((header, i) => (
          <div
            key={`${header.name}-${i}`}
            className={cn(
              'flex gap-4 px-3 py-2 text-sm',
              i !== headers.length - 1 && 'border-b border-border/40',
            )}
          >
            <span className="w-[200px] shrink-0 truncate font-mono text-xs font-medium text-foreground">
              {header.name}
            </span>
            <span className="min-w-0 flex-1 break-all font-mono text-xs text-muted-foreground">
              {header.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function HeadersTab({ request }: { request: NetworkRequest }) {
  const hasRequest = (request.requestHeaders?.length ?? 0) > 0;
  const hasResponse = (request.responseHeaders?.length ?? 0) > 0;

  if (!hasRequest && !hasResponse) {
    return <EmptyState message="No headers available." />;
  }

  return (
    <div className="flex flex-col gap-5 p-4">
      {hasRequest && (
        <HeadersTable
          title="Request Headers"
          headers={request.requestHeaders!}
          icon={ArrowUp}
        />
      )}
      {hasResponse && (
        <HeadersTable
          title="Response Headers"
          headers={request.responseHeaders!}
          icon={ArrowDown}
        />
      )}
    </div>
  );
}
