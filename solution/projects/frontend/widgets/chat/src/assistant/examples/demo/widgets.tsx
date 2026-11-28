'use client';

import { Check, CircleDashed, FileText, Loader2, Play } from 'lucide-react';
import type { ReactNode } from 'react';

import { Badge, Progress, Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@djangocfg/ui-core/components';

import type { DataPartRenderer } from '../../shell';

/**
 * The widgets of the demo transcript, one per kind of structured part an answer can carry. They are the pattern a product copies: a payload shape,
 * a guard that returns `undefined` for a malformed one (the widget then draws its own fallback), and a card made of ready ui-core parts.
 * Every card is a block of the same width and rhythm, so a long answer reads as one column.
 */

const CARD = 'my-2 rounded-lg border bg-card p-3 text-sm';
const isObject = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null;

/* Media: the gptkino pattern, a poster row that opens the item. Fixed height, so hydrating it never moves the transcript. */
export interface MediaData { items: { id: string; title: string; meta: string; duration: string; hue: number }[] }

function Media({ data }: { data: MediaData }) {
  return (
    <div className="my-2 space-y-2">
      {data.items.map((item) => (
        <a key={item.id} href="#" onClick={(event) => event.preventDefault()} className="flex h-[62px] items-center gap-3 rounded-lg border bg-card p-1.5 no-underline outline-none hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring">
          <span className="relative flex h-full w-24 shrink-0 items-center justify-center overflow-hidden rounded-md text-white" style={{ background: `linear-gradient(135deg, hsl(${item.hue} 45% 38%), hsl(${(item.hue + 40) % 360} 40% 22%))` }}>
            <Play className="size-4 fill-current" />
            <span className="absolute bottom-0.5 right-1 text-[10px] tabular-nums">{item.duration}</span>
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-medium text-foreground">{item.title}</span>
            <span className="block truncate text-xs text-muted-foreground">{item.meta}</span>
          </span>
        </a>
      ))}
    </div>
  );
}

/* Steps: what the assistant did or is doing. */
export interface StepsData { title?: string; steps: { label: string; state: 'done' | 'running' | 'todo' }[] }

function Steps({ data }: { data: StepsData }) {
  return (
    <div className={CARD}>
      {data.title ? <p className="mb-2 font-medium">{data.title}</p> : null}
      <ul className="space-y-1.5">
        {data.steps.map((step) => (
          <li key={step.label} className="flex items-center gap-2">
            {step.state === 'done' ? <Check className="size-4 text-success" /> : step.state === 'running' ? <Loader2 className="size-4 animate-spin text-muted-foreground" /> : <CircleDashed className="size-4 text-muted-foreground" />}
            <span className={step.state === 'todo' ? 'text-muted-foreground' : undefined}>{step.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/* Metrics: a few figures and one progress bar. */
export interface MetricsData { items: { label: string; value: string; delta?: string }[]; progress?: { label: string; value: number } }

function Metrics({ data }: { data: MetricsData }) {
  return (
    <div className={CARD}>
      <div className="grid grid-cols-3 gap-3">
        {data.items.map((item) => (
          <div key={item.label}>
            <p className="text-xs text-muted-foreground">{item.label}</p>
            <p className="text-lg font-semibold tabular-nums">{item.value}</p>
            {item.delta ? <p className="text-xs text-muted-foreground">{item.delta}</p> : null}
          </div>
        ))}
      </div>
      {data.progress ? (
        <div className="mt-3 space-y-1">
          <p className="flex justify-between text-xs text-muted-foreground"><span>{data.progress.label}</span><span className="tabular-nums">{data.progress.value}%</span></p>
          <Progress value={data.progress.value} />
        </div>
      ) : null}
    </div>
  );
}

/* Table: rows with tag cells, the Notion database look. */
export interface TableData { columns: string[]; rows: { cells: string[]; tag?: { column: number; tone: 'gray' | 'blue' | 'green' | 'yellow' | 'red' | 'purple' } }[] }

function DataTable({ data }: { data: TableData }) {
  return (
    <div className="my-2 overflow-hidden rounded-lg border">
      <Table frame={false} grid className="w-full">
        <TableHeader>
          <TableRow>{data.columns.map((column) => <TableHead key={column}>{column}</TableHead>)}</TableRow>
        </TableHeader>
        <TableBody>
          {data.rows.map((row) => (
            <TableRow key={row.cells.join('|')}>
              {row.cells.map((cell, index) => (
                <TableCell key={`${index}-${cell}`}>{row.tag?.column === index ? <Badge variant={row.tag.tone}>{cell}</Badge> : cell}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

/* Files: attachments the answer produced. */
export interface FilesData { files: { name: string; size: string }[] }

function Files({ data }: { data: FilesData }) {
  return (
    <div className="my-2 flex flex-wrap gap-2">
      {data.files.map((file) => (
        <span key={file.name} className="inline-flex items-center gap-2 rounded-lg border bg-card px-2.5 py-1.5 text-xs">
          <FileText className="size-4 text-muted-foreground" />
          <span className="font-medium">{file.name}</span>
          <span className="text-muted-foreground">{file.size}</span>
        </span>
      ))}
    </div>
  );
}

const guard = <T,>(check: (data: Record<string, unknown>) => boolean, draw: (data: T) => ReactNode): DataPartRenderer => (data) => (isObject(data) && check(data) ? draw(data as T) : undefined);

/** What the demo draws, by `kind`. Pass it as `dataRenderers`. */
export const DEMO_RENDERERS: Readonly<Record<string, DataPartRenderer>> = {
  media: guard<MediaData>((d) => Array.isArray(d.items), (d) => <Media data={d} />),
  steps: guard<StepsData>((d) => Array.isArray(d.steps), (d) => <Steps data={d} />),
  metrics: guard<MetricsData>((d) => Array.isArray(d.items), (d) => <Metrics data={d} />),
  table: guard<TableData>((d) => Array.isArray(d.columns) && Array.isArray(d.rows), (d) => <DataTable data={d} />),
  files: guard<FilesData>((d) => Array.isArray(d.files), (d) => <Files data={d} />),
};
export const DEMO_PAYLOAD_KINDS: readonly string[] = Object.keys(DEMO_RENDERERS);
