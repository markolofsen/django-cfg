'use client';

import { useMemo } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import type { SpotlightRect } from './types';

/**
 * SVG-mask spotlight renderer — adapted from the former Tour component.
 *
 * Draws a dimmed full-screen overlay with rounded cut-outs over the
 * target rects, plus a brand-coloured border and an attention pulse.
 * Pure presentation: it takes geometry, not DOM elements.
 */

// Injected once — keyframes + transition classes for the SVG rects.
const SPOTLIGHT_STYLES = `
  @keyframes chat-spotlight-pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }
  @keyframes chat-spotlight-ring {
    0% { transform: scale(1); opacity: 0.8; }
    100% { transform: scale(1.15); opacity: 0; }
  }
  .chat-spotlight-rect {
    transition: x 300ms ease-out, y 300ms ease-out,
                width 300ms ease-out, height 300ms ease-out;
  }
`;

/** Props for the spotlight canvas. */
export interface SpotlightCanvasProps {
  /** Geometry of every element to spotlight. */
  rects: SpotlightRect[];
  /** Dim-overlay opacity, 0–1 (default: 0.5). */
  opacity?: number;
  /** Show an expanding attention ring (default: true). */
  pulseRing?: boolean;
  /** Dismiss the overlay when the scrim is clicked. */
  onClick?: () => void;
  className?: string;
}

export function SpotlightCanvas({
  rects,
  opacity = 0.5,
  pulseRing = true,
  onClick,
  className,
}: SpotlightCanvasProps) {
  // Expand each rect by its padding and pre-compute the rounded box.
  // Hooks run unconditionally — no early return before this.
  const boxes = useMemo(
    () =>
      rects.map((target, index) => {
        const x = target.rect.x - target.padding;
        const y = target.rect.y - target.padding;
        const width = target.rect.width + target.padding * 2;
        const height = target.rect.height + target.padding * 2;
        const rx = target.radius + 2;
        const centerX = target.rect.x + target.rect.width / 2;
        const centerY = target.rect.y + target.rect.height / 2;
        return {
          key: index,
          x,
          y,
          width,
          height,
          rx,
          transformOrigin: `${centerX}px ${centerY}px`,
        };
      }),
    [rects],
  );

  if (rects.length === 0) return null;

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: SPOTLIGHT_STYLES }} />
      <svg
        className={cn('fixed inset-0 h-full w-full', className)}
        aria-hidden="true"
        onClick={onClick}
      >
        <defs>
          <mask id="chat-spotlight-mask">
            {/* White = visible dim; black cut-outs = transparent targets. */}
            <rect fill="white" width="100%" height="100%" />
            {boxes.map((b) => (
              <rect
                key={b.key}
                fill="black"
                className="chat-spotlight-rect"
                x={b.x}
                y={b.y}
                width={b.width}
                height={b.height}
                rx={b.rx}
                ry={b.rx}
              />
            ))}
          </mask>
        </defs>

        {/* Dimmed scrim with the target cut-outs. */}
        <rect
          fill="black"
          fillOpacity={opacity}
          width="100%"
          height="100%"
          mask="url(#chat-spotlight-mask)"
          className="transition-opacity duration-300"
        />

        {/* Attention pulse. */}
        {pulseRing &&
          boxes.map((b) => (
            <rect
              key={`pulse-${b.key}`}
              className="fill-none stroke-primary stroke-2"
              style={{
                transformOrigin: b.transformOrigin,
                animation: 'chat-spotlight-ring 1.5s ease-out infinite',
              }}
              x={b.x}
              y={b.y}
              width={b.width}
              height={b.height}
              rx={b.rx}
              ry={b.rx}
            />
          ))}

        {/* Solid border around each target. */}
        {boxes.map((b) => (
          <rect
            key={`border-${b.key}`}
            className="chat-spotlight-rect fill-none stroke-primary stroke-2"
            x={b.x}
            y={b.y}
            width={b.width}
            height={b.height}
            rx={b.rx}
            ry={b.rx}
          />
        ))}
      </svg>
    </>
  );
}
