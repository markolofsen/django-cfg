'use client';

/**
 * Lazy ImageLightbox: the engine and its three plugins load when a reader first
 * opens a picture, not with the page. Mounted only while `open`, so nothing is
 * fetched (and nothing renders on the server) until then.
 */

import { lazy, Suspense } from 'react';

import type { ImageLightboxProps } from '../types';

const ImageLightboxImpl = lazy(() =>
  import('./ImageLightbox').then((mod) => ({ default: mod.ImageLightbox })),
);

export function LazyImageLightbox(props: ImageLightboxProps) {
  if (!props.open) return null;
  return (
    <Suspense fallback={null}>
      <ImageLightboxImpl {...props} />
    </Suspense>
  );
}
