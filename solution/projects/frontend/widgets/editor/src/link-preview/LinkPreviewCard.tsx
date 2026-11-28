'use client';

/**
 * LinkPreviewCard — a presentational URL-unfurl card (favicon + og:image +
 * title / description / site name), Notion / Telegram style.
 *
 * It NEVER fetches the page itself — the browser can't read cross-origin
 * meta tags (CORS). It either renders pre-resolved `data`, or calls the
 * host-provided `resolver(url)` (a Wails/Go method, a Next.js API route)
 * once on mount, showing a skeleton until it resolves. A `null` result
 * (or a thrown resolver) renders nothing.
 */

import { useEffect, useRef, useState } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { LinkPreviewData, ResolveLinkPreview } from './types';

export interface LinkPreviewCardProps {
  url: string;
  /** Pre-resolved metadata. When present, no resolver call is made. */
  data?: LinkPreviewData;
  /** Host resolver used when `data` is absent. */
  resolver?: ResolveLinkPreview;
  /** Layout — `compact` (default) is a tight horizontal card; `full` is a
   *  roomier card with a larger cover image. */
  appearance?: 'compact' | 'full';
  className?: string;
}

/** Hostname for the fallback site label / favicon. */
function hostnameOf(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return url;
  }
}

type LoadState =
  | { status: 'ready'; data: LinkPreviewData }
  | { status: 'loading' }
  | { status: 'empty' };

export function LinkPreviewCard({
  url,
  data,
  resolver,
  appearance = 'compact',
  className,
}: LinkPreviewCardProps) {
  // If data is supplied we're immediately ready; else loading (resolver) or
  // empty (nothing to do).
  const [state, setState] = useState<LoadState>(() =>
    data ? { status: 'ready', data } : resolver ? { status: 'loading' } : { status: 'empty' },
  );

  // Keep the latest resolver without re-running the effect on identity churn.
  const resolverRef = useRef(resolver);
  resolverRef.current = resolver;

  useEffect(() => {
    if (data) {
      setState({ status: 'ready', data });
      return;
    }
    const resolve = resolverRef.current;
    if (!resolve) {
      setState({ status: 'empty' });
      return;
    }

    let alive = true;
    const controller = new AbortController();
    setState({ status: 'loading' });

    resolve(url, controller.signal)
      .then((result) => {
        if (!alive) return;
        setState(result ? { status: 'ready', data: result } : { status: 'empty' });
      })
      .catch(() => {
        if (alive) setState({ status: 'empty' });
      });

    return () => {
      alive = false;
      controller.abort();
    };
  }, [url, data]);

  if (state.status === 'empty') return null;

  const host = hostnameOf(url);

  // Shared frame — matches the calm media-card surface used elsewhere.
  const frame = cn(
    'block w-full overflow-hidden rounded-2xl border border-border bg-card shadow-sm',
    'transition-colors hover:bg-accent/40',
    'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
    className,
  );

  if (state.status === 'loading') {
    return (
      <div className={cn(frame, 'pointer-events-none')} aria-busy="true">
        <div className="flex items-center gap-3 p-3">
          <div className="size-9 shrink-0 animate-pulse rounded-md bg-muted" />
          <div className="min-w-0 flex-1 space-y-2">
            <div className="h-3 w-2/3 animate-pulse rounded bg-muted" />
            <div className="h-2.5 w-1/3 animate-pulse rounded bg-muted" />
          </div>
        </div>
      </div>
    );
  }

  const meta = state.data;
  const title = meta.title || host;
  const siteName = meta.siteName || host;
  const isFull = appearance === 'full';

  return (
    <a href={url} target="_blank" rel="noopener noreferrer" className={frame}>
      {/* Cover image (full appearance, when present) — top banner. */}
      {isFull && meta.image ? (
        <img
          src={meta.image}
          alt=""
          loading="lazy"
          // Fixed banner height (not just max-h) so `object-cover` actually
          // crops to fill — with only `max-h` the image keeps its aspect and
          // letterboxes. `h-44` is a sensible cover banner.
          className="h-44 w-full border-b border-border object-cover"
        />
      ) : null}

      <div className="flex items-stretch gap-3 p-3">
        <div className="min-w-0 flex-1">
          {/* Site row — favicon + site name. */}
          <div className="mb-1 flex items-center gap-1.5 text-xs text-muted-foreground">
            {meta.favicon ? (
              <img
                src={meta.favicon}
                alt=""
                loading="lazy"
                className="size-4 shrink-0 rounded-sm"
              />
            ) : null}
            <span className="truncate">{siteName}</span>
          </div>

          <div className="line-clamp-2 text-sm font-medium text-foreground">{title}</div>

          {meta.description ? (
            <div className="mt-1 line-clamp-2 text-xs text-muted-foreground">
              {meta.description}
            </div>
          ) : null}
        </div>

        {/* Compact thumbnail (compact appearance, when present) — side. */}
        {!isFull && meta.image ? (
          <img
            src={meta.image}
            alt=""
            loading="lazy"
            className="size-16 shrink-0 self-center rounded-lg object-cover"
          />
        ) : null}
      </div>
    </a>
  );
}
