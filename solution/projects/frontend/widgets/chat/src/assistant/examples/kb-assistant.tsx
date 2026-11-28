import type { ReactNode } from 'react';

import type { DataPartRenderer } from '../shell';

/**
 * A plain knowledge-base host, not a film site: the answer carries a `citations` payload and the host draws it as a numbered list. It is the reference the
 * tests mount, and the shape a new product copies: the payload kinds it draws, and a renderer per kind.
 */
export interface Citation {
  n: number;
  title: string;
  heading_path?: string[];
  url?: string;
}

const isCitations = (data: unknown): data is { items: Citation[] } =>
  typeof data === 'object' && data !== null && Array.isArray((data as { items?: unknown }).items);

export const citationsRenderer: DataPartRenderer = (data): ReactNode | undefined => {
  if (!isCitations(data) || data.items.length === 0) return undefined;
  return (
    <ol className="mt-2 space-y-1 text-sm text-muted-foreground">
      {data.items.map((item) => (
        <li key={item.n}>
          [{item.n}] {item.url ? <a href={item.url}>{item.title}</a> : item.title}
          {item.heading_path && item.heading_path.length > 1 ? ` — ${item.heading_path.slice(1).join(' › ')}` : ''}
        </li>
      ))}
    </ol>
  );
};

/** What the host draws, by `kind`. Pass it as `dataRenderers`, and its keys as `payloadKinds`. */
export const KB_RENDERERS: Readonly<Record<string, DataPartRenderer>> = { citations: citationsRenderer };
export const KB_PAYLOAD_KINDS: readonly string[] = Object.keys(KB_RENDERERS);
