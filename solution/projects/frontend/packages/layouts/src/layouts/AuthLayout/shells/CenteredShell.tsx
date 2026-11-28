'use client';

import React, { memo } from 'react';

import type { ShellRenderProps } from './types';

/**
 * CenteredShell — frameless auth layout, full viewport centering.
 *
 * Default background is plain `var(--background)` — the form chrome
 * carries the design. Callers can still supply a custom
 * image/gradient/overlay via `bgStyle` / `overlayStyle`.
 */
function CenteredShellRaw({
  children,
  topBar,
  className,
  bgStyle,
  overlayStyle,
}: ShellRenderProps) {
  const hasCustomBg = Boolean(bgStyle);

  return (
    <div className={`auth-shell-centered ${className || ''}`}>
      {hasCustomBg && (
        <>
          <div className="auth-shell-centered__bg" style={bgStyle} />
          {overlayStyle && (
            <div className="auth-shell-centered__overlay" style={overlayStyle} />
          )}
        </>
      )}

      {topBar && <div className="auth-shell-centered__topbar">{topBar}</div>}

      <div className="auth-shell-centered__content">
        {children}
      </div>
    </div>
  );
}

export const CenteredShell = memo(CenteredShellRaw);
