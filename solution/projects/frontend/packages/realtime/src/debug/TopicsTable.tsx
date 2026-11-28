'use client';

import { Badge, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@djangocfg/ui-core';

import type { TopicRow } from './view-model';

function TopicLine({ row }: { row: TopicRow }) {
  return (
    <TableRow>
      <TableCell className="font-mono text-xs">{row.topic}</TableCell>
      <TableCell>
        <Badge variant={row.tone}>{row.status}</Badge>
      </TableCell>
      <TableCell className="font-mono text-xs">{row.offset}</TableCell>
      <TableCell className="text-right tabular-nums">{row.subscribers}</TableCell>
      <TableCell className="text-right tabular-nums">{row.received}</TableCell>
      <TableCell className="text-right tabular-nums">{row.gaps}</TableCell>
      <TableCell className="text-xs text-muted-foreground">{row.note}</TableCell>
    </TableRow>
  );
}

export function TopicsTable({ rows }: { rows: TopicRow[] }) {
  const lines = rows.map((row) => <TopicLine key={row.topic} row={row} />);
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Topic</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Offset</TableHead>
          <TableHead className="text-right">Subscribers</TableHead>
          <TableHead className="text-right">Received</TableHead>
          <TableHead className="text-right">Gaps</TableHead>
          <TableHead>Refusal</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>{lines}</TableBody>
    </Table>
  );
}
