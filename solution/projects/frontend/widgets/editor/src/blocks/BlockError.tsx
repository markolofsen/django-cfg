'use client';

/**
 * `<BlockError>` — the safe presentational fallback a data-driven block renders
 * when its payload fails schema validation (a corrupted ```map JSON, a
 * malformed wire block). Informative, not scary: a compact muted card that says
 * the block couldn't render, with an optional short reason. Never throws, so the
 * surrounding editor / message list stays alive.
 *
 * Semantic tokens only (`bg-muted` / `border-border` / `text-muted-foreground`).
 */

import { AlertTriangle } from 'lucide-react';

export interface BlockErrorProps {
  /**
   * Short, human-readable reason (e.g. the first Zod issue). Optional — when
   * omitted only the generic headline shows.
   */
  reason?: string;
  /** What couldn't be rendered (e.g. "map", "bookmark"). Defaults to "block". */
  label?: string;
  className?: string;
}

export function BlockError({ reason, label = 'block', className }: BlockErrorProps) {
  return (
    <div
      role="status"
      className={
        'flex items-start gap-2.5 rounded-lg border border-border bg-muted px-3 py-2.5 text-sm text-muted-foreground' +
        (className ? ` ${className}` : '')
      }
    >
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
      <div className="min-w-0">
        <div className="font-medium text-foreground">Couldn&apos;t render this {label}</div>
        {reason ? (
          <div className="mt-0.5 break-words text-xs text-muted-foreground">{reason}</div>
        ) : null}
      </div>
    </div>
  );
}

export default BlockError;
