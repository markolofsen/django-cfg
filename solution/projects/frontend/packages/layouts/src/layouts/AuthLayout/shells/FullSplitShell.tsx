'use client';

import React, { memo } from 'react';

import type { ShellRenderProps } from './types';

interface FullSplitShellProps extends ShellRenderProps {
  sidebar?: React.ReactNode;
}

/**
 * FullSplitShell — full-bleed 50/50 auth layout (the large-SaaS look).
 *
 * Desktop (>= lg): edge-to-edge. Left half is the background image with an
 *   overlay and the `sidebar` content (brand + quote) laid over it; right half
 *   is a solid `--background` panel with the centered form.
 * Mobile (< lg): the image half is dropped entirely — just the plain centered
 *   form on `--background`, like an ordinary sign-in screen.
 *
 * No floating card, no glass: the two halves meet edge-to-edge, which reads as
 * a considered product layout rather than a panel hovering in space.
 *
 * Memoised: re-renders only when bgStyle, overlayStyle, blurValue, sidebar or
 * children references change.
 */
function FullSplitShellRaw({
  children,
  topBar,
  className,
  bgStyle,
  overlayStyle,
  blurValue,
  mediaSide = 'left',
  bgLoaded = false,
  sidebar,
}: FullSplitShellProps) {
  return (
    <div
      className={`auth-shell-fullsplit ${className || ''}`}
      data-media-side={mediaSide}
    >
      {/* Media half — `data-loaded` drives the image fade-in. */}
      <div className="auth-shell-fullsplit__media">
        {bgStyle && (
          <div
            className="auth-shell-fullsplit__bg"
            style={bgStyle}
            data-loaded={bgLoaded}
          />
        )}
        {overlayStyle && (
          <div
            className="auth-shell-fullsplit__overlay"
            style={{
              ...overlayStyle,
              backdropFilter: blurValue ? `blur(${blurValue})` : undefined,
              WebkitBackdropFilter: blurValue ? `blur(${blurValue})` : undefined,
            }}
          />
        )}
        {sidebar && (
          <div className="auth-shell-fullsplit__sidebar">{sidebar}</div>
        )}
      </div>

      {/* Right: solid panel with the centered form */}
      <div className="auth-shell-fullsplit__form">
        {topBar}
        <div className="auth-shell-fullsplit__form-inner">{children}</div>
      </div>
    </div>
  );
}

export const FullSplitShell = memo(FullSplitShellRaw);
