'use client';

import { ScrollArea } from '@djangocfg/ui-core';

import type { FrameRow } from './view-model';

function FrameLine({ row }: { row: FrameRow }) {
  return (
    <li className="grid grid-cols-[6.5rem_1rem_4.5rem_minmax(0,1fr)] gap-2 py-1 font-mono text-xs">
      <span className="text-muted-foreground tabular-nums">{row.time}</span>
      <span aria-hidden="true">{row.direction}</span>
      <span className="font-semibold">{row.op}</span>
      <span className="truncate" title={row.text}>
        {row.text}
      </span>
    </li>
  );
}

export function FramesList({ rows }: { rows: FrameRow[] }) {
  const lines = rows.map((row) => <FrameLine key={row.id} row={row} />);
  return (
    <ScrollArea className="h-64">
      <ul aria-label="Last frames, newest first" className="divide-y divide-border pr-3">
        {lines}
      </ul>
    </ScrollArea>
  );
}
