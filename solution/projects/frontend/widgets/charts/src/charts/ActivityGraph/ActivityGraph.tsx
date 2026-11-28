// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// GitHub-style activity heatmap that visualizes daily counts as a
// color-intensity grid. Auto-sizes blocks to fit the container by default.
//
// Port notes:
//   - Cell colors resolve through `useThemeColor('primary')` + `alpha(...)`,
//     not raw `bg-emerald-*` (CONTRACT §2, AUDIT §1). The five emerald
//     stops in the original collapse to five opacity stops on the active
//     theme's `primary` token, which means the heatmap follows the theme
//     preset automatically.
//   - Intensity bucketing routed through `getIntensity` from
//     `@djangocfg/ui-core/lib` (CONTRACT shared util added in Phase 0).
//   - Container sizing routed through `useResizeObserver` from
//     `@djangocfg/ui-core/hooks` (shared RO from Phase 0), replacing the
//     local `ResizeObserver` instance in the source.
//   - Tooltips: the original wrapped every cell in its own Radix
//     `Tooltip.Provider`. Mounting a provider per cell violates CONTRACT
//     §5 ("no nested providers") and explodes to 365 portals on a default
//     52-week graph. The port uses the native `title` attribute on each
//     cell instead — accessible, no provider dependency, no portal.

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { getIntensity } from '@djangocfg/ui-core/lib';
import { useResizeObserver } from '@djangocfg/ui-core/hooks';
import { useThemeColor, alpha } from '@djangocfg/ui-core/styles/palette';

import {
  DAY_LABEL_ROWS,
  DAY_LABEL_WIDTH,
  DEFAULT_INTENSITY_OPACITY,
  DEFAULT_INTENSITY_THRESHOLDS,
  GAP,
  MONTH_LABEL_HEIGHT,
  type ActivityGraphProps,
} from './types';
import { buildWeeks, formatDate, getMonthLabels } from './utils';

export function ActivityGraph({
  data,
  intensityOpacity = DEFAULT_INTENSITY_OPACITY,
  blockSize: fixedBlockSize,
  blockRadius = 2,
  weeks: weekCount = 52,
  className,
  ...props
}: ActivityGraphProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const { width: containerWidth } = useResizeObserver(containerRef);

  const isAutoFit = fixedBlockSize == null;

  // Auto-fit cell size based on container width. Falls back to a small
  // default until the first measurement lands (consistent with original).
  const autoSize = React.useMemo(() => {
    if (!isAutoFit || containerWidth <= 0) return null;
    const available = containerWidth - DAY_LABEL_WIDTH;
    const size = (available - GAP * (weekCount - 1)) / weekCount;
    return Math.max(4, Math.floor(size));
  }, [isAutoFit, containerWidth, weekCount]);

  const blockSize = fixedBlockSize ?? autoSize ?? 10;
  const showGraph = !isAutoFit || autoSize != null;

  // Resolve the theme color once; map each intensity bucket to an
  // opacity stop applied to that color (see CONTRACT §3 — never raw
  // Tailwind class for parametric colors).
  const primary = useThemeColor('primary');
  const intensityColors = React.useMemo(
    () => intensityOpacity.map((op) => alpha(primary, op)),
    [primary, intensityOpacity],
  );

  const weeks = React.useMemo(() => buildWeeks(data, weekCount), [data, weekCount]);
  const maxCount = React.useMemo(
    () => data.reduce((m, d) => (d.count > m ? d.count : m), 0),
    [data],
  );
  const monthLabels = React.useMemo(
    () => getMonthLabels(weeks, blockSize),
    [weeks, blockSize],
  );

  const gridWidth = weeks.length * (blockSize + GAP) - GAP;
  const gridHeight = 7 * (blockSize + GAP) - GAP;
  const totalWidth = DAY_LABEL_WIDTH + gridWidth;

  return (
    <div
      ref={containerRef}
      className={cn(isAutoFit ? 'w-full' : 'overflow-x-auto', className)}
      role="img"
      aria-label="Activity graph"
      data-slot="activity-graph"
      {...props}
    >
      {showGraph && (
        <div
          className="flex flex-col gap-2"
          style={{ minWidth: isAutoFit ? undefined : totalWidth }}
        >
          <div
            className="relative"
            style={{
              width: isAutoFit ? '100%' : totalWidth,
              height: MONTH_LABEL_HEIGHT + gridHeight,
            }}
          >
            {monthLabels.map((m, i) => (
              <span
                key={`${m.label}-${i}`}
                className="absolute text-[10px] leading-none text-muted-foreground"
                style={{ left: DAY_LABEL_WIDTH + m.offset, top: 0 }}
              >
                {m.label}
              </span>
            ))}

            {DAY_LABEL_ROWS.map(({ label, row }) => (
              <span
                key={label}
                className="absolute text-[10px] leading-none text-muted-foreground"
                style={{
                  left: 0,
                  top: MONTH_LABEL_HEIGHT + row * (blockSize + GAP) + blockSize / 2 - 4,
                }}
              >
                {label}
              </span>
            ))}

            <div
              className="absolute"
              style={{
                left: DAY_LABEL_WIDTH,
                top: MONTH_LABEL_HEIGHT,
                display: 'flex',
                gap: GAP,
              }}
            >
              {weeks.map((week, wi) => (
                <div key={wi} style={{ display: 'flex', flexDirection: 'column', gap: GAP }}>
                  {week.map((day, di) => {
                    const ratio = maxCount > 0 ? day.count / maxCount : 0;
                    const intensity = getIntensity(ratio, [...DEFAULT_INTENSITY_THRESHOLDS]);
                    const title = `${day.count} contribution${day.count === 1 ? '' : 's'} — ${formatDate(day.date)}`;
                    return (
                      <div
                        key={di}
                        data-slot="activity-graph-cell"
                        data-intensity={intensity}
                        className="transition-colors"
                        title={title}
                        style={{
                          width: blockSize,
                          height: blockSize,
                          borderRadius: blockRadius,
                          backgroundColor: intensityColors[intensity],
                        }}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-1.5 self-end text-[10px] text-muted-foreground">
            <span>Less</span>
            {intensityColors.map((color, i) => (
              <div
                key={i}
                style={{
                  width: blockSize,
                  height: blockSize,
                  borderRadius: blockRadius,
                  backgroundColor: color,
                }}
              />
            ))}
            <span>More</span>
          </div>
        </div>
      )}
    </div>
  );
}
