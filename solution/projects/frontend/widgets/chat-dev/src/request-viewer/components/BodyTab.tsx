// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { JsonTree } from '@djangocfg/widget-data/json-tree';
import type { NetworkRequest } from '../types';
import { byteSize, looksLikeJson, tryParseJson } from './utils';
import { EmptyState } from './EmptyState';

export function BodyTab({ request }: { request: NetworkRequest }) {
  if (!request.responseBody) {
    return <EmptyState message="No response body available." />;
  }

  const declaredJson = request.contentType?.toLowerCase().includes('json');
  const isJson = declaredJson || looksLikeJson(request.responseBody);
  const parsed = isJson ? tryParseJson(request.responseBody) : null;

  return (
    <div className="flex flex-col gap-2 p-4">
      {request.contentType && (
        <div className="flex items-center gap-2">
          <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-[10px] font-medium text-muted-foreground">
            {request.contentType}
          </span>
          <span className="text-[10px] text-muted-foreground">
            {byteSize(request.responseBody)}
          </span>
        </div>
      )}
      {parsed !== null ? (
        // JsonTree provides collapsible tree + search/copy for structured bodies.
        <JsonTree data={parsed} bordered toolbar="always" compactHeader />
      ) : (
        <div className="overflow-auto rounded-lg border border-border/60 bg-muted/30">
          <pre className="p-4 text-xs leading-relaxed text-foreground">
            <code>{request.responseBody}</code>
          </pre>
        </div>
      )}
    </div>
  );
}
