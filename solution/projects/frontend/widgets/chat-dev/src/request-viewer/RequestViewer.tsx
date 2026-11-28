// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Lightweight HTTP inspector — headers / body / timing in tabs. Renders an
// already-executed request/response object; never fetches. For an
// interactive request playground, use OpenapiViewer instead.
//
// Requires <UiProviders> mounted at the host root (Tabs use Radix primitives).

'use client';

import * as React from 'react';
import { Clock, FileText, Globe, Activity } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@djangocfg/ui-core';
import { cn } from '@djangocfg/ui-core/lib';
import { methodColor, statusColor } from './http';
import {
  METHOD_TONE_TEXT,
  STATUS_TONE_PILL,
  type RequestViewerProps,
  type RequestViewerTab,
} from './types';
import { HeadersTab } from './components/HeadersTab';
import { BodyTab } from './components/BodyTab';
import { TimingTab } from './components/TimingTab';
import { formatDuration } from './components/utils';

export function RequestViewer({
  request,
  defaultTab = 'headers',
  className,
  ...props
}: RequestViewerProps) {
  const headerCount =
    (request.requestHeaders?.length ?? 0) +
    (request.responseHeaders?.length ?? 0);
  const timingCount = request.timing?.length ?? 0;

  const methodToneCls = METHOD_TONE_TEXT[methodColor(request.method)];
  const statusToneCls = STATUS_TONE_PILL[statusColor(request.status)];

  return (
    <div
      data-slot="request-viewer"
      className={cn(
        'overflow-hidden rounded-xl border border-border/60 bg-card shadow-sm',
        className,
      )}
      {...props}
    >
      {/* Request summary */}
      <div className="flex flex-wrap items-center gap-3 border-b border-border/40 px-4 py-3">
        <span
          className={cn(
            'font-mono text-sm font-bold uppercase',
            methodToneCls,
          )}
        >
          {request.method}
        </span>
        <span className="min-w-0 flex-1 truncate font-mono text-sm text-muted-foreground">
          {request.url}
        </span>
        <span
          className={cn(
            'inline-flex items-center rounded-md px-2.5 py-0.5 font-mono text-xs font-semibold',
            statusToneCls,
          )}
        >
          {request.status}
          {request.statusText ? ` ${request.statusText}` : null}
        </span>
        {request.duration !== undefined && (
          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="size-3" />
            {formatDuration(request.duration)}
          </span>
        )}
      </div>

      {/* Tabs */}
      <Tabs defaultValue={defaultTab satisfies RequestViewerTab}>
        <div className="border-b border-border/40 bg-muted/20 px-2 pt-2">
          <TabsList variant="underline">
            <TabsTrigger value="headers">
              <FileText className="size-3.5 mr-1.5" />
              Headers
              {headerCount > 0 && (
                <span className="ml-1.5 rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-semibold leading-none">
                  {headerCount}
                </span>
              )}
            </TabsTrigger>
            <TabsTrigger value="body">
              <Globe className="size-3.5 mr-1.5" />
              Body
            </TabsTrigger>
            <TabsTrigger value="timing">
              <Activity className="size-3.5 mr-1.5" />
              Timing
              {timingCount > 0 && (
                <span className="ml-1.5 rounded-full bg-muted px-1.5 py-0.5 text-[10px] font-semibold leading-none">
                  {timingCount}
                </span>
              )}
            </TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value="headers" className="mt-0">
          <HeadersTab request={request} />
        </TabsContent>
        <TabsContent value="body" className="mt-0">
          <BodyTab request={request} />
        </TabsContent>
        <TabsContent value="timing" className="mt-0">
          <TimingTab request={request} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
