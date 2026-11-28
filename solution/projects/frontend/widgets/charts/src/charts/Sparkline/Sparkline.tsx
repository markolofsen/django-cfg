// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// Generic inline SVG sparkline. Pure SVG, no charting deps. Color resolves
// through the theme palette (semantic token → hex), so the stroke and area
// fill follow the active preset.
//
// Requires <UiProviders> mounted by the host app (no nested providers here).

'use client';

import * as React from 'react';
import { cn } from '@djangocfg/ui-core/lib';
import { useThemeColor, alpha } from '@djangocfg/ui-core/styles/palette';
import type { SparklineDatum, SparklineProps } from './types';

function toValue(d: SparklineDatum): number {
  return typeof d === 'number' ? d : d.value;
}

interface Stats {
  values: number[];
  min: number;
  max: number;
  range: number;
  avg: number;
}

function computeStats(data: SparklineDatum[]): Stats {
  const values = data.map(toValue);
  // No floor on the max: forcing it to at least 1 flattens an all-negative
  // series, whose real peak then never reaches the top of the box. `range`
  // below already covers the flat and empty cases.
  const max = values.length > 0 ? Math.max(...values) : 1;
  const min = values.length > 0 ? Math.min(...values) : 0;
  const range = max - min || 1;
  const total = values.reduce((s, v) => s + v, 0);
  const avg = values.length > 0 ? total / values.length : 0;
  return { values, min, max, range, avg };
}

function buildLinePath(
  values: number[],
  width: number,
  height: number,
  padding: number,
  min: number,
  range: number,
): string {
  if (values.length === 0) return '';
  const drawHeight = height - padding * 2;
  const drawWidth = width - padding * 2;
  const denom = values.length - 1 || 1;

  return values
    .map((v, i) => {
      const x = padding + (i / denom) * drawWidth;
      const y = padding + drawHeight - ((v - min) / range) * drawHeight;
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(' ');
}

function buildAreaPath(
  linePath: string,
  width: number,
  height: number,
  padding: number,
): string {
  if (!linePath) return '';
  const lastX = width - padding;
  const firstX = padding;
  const bottom = height - padding;
  return `${linePath} L ${lastX.toFixed(2)} ${bottom.toFixed(2)} L ${firstX.toFixed(2)} ${bottom.toFixed(2)} Z`;
}

function getEndpoint(
  values: number[],
  width: number,
  height: number,
  padding: number,
  min: number,
  range: number,
): { x: number; y: number } | null {
  const lastV = values[values.length - 1];
  if (lastV === undefined) return null;
  const drawHeight = height - padding * 2;
  return {
    x: width - padding,
    y: padding + drawHeight - ((lastV - min) / range) * drawHeight,
  };
}

function getBaselineY(
  avg: number,
  height: number,
  padding: number,
  min: number,
  range: number,
): number {
  const drawHeight = height - padding * 2;
  return padding + drawHeight - ((avg - min) / range) * drawHeight;
}

export function Sparkline({
  data,
  variant = 'line',
  color = 'primary',
  width = 120,
  height = 32,
  strokeWidth = 1.5,
  showEndpoint = true,
  showBaseline = false,
  ariaLabel,
  className,
  ...rest
}: SparklineProps) {
  const stroke = useThemeColor(color);
  const fill = alpha(stroke, 0.15);
  const baselineStroke = alpha(stroke, 0.4);

  if (data.length === 0) return null;

  const stats = computeStats(data);
  const padding = variant === 'bar' ? 2 : 2 + strokeWidth;
  const linePath =
    variant !== 'bar'
      ? buildLinePath(stats.values, width, height, padding, stats.min, stats.range)
      : '';
  const areaPath = variant === 'area' ? buildAreaPath(linePath, width, height, padding) : '';
  const endpoint =
    showEndpoint && variant !== 'bar'
      ? getEndpoint(stats.values, width, height, padding, stats.min, stats.range)
      : null;
  const baselineY = showBaseline
    ? getBaselineY(stats.avg, height, padding, stats.min, stats.range)
    : null;

  return (
    <div
      data-slot="sparkline"
      data-variant={variant}
      data-color={color}
      className={cn('inline-flex items-center', className)}
      {...rest}
    >
      <svg
        viewBox={`0 0 ${width} ${height}`}
        width={width}
        height={height}
        fill="none"
        role="img"
        aria-label={ariaLabel}
        aria-hidden={ariaLabel ? undefined : true}
        className="block"
      >
        {baselineY != null && (
          <line
            x1={padding}
            y1={baselineY}
            x2={width - padding}
            y2={baselineY}
            stroke={baselineStroke}
            strokeWidth={0.75}
            strokeDasharray="3 3"
          />
        )}

        {variant === 'bar' && (() => {
          const drawHeight = height - padding * 2;
          const drawWidth = width - padding * 2;
          const gap = 1;
          const barWidth = Math.max(
            1,
            (drawWidth - gap * (stats.values.length - 1)) / stats.values.length,
          );
          const denom = stats.values.length - 1 || 1;
          return stats.values.map((v, i) => {
            const barHeight = Math.max(1, ((v - stats.min) / stats.range) * drawHeight);
            const x = padding + i * (barWidth + gap);
            const y = padding + drawHeight - barHeight;
            return (
              <rect
                key={i}
                x={x}
                y={y}
                width={barWidth}
                height={barHeight}
                rx={Math.min(barWidth / 2, 1)}
                fill={stroke}
                opacity={0.7 + 0.3 * (i / denom)}
              />
            );
          });
        })()}

        {variant === 'area' && areaPath && <path d={areaPath} fill={fill} />}

        {variant !== 'bar' && linePath && (
          <path
            d={linePath}
            stroke={stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
          />
        )}

        {endpoint && (
          <circle
            cx={endpoint.x}
            cy={endpoint.y}
            r={strokeWidth + 0.5}
            fill={stroke}
          />
        )}
      </svg>
    </div>
  );
}
