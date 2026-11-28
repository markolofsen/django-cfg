'use client';

/**
 * Lazy-loaded ImageViewer.
 *
 * The viewer carries react-zoom-pan-pinch (~50KB), which no chat turn needs
 * until a reader actually opens a picture — so it is split out and mounted on
 * demand rather than shipped in the first paint.
 */

import { lazy, Suspense } from 'react';

import type { ImageViewerProps } from './types';

export type { ImageViewerProps };

const ImageViewerImpl = lazy(() =>
  import('./components').then((mod) => ({ default: mod.ImageViewer })),
);

// Reserves the viewer's minimum height while the chunk arrives: a zero-height
// fallback collapses the dialog and the image then pops it back open.
function Fallback() {
  return <div aria-hidden className="min-h-[200px]" />;
}

export function LazyImageViewer(props: ImageViewerProps) {
  return (
    <Suspense fallback={<Fallback />}>
      <ImageViewerImpl {...props} />
    </Suspense>
  );
}
