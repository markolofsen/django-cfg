'use client';

import React, { memo, useMemo } from 'react';

import { useImageLoader } from '@djangocfg/ui-core/hooks';

import { AuthShellProvider } from './context';
import { CenteredShell } from './CenteredShell';
import { FullSplitShell } from './FullSplitShell';
import { SplitShell } from './SplitShell';
import type { AuthShellProps } from './types';

/**
 * AuthShell — shared orchestrator for auth layout variants.
 *
 * Handles common concerns:
 *  - background image loading (via useImageLoader)
 *  - shell context registration
 *  - variant dispatch (centered | split)
 *
 * Variants own their own chrome (positioning, shape, background).
 *
 * Memoised: re-renders only when `variant`, `background`, `sidebar`,
 * `className` or `children` reference change. Background styles are
 * memoised internally so object reference churn from the parent does
 * not cause shell re-renders.
 */
function AuthShellRaw({
  variant,
  children,
  mediaSide = 'left',
  background,
  sidebar,
  topBar,
  className,
}: AuthShellProps) {
  const { isLoaded: bgLoaded, hasError: bgError } = useImageLoader(background?.imageUrl);

  // Build the image style as soon as a URL is provided (the image is
  // pre-warmed by useImageLoader, so painting it doesn't flash). `bgLoaded`
  // is passed through separately so the shell can fade the layer in once the
  // download actually completes — a quiet preloader, no spinner.
  const hasBgImage = Boolean(background?.imageUrl) && !bgError;

  const bgStyle = useMemo(() => {
    if (hasBgImage && background?.imageUrl) {
      return {
        backgroundImage: `url(${background.imageUrl})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat',
      } as React.CSSProperties;
    }
    if (background?.gradient) {
      return { background: background.gradient } as React.CSSProperties;
    }
    return undefined;
  }, [hasBgImage, background]);

  const overlayStyle = useMemo(() => {
    if (!background?.overlay) return undefined;
    return { background: background.overlay } as React.CSSProperties;
  }, [background?.overlay]);

  const blurValue = background?.blur ?? '8px';

  const shellContext = useMemo(
    () => ({
      variant,
      hasSidebar: Boolean(sidebar),
    }),
    [variant, sidebar]
  );

  const commonShellProps = {
    children,
    topBar,
    className,
    bgStyle,
    overlayStyle,
    blurValue,
    bgLoaded,
  };

  return (
    <AuthShellProvider value={shellContext}>
      {variant === 'split' ? (
        <SplitShell {...commonShellProps} sidebar={sidebar} />
      ) : variant === 'fullsplit' ? (
        <FullSplitShell {...commonShellProps} mediaSide={mediaSide} sidebar={sidebar} />
      ) : (
        <CenteredShell {...commonShellProps} />
      )}
    </AuthShellProvider>
  );
}

export const AuthShell = memo(AuthShellRaw);
