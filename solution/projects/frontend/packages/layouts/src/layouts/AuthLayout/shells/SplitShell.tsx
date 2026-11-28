'use client';

import React, { memo } from 'react';

import type { ShellRenderProps } from './types';

interface SplitShellProps extends ShellRenderProps {
  sidebar?: React.ReactNode;
}

/**
 * SplitShell — Two-column auth layout (desktop) / single-column (mobile).
 *
 * Layout:
 * - Mobile (< xl): single column, centered form, optional background
 * - Desktop (>= xl): two columns inside a card — form left, sidebar right
 *
 * Background: full-bleed image/gradient with optional overlay + blur.
 *
 * Memoised: re-renders only when bgStyle, overlayStyle, blurValue or
 * children references change. `sidebar` is compared by reference — the
 * consumer should stabilise it (e.g. wrap in useMemo) to avoid re-renders.
 */
function SplitShellRaw({
  children,
  topBar,
  className,
  bgStyle,
  overlayStyle,
  blurValue,
  sidebar,
}: SplitShellProps) {
  return (
    <div className={`auth-shell-split ${className || ''}`}>
      {/* Background layer */}
      {bgStyle && (
        <div className="auth-shell-split__bg" style={bgStyle} />
      )}
      {overlayStyle && (
        <div
          className="auth-shell-split__overlay"
          style={{
            ...overlayStyle,
            backdropFilter: `blur(${blurValue})`,
            WebkitBackdropFilter: `blur(${blurValue})`,
          }}
        />
      )}

      {/* Card container */}
      <div className="auth-shell-split__card">
        {/* Left: form */}
        <div className="auth-shell-split__form">
          {topBar}
          <div className="auth-shell-split__form-inner">
            {children}
          </div>
        </div>

        {/* Right: sidebar (desktop only) */}
        {sidebar && (
          <div className="auth-shell-split__sidebar">
            {sidebar}
          </div>
        )}
      </div>
    </div>
  );
}

export const SplitShell = memo(SplitShellRaw);
