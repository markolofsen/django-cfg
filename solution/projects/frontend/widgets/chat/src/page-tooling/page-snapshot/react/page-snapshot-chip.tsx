'use client';

import { useState } from 'react';

import { cn } from '@djangocfg/ui-core/lib';
import { Eye, MonitorUp, RefreshCw } from 'lucide-react';

import { PageSnapshotPreview } from './page-snapshot-preview';
import { usePageSnapshot } from './use-page-snapshot';

/** Props for `PageSnapshotChip`. */
export interface PageSnapshotChipProps {
  className?: string;
}

/**
 * A small status chip the user sees near the composer when page-context
 * sharing is on. Communicates three things:
 *   - that the screen is currently shared ("Screen connected"),
 *   - whether the captured context is stale vs the page they now see,
 *   - a way to inspect exactly what is shared (opens the preview drawer).
 *
 * Renders nothing when the user has not opted in — no opt-in, no chip.
 */
export function PageSnapshotChip({ className }: PageSnapshotChipProps) {
  const { isLinked, isStale, refresh } = usePageSnapshot();
  const [previewOpen, setPreviewOpen] = useState(false);

  // No chip at all until the user opts in.
  if (!isLinked) return null;

  return (
    <>
      <div
        className={cn(
          'inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs',
          isStale
            ? 'border-warning-border/40 text-warning'
            : 'border-border text-muted-foreground',
          className,
        )}
      >
        <MonitorUp className="size-3.5" aria-hidden />
        <span>{isStale ? 'Screen changed' : 'Screen connected'}</span>

        {/* Refresh — only meaningful once the context is stale. */}
        {isStale && (
          <button
            type="button"
            onClick={refresh}
            className="hover:text-foreground inline-flex items-center"
            aria-label="Refresh page context"
          >
            <RefreshCw className="size-3.5" aria-hidden />
          </button>
        )}

        {/* Inspect — opens the preview drawer (the trust surface). */}
        <button
          type="button"
          onClick={() => setPreviewOpen(true)}
          className="hover:text-foreground inline-flex items-center"
          aria-label="Preview shared page context"
        >
          <Eye className="size-3.5" aria-hidden />
        </button>
      </div>

      <PageSnapshotPreview open={previewOpen} onOpenChange={setPreviewOpen} />
    </>
  );
}
