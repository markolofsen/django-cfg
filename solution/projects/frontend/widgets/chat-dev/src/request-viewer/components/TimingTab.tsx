// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { useStylePresets } from '@djangocfg/ui-core/styles/palette';
import { cn } from '@djangocfg/ui-core/lib';
import type { NetworkRequest } from '../types';
import { EmptyState } from './EmptyState';
import { formatDuration } from './utils';

/**
 * Categorical palette for timing phases (DNS, TCP, TLS, …). Stages are not
 * statuses, so we route through `useStylePresets()` — 8 distinguishable hex
 * colors that respect the active theme. Indices wrap modulo length.
 */
function useStagePalette(): string[] {
  const presets = useStylePresets();
  return React.useMemo(
    () => [
      presets.primary.fill,
      presets.success.fill,
      presets.warning.fill,
      presets.danger.fill,
      presets.info.fill,
      presets.chart3.fill,
      presets.chart4.fill,
      presets.chart5.fill,
    ],
    [presets],
  );
}

export function TimingTab({ request }: { request: NetworkRequest }) {
  const stagePalette = useStagePalette();

  if (!request.timing || request.timing.length === 0) {
    return <EmptyState message="No timing data available." />;
  }

  const timing = request.timing;
  const maxDuration = Math.max(...timing.map((t) => t.duration));
  const totalDuration =
    request.duration ?? timing.reduce((sum, t) => sum + t.duration, 0);

  return (
    <div className="flex flex-col gap-4 p-4">
      {/* Total */}
      <div className="flex items-baseline justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Total Duration
        </span>
        <span className="font-mono text-sm font-semibold text-foreground">
          {formatDuration(totalDuration)}
        </span>
      </div>

      {/* Waterfall */}
      <div className="flex flex-col gap-2.5">
        {timing.map((entry, i) => {
          const percentage =
            maxDuration > 0 ? (entry.duration / maxDuration) * 100 : 0;
          const color = stagePalette[i % stagePalette.length];

          return (
            <div
              key={`${entry.label}-${i}`}
              className="flex items-center gap-3"
            >
              <span className="w-[120px] shrink-0 truncate text-xs text-muted-foreground">
                {entry.label}
              </span>
              <div className="relative h-5 flex-1 overflow-hidden rounded-md bg-muted/50">
                <div
                  className={cn('h-full rounded-md transition-all')}
                  style={{
                    width: `${Math.max(percentage, 2)}%`,
                    opacity: percentage === 0 ? 0.3 : 1,
                    backgroundColor: color,
                  }}
                />
              </div>
              <span className="w-[64px] shrink-0 text-right font-mono text-xs text-muted-foreground">
                {formatDuration(entry.duration)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 border-t border-border/40 pt-3">
        {timing.map((entry, i) => {
          const color = stagePalette[i % stagePalette.length];
          return (
            <div
              key={`legend-${entry.label}-${i}`}
              className="flex items-center gap-1.5"
            >
              <span
                className="size-2.5 rounded-full"
                style={{ backgroundColor: color }}
              />
              <span className="text-[10px] text-muted-foreground">
                {entry.label}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
