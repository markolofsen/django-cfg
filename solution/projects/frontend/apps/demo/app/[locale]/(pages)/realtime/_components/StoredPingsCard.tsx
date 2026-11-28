'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui-core';

import { useAppTranslations } from '@i18n';

import type { PaginatedDemoPingList } from '@/api/generated/models/paginatedDemoPingList.zod';

interface StoredPingsCardProps {
  data: PaginatedDemoPingList | undefined;
  error: unknown;
}

/** The REST list, read by the page through the generated React Query hook. */
export function StoredPingsCard({ data, error }: StoredPingsCardProps) {
  const { app } = useAppTranslations();
  let body;
  if (error) {
    body = <p className="text-sm text-destructive">{app('realtime.loadFailed')}</p>;
  } else if (data === undefined) {
    body = <div className="h-24 animate-pulse rounded-md bg-muted" aria-label={app('realtime.loading')} />;
  } else if (data.results.length === 0) {
    body = <p className="text-sm text-muted-foreground">{app('realtime.storedEmpty')}</p>;
  } else {
    const rows = data.results.map((ping) => (
      <li key={ping.id} className="flex justify-between gap-4 border-b border-border py-2 text-sm last:border-0">
        <span className="font-medium">{ping.note || '—'}</span>
        <span className="text-xs text-muted-foreground">{ping.created_at}</span>
      </li>
    ));
    body = <ul className="max-h-72 overflow-y-auto">{rows}</ul>;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{app('realtime.stored')}</CardTitle>
        <CardDescription>{app('realtime.storedHint')}</CardDescription>
      </CardHeader>
      <CardContent>{body}</CardContent>
    </Card>
  );
}
