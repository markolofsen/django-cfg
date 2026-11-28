'use client';

import { useAppTranslations } from '@i18n';

import type { LoggedPing } from './useTopicLog';

/** Received pings, newest first, or `empty` when there are none. */
export function PingList({ entries, empty }: { entries: LoggedPing[]; empty: string }) {
  const { app } = useAppTranslations();
  if (entries.length === 0) {
    return <p className="text-sm text-muted-foreground">{empty}</p>;
  }
  const rows = entries.map((entry) => {
    const origin = entry.originCid === null
      ? app('realtime.originNone')
      : `${app('realtime.origin')} ${entry.originCid}`;
    const note = entry.note || '—';
    return (
      <li key={entry.offset} className="flex flex-col gap-0.5 border-b border-border py-2 last:border-0">
        <div className="flex justify-between gap-4 text-sm">
          <span className="font-medium">{note}</span>
          <span className="font-mono text-xs text-muted-foreground">{entry.offset}</span>
        </div>
        <div className="flex justify-between gap-4 text-xs text-muted-foreground">
          <span>{entry.at}</span>
          <span>{origin}</span>
        </div>
      </li>
    );
  });
  return <ul className="max-h-72 overflow-y-auto">{rows}</ul>;
}
