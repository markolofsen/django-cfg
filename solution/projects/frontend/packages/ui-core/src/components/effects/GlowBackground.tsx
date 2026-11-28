'use client';

import * as React from 'react';

export interface GlowBackgroundProps {
  className?: string;
  /**
   * Overall opacity of the glow layer (0..1). Use ≤0.5 when the glow
   * sits behind dense UI like forms — the default `1` is tuned for
   * marketing surfaces and quickly drowns small inputs.
   * @default 1
   */
  intensity?: number;
}

/**
 * GlowBackground — animated mesh gradient backdrop.
 *
 * Renders as `position: absolute inset-0` — must be placed inside
 * a `position: relative` container. Content goes on top with `position: relative`.
 *
 * @example
 * ```tsx
 * <div style={{ position: 'relative', minHeight: '100vh' }}>
 *   <GlowBackground />
 *   <div style={{ position: 'relative' }}>{content}</div>
 * </div>
 * ```
 */
export const GlowBackground = React.memo(({ className, intensity = 1 }: GlowBackgroundProps) => (
  <div
    aria-hidden="true"
    style={{
      position: 'absolute',
      inset: 0,
      overflow: 'hidden',
      pointerEvents: 'none',
      zIndex: 0,
      opacity: intensity,
    }}
    className={className}
  >
    {/* Primary-hue blob — top left (follows --primary) */}
    <div style={{
      position: 'absolute',
      top: '-10%',
      left: '-10%',
      width: 700,
      height: 700,
      borderRadius: '50%',
      background: 'radial-gradient(circle, color-mix(in oklab, var(--primary) 45%, transparent) 0%, transparent 70%)',
      filter: 'blur(80px)',
      animation: 'blob 10s ease-in-out infinite',
    }} />

    {/* Purple blob — bottom right */}
    <div style={{
      position: 'absolute',
      bottom: '-10%',
      right: '-10%',
      width: 600,
      height: 600,
      borderRadius: '50%',
      background: 'radial-gradient(circle, hsl(262 83% 65% / 0.4) 0%, transparent 70%)',
      filter: 'blur(80px)',
      animation: 'blob 10s ease-in-out infinite',
      animationDelay: '3s',
    }} />

    {/* Indigo blob — center top */}
    <div style={{
      position: 'absolute',
      top: '10%',
      right: '20%',
      width: 400,
      height: 400,
      borderRadius: '50%',
      background: 'radial-gradient(circle, hsl(234 89% 74% / 0.35) 0%, transparent 70%)',
      filter: 'blur(60px)',
      animation: 'blob 12s ease-in-out infinite',
      animationDelay: '6s',
    }} />
  </div>
));

GlowBackground.displayName = 'GlowBackground';
