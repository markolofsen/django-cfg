'use client';

/**
 * ImageLightbox - modal gallery on yet-another-react-lightbox.
 *
 * The engine owns what is costly to get right: focus trap, swipe, preload of
 * the neighbours, keyboard, wheel/pinch zoom, and a double-click that zooms in
 * and back out. This file only configures it, themes it from tokens
 * (`lightbox.css`) and adds the SAVE button with the same same-origin rule the
 * embedded viewer has.
 */

import { Download } from 'lucide-react';
import { useCallback, useMemo, useState } from 'react';
import Lightbox, { IconButton, useLightboxState } from 'yet-another-react-lightbox';
import Counter from 'yet-another-react-lightbox/plugins/counter';
import Thumbnails from 'yet-another-react-lightbox/plugins/thumbnails';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';

import 'yet-another-react-lightbox/styles.css';
import 'yet-another-react-lightbox/plugins/counter.css';
import 'yet-another-react-lightbox/plugins/thumbnails.css';
import './lightbox.css';

import { useMediaCopy } from '../../i18n';
import type { ImageLightboxProps, LightboxImage } from '../types';

declare module 'yet-another-react-lightbox' {
  interface Labels {
    /** Title of the SAVE button this widget adds to the toolbar. */
    Save?: string;
  }
}

/** Double-click: one stop in, the next one out. */
const ZOOM = {
  doubleClickMaxStops: 1,
  zoomInMultiplier: 2.5,
  maxZoomPixelRatio: 3,
  scrollToZoom: true,
} as const;

export function ImageLightbox({
  images,
  open,
  index = 0,
  onClose,
  onIndexChange,
  thumbnails = true,
  copy,
}: ImageLightboxProps) {
  const labels = useMediaCopy(copy);
  const [zoomed, setZoomed] = useState(false);

  const slides = useMemo(
    () =>
      images.map((image) => ({
        src: image.src,
        alt: image.name,
        width: image.width,
        height: image.height,
      })),
    [images],
  );

  const handleView = useCallback(
    ({ index: next }: { index: number }) => onIndexChange?.(next),
    [onIndexChange],
  );

  return (
    <Lightbox
      open={open}
      close={onClose}
      index={index}
      slides={slides}
      className={zoomed ? 'dj-lightbox dj-lightbox--zoomed' : 'dj-lightbox'}
      plugins={thumbnails && slides.length > 1 ? [Counter, Thumbnails, Zoom] : [Counter, Zoom]}
      zoom={ZOOM}
      carousel={{ finite: true, preload: 2 }}
      animation={{ swipe: 250 }}
      controller={{ closeOnBackdropClick: true, closeOnPullDown: true }}
      thumbnails={{ position: 'bottom', vignette: false, border: 0, gap: 8 }}
      labels={{
        Close: labels.close,
        Next: labels.next,
        Previous: labels.previous,
        Save: labels.download,
        'Zoom in': labels.zoomIn,
        'Zoom out': labels.zoomOut,
      }}
      on={{ view: handleView, zoom: ({ zoom }) => setZoomed(zoom > 1.01) }}
      toolbar={{
        buttons: [<SaveButton key="save" images={images} />, 'close'],
      }}
      render={slides.length > 1 ? undefined : { buttonPrev: () => null, buttonNext: () => null }}
    />
  );
}

/**
 * Saves the slide on screen. `download` is honoured only for a same-origin
 * address, so a picture shown from a CDN is saved from `downloadSrc` when the
 * host has one.
 */
function SaveButton({ images }: { images: LightboxImage[] }) {
  const { currentIndex } = useLightboxState();
  const image = images[currentIndex];
  const save = useCallback(() => {
    if (!image) return;
    const link = document.createElement('a');
    link.href = image.downloadSrc ?? image.src;
    link.download = image.name;
    link.rel = 'noopener';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }, [image]);

  if (!image) return null;
  return (
    <IconButton
      label="Save"
      icon={() => null}
      renderIcon={() => <Download className="yarl__icon" aria-hidden />}
      onClick={save}
    />
  );
}
