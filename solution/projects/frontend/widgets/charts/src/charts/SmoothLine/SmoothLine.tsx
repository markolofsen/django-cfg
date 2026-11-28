// SmoothLine — the streaming sibling of Sparkline, now drawn on a CANVAS.
//
// The trace SCROLLS left at constant velocity via the `useSmoothSeries`
// wall-clock canvas engine: every rAF frame the whole monotone-cubic curve is
// redrawn at its scrolled X (one writer, one clock), so there is no SVG-era
// path/transform desync — the jump-then-catch-up is gone by construction.
//
// Geometry stays ours: the draw callback strokes a monotone-cubic (Fritsch–
// Carlson / d3 `curveMonotoneX`) polyline through the data points, with an
// optional area fill closed to the baseline. `tension={0}` degenerates to sharp
// straight segments.
//
// Color via the token bridge, resolved ONCE per theme change (not per frame):
//   • a semantic token (`'primary' | 'success' | …`) → `useThemeColor()` → hex.
//   • `'currentColor'` → the canvas inherits an ancestor's CSS `color` (a `text-*`
//     className tint, e.g. cmdop's `text-chart-*`); we read the resolved color off
//     the canvas element via `getComputedStyle(canvas).color` and pass it to
//     `ctx.strokeStyle`. Re-resolved on theme change (the resolved-theme dep on
//     `useThemeColor`'s own re-render path drives a redraw).
//
// Requires <UiProviders> mounted by the host app (no nested providers here).

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { useThemeColor } from '@djangocfg/ui-core/styles/palette';
import { useResolvedTheme } from '@djangocfg/ui-core/hooks';
import type { SmoothLineProps } from './types';
import { useSmoothSeries, type DrawFn } from './useSmoothSeries';
import { DEFAULT_TENSION, type Pt, traceSmoothSegments } from './smoothPath';

/**
 * Map oldest-first values to logical points (shared by the line + area draws).
 *
 * The Y-domain (min/max) is computed from the drawn values. Because the engine
 * draws from a FIXED committed set between ticks (no per-frame Y-tween), the
 * domain is stable across the whole scroll — the curve never rubber-bands.
 */
function valuePoints(
  values: readonly number[],
  width: number,
  height: number,
): Pt[] {
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const span = max - min || 1;
  const stepX = values.length > 1 ? width / (values.length - 1) : width;
  return values.map((v, i) => ({
    x: i * stepX,
    y: height - ((v - min) / span) * (height - 2) - 1,
  }));
}

export function SmoothLine({
  values,
  color = 'primary',
  width = 240,
  height = 40,
  strokeWidth = 1.5,
  area = false,
  tweenMs = 1000,
  scroll = false,
  delay = true,
  tension = DEFAULT_TENSION,
  ariaLabel,
  className,
  ...rest
}: SmoothLineProps) {
  const isBridge = color === 'currentColor';
  // Semantic token → hex; bridge mode reads the canvas's inherited CSS color.
  const themeColor = useThemeColor(isBridge ? 'primary' : color);
  // Re-resolve the bridge color when the theme flips (dark/light).
  const resolvedTheme = useResolvedTheme();

  // With the right-edge lag, the drawn set drops the freshest point so the right
  // edge is always a known point; the engine's scroll reveals the off-edge value.
  const useLag = scroll && delay && values.length > 2;
  const drawn = React.useMemo(
    () => (useLag ? [...values].slice(0, -1) : [...values]),
    // values identity changes per tick; the joined key gates recompute.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [values.join(','), useLag],
  );

  // The per-frame canvas draw: monotone-cubic stroke (+ optional area), at the
  // scrolled X. Rebuilt when the committed values / geometry / color change — so
  // there is no per-frame Y-tween, only the scroll moves.
  const draw = React.useCallback<DrawFn>(
    (ctx, frame) => {
      // Resolve the stroke/fill color ONCE per draw (not a per-point cost). In
      // bridge mode read the inherited CSS color off the canvas; else the token.
      let stroke = themeColor;
      if (isBridge && ctx.canvas) {
        const c = getComputedStyle(ctx.canvas).color;
        if (c) stroke = c;
      }

      const w = frame.width;
      const h = frame.height;
      const sx = frame.scrollX;

      if (drawn.length === 0) {
        const mid = h / 2;
        ctx.beginPath();
        ctx.moveTo(0, mid);
        ctx.lineTo(w, mid);
        ctx.strokeStyle = stroke;
        ctx.lineWidth = strokeWidth;
        ctx.stroke();
        return;
      }

      const pts = valuePoints(drawn, w, h).map((p) => ({
        x: p.x + sx,
        y: p.y,
      }));

      // `valuePoints` maps `drawn` one-to-one and `drawn` is non-empty here.
      const firstPt = pts[0];
      const lastPt = pts[pts.length - 1];
      if (firstPt === undefined || lastPt === undefined) return;

      // Area fill first (under the stroke), hugging the same curve down to the
      // baseline. Opacity 0.12 matches the old SVG fill.
      if (area) {
        ctx.beginPath();
        ctx.moveTo(firstPt.x, h);
        ctx.lineTo(firstPt.x, firstPt.y);
        traceSmoothSegments(ctx, pts, tension);
        ctx.lineTo(lastPt.x, h);
        ctx.closePath();
        ctx.globalAlpha = 0.12;
        ctx.fillStyle = stroke;
        ctx.fill();
        ctx.globalAlpha = 1;
      }

      // Stroke the line over the fill.
      ctx.beginPath();
      ctx.moveTo(firstPt.x, firstPt.y);
      traceSmoothSegments(ctx, pts, tension);
      ctx.strokeStyle = stroke;
      ctx.lineWidth = strokeWidth;
      ctx.lineJoin = 'round';
      ctx.lineCap = 'round';
      ctx.stroke();
    },
    // resolvedTheme re-runs the bridge color read on a theme flip.
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [drawn, area, tension, strokeWidth, themeColor, isBridge, resolvedTheme],
  );

  const { canvasRef } = useSmoothSeries({
    values,
    tweenMs,
    scroll,
    delay,
    width,
    height,
    draw,
  });

  return (
    <div
      data-slot="smooth-line"
      data-color={color}
      className={cn('block w-full', className)}
      style={isBridge ? undefined : { color: themeColor }}
      {...rest}
    >
      <canvas
        ref={canvasRef}
        className="block w-full"
        style={{ height, color: isBridge ? undefined : themeColor }}
        role="img"
        aria-label={ariaLabel}
        aria-hidden={ariaLabel ? undefined : true}
      />
    </div>
  );
}
