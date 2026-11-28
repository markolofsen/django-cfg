'use client';

/**
 * ImageViewer - Image viewer with zoom, pan, rotate, flip, gallery navigation
 *
 * Two presentations share one engine (react-zoom-pan-pinch):
 * - Embedded (default): checkerboard canvas + editing toolbar (zoom presets,
 *   rotate, flip, expand-to-fullscreen).
 * - Lightbox (`lightbox` / `inDialog`): macOS Quick-Look-grade fullscreen —
 *   clean dark backdrop, idle-fading floating chrome, no rotate/flip slab.
 *
 * Gesture model (macOS-native):
 * - Trackpad pinch arrives as wheel events with `ctrlKey=true`; the library's
 *   `smooth` path maps `|deltaY|` to the zoom magnitude so scale tracks the
 *   gesture 1:1. We raise `smoothStep` (see WHEEL_SMOOTH_STEP) so a real pinch
 *   reaches a meaningful zoom in one motion.
 * - Zoom is anchored to the FOCAL POINT (cursor / pinch midpoint) — the point
 *   under the fingers stays put — handled natively by the library.
 * - Pan by drag when zoomed; double-click/tap toggles fit ↔ zoom toward the
 *   point; keyboard +/-/0 and arrows (pan when zoomed, gallery nav at fit).
 */

import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { ImageIcon, AlertCircle, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';
import {
  TransformWrapper,
  TransformComponent,
  type ReactZoomPanPinchRef,
} from 'react-zoom-pan-pinch';
import { cn, Dialog, DialogContent, DialogTitle, Alert, AlertDescription, TooltipHint } from '@djangocfg/ui-core';
import { useMediaCopy } from '../../i18n';
import { useHotkey } from '@djangocfg/ui-core/hooks';

import { ImageToolbar } from './ImageToolbar';
import { ImageInfo } from './ImageInfo';
import { LightboxChrome } from './LightboxChrome';
import { useImageTransform, useImageLoading, useIdleChrome } from '../hooks';
import {
  KEYBOARD_PAN_STEP,
  MIN_ZOOM,
  MAX_ZOOM,
  WHEEL_SMOOTH_STEP,
  PINCH_STEP,
  DOUBLE_CLICK_ZOOM,
  FIT_EPSILON,
} from '../utils';
import type { ImageViewerProps } from '../types';

// =============================================================================
// COMPONENT
// =============================================================================

export function ImageViewer({
  images,
  initialIndex = 0,
  inDialog = false,
  lightbox = false,
  onRequestClose,
  autoFocus = false,
  fitScale = 1,
  copy,
}: ImageViewerProps) {
  const labels = useMediaCopy(copy);

  // `lightbox` implies the in-dialog presentation.
  const isLightbox = lightbox || inDialog;

  // Cap the at-rest image size to `fitScale` of the viewport in the lightbox so
  // it opens with a margin instead of edge-to-edge. Clamp to a sane range; a
  // value of 1 (the default) is a no-op (falls back to the max-w/h-full class).
  const fit = Math.min(1, Math.max(0.1, fitScale));
  const fitStyle: React.CSSProperties | undefined =
    isLightbox && fit < 1
      ? { maxWidth: `${fit * 100}%`, maxHeight: `${fit * 100}%` }
      : undefined;

  const [currentIndex, setCurrentIndex] = useState(() =>
    Math.max(0, Math.min(initialIndex, images.length - 1))
  );

  // Reset index when initialIndex changes (e.g. opening different image)
  useEffect(() => {
    setCurrentIndex(Math.max(0, Math.min(initialIndex, images.length - 1)));
  }, [initialIndex, images.length]);

  const current = images[currentIndex];
  const hasMultiple = images.length > 1;

  const [scale, setScale] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [loadError, setLoadError] = useState(false);
  const [imgDecoded, setImgDecoded] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);
  const controlsRef = useRef<ReactZoomPanPinchRef | null>(null);
  const atRest = Math.abs(scale - 1) < FIT_EPSILON;
  const imgRef = useRef<HTMLImageElement>(null);

  // Idle-fading chrome (lightbox only). Pointer movement over the canvas keeps
  // the controls visible; resting for CHROME_IDLE_MS fades them out.
  const { active: chromeActive, onActivity, setPinned } = useIdleChrome(isLightbox);

  const {
    src,
    lqip,
    isFullyLoaded,
    useProgressiveLoading,
    error,
    hasContent,
  } = useImageLoading({
    content: current?.content ?? '',
    mimeType: current?.file.mimeType,
    src: current?.src,
  });

  // Save the image the viewer RESOLVED, not the prop: `src` is already a blob
  // URL when the caller passed bytes, so one anchor covers both a hosted URL
  // and an in-memory image without branching on which arrived.
  //
  // A generated picture is served as /api/admin/attachments/<sha256> — a path
  // with no extension — so the store's file name is the only source of a
  // meaningful one, and the hash is a poor thing to hand a user's Downloads
  // folder. Undefined without a src: a control that cannot act is worse absent.
  // `downloadSrc` wins when the host supplied one: `download` is honoured only
  // for a same-origin address, so a picture displayed from a CDN must be SAVED
  // from wherever this page can serve the same bytes. The resolved `src` is the
  // fallback and covers the in-memory case, where it is already a blob URL.
  const saveFrom = current?.downloadSrc ?? src;
  const handleDownload = useMemo(() => {
    if (!saveFrom) return undefined;
    return () => {
      const link = document.createElement('a');
      link.href = saveFrom;
      link.download = current?.file.name ?? 'image';
      link.rel = 'noopener';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };
  }, [saveFrom, current?.file.name]);

  // Reset per-source load flags whenever the source changes.
  //
  // Race guard (first-open stuck on "Loading…"): the `<img onLoad>` handler is
  // the ONLY thing that clears `imgDecoded`, but the browser can finish
  // decoding — and fire `load` — BEFORE React commits the element and attaches
  // that handler (a same-origin blob/attachment URL that resolves synchronously,
  // or an already-cached image). The event is then missed and the spinner hangs
  // forever; reopening "fixes" it only because the fresh mount happens to win
  // the race. So after resetting, synchronously reconcile against the live img:
  // if it's already `complete` with real pixels, mark it decoded now instead of
  // waiting for an onLoad that already fired.
  useEffect(() => {
    setLoadError(false);
    const img = imgRef.current;
    if (img && img.complete && img.naturalWidth > 0) {
      setImgDecoded(true);
    } else {
      setImgDecoded(false);
    }
  }, [src]);

  const { transform, rotate, flipH, flipV, transformStyle } = useImageTransform({
    resetKey: current?.file.path ?? '',
  });

  // Double-click / double-tap: zoom to the pointer from fit, back to fit from
  // anywhere else. The point under the pointer stays put (focal-point zoom).
  const handleDoubleClick = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    const controls = controlsRef.current;
    const wrapper = controls?.instance.wrapperComponent;
    if (!controls || !wrapper) return;
    const { scale: current, positionX, positionY } = controls.instance.transformState;
    if (Math.abs(current - 1) >= FIT_EPSILON) {
      controls.resetTransform(200);
      return;
    }
    const rect = wrapper.getBoundingClientRect();
    const px = event.clientX - rect.left;
    const py = event.clientY - rect.top;
    const ratio = DOUBLE_CLICK_ZOOM / current;
    controls.setTransform(px - (px - positionX) * ratio, py - (py - positionY) * ratio, DOUBLE_CLICK_ZOOM, 200);
  }, []);

  const handleZoomPreset = useCallback((value: number | 'fit') => {
    const controls = controlsRef.current;
    if (!controls) return;
    if (value === 'fit') {
      controls.resetTransform();
      return;
    }
    // Anchor preset zoom to the canvas center instead of the top-left origin
    const el = controls.instance.wrapperComponent;
    if (el) {
      const cx = el.offsetWidth / 2;
      const cy = el.offsetHeight / 2;
      const x = cx - cx * value;
      const y = cy - cy * value;
      controls.setTransform(x, y, value);
    } else {
      controls.setTransform(0, 0, value);
    }
  }, []);

  const handleExpand = useCallback(() => setDialogOpen(true), []);

  // Reset zoom/pan to fit whenever the gallery image changes — a fresh image
  // should never inherit the previous one's pan offset.
  const goTo = useCallback((next: number) => {
    setCurrentIndex(next);
    controlsRef.current?.resetTransform();
  }, []);

  const prev = useCallback(() =>
    goTo((currentIndex - 1 + images.length) % images.length),
    [goTo, currentIndex, images.length]
  );

  const next = useCallback(() =>
    goTo((currentIndex + 1) % images.length),
    [goTo, currentIndex, images.length]
  );

  // Pan the image by a fixed offset (arrow keys)
  const panBy = useCallback((dx: number, dy: number) => {
    const controls = controlsRef.current;
    if (!controls) return false;
    const { positionX, positionY, scale: s } = controls.instance.transformState;
    // Only pan when the image is zoomed in — otherwise it cannot move
    if (s <= 1) return false;
    controls.setTransform(positionX + dx, positionY + dy, s);
    return true;
  }, []);

  // Declarative autoFocus: focus the container once on mount. Pair with
  // `key={src}` upstream for per-source focus reset.
  useEffect(() => {
    if (!autoFocus) return;
    containerRef.current?.focus({ preventScroll: true });
  }, [autoFocus]);

  // Keyboard: zoom / rotate / pan (only when container focused)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!containerRef.current?.contains(document.activeElement) &&
          document.activeElement !== containerRef.current) return;
      const controls = controlsRef.current;
      if (!controls) return;
      switch (e.key) {
        case '+': case '=': e.preventDefault(); controls.zoomIn(); break;
        case '-': case '_': e.preventDefault(); controls.zoomOut(); break;
        case '0': e.preventDefault(); controls.resetTransform(); break;
        case 'r': case 'R':
          // Rotate is an editing affordance — embedded mode only.
          if (!isLightbox && !e.metaKey && !e.ctrlKey) { e.preventDefault(); rotate(); }
          break;
        case 'Escape':
          if (isLightbox && onRequestClose) { e.preventDefault(); onRequestClose(); }
          break;
        // Arrow keys pan only when zoomed in. While at fit scale they
        // fall through to gallery navigation (handled by useHotkey).
        case 'ArrowUp': if (panBy(0, KEYBOARD_PAN_STEP)) e.preventDefault(); break;
        case 'ArrowDown': if (panBy(0, -KEYBOARD_PAN_STEP)) e.preventDefault(); break;
        case 'ArrowLeft': if (panBy(KEYBOARD_PAN_STEP, 0)) e.preventDefault(); break;
        case 'ArrowRight': if (panBy(-KEYBOARD_PAN_STEP, 0)) e.preventDefault(); break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [rotate, panBy, isLightbox, onRequestClose]);

  // Keyboard: gallery navigation (global, only while not zoomed in so it
  // never competes with arrow-key panning)
  useHotkey('ArrowLeft', prev, {
    enabled: hasMultiple && scale <= 1,
    preventDefault: true,
  });
  useHotkey('ArrowRight', next, {
    enabled: hasMultiple && scale <= 1,
    preventDefault: true,
  });

  if (!current) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-2 bg-muted/30">
        <ImageIcon className="w-12 h-12 text-muted-foreground/50" />
        <p className="text-sm text-muted-foreground">{labels.noImage}</p>
      </div>
    );
  }

  if (error || loadError) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-3 bg-muted/30 p-4">
        <AlertCircle className="w-12 h-12 text-destructive/70" />
        <Alert variant="destructive" className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error || labels.failedToLoad}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!hasContent) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center gap-2 bg-muted/30">
        <ImageIcon className="w-12 h-12 text-muted-foreground/50" />
        <p className="text-sm text-muted-foreground">{labels.noImage}</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      tabIndex={0}
      // `group`, not `img`: this element is the viewer's keyboard scope (zoom,
      // rotate, gallery hotkeys) and in the lightbox it CONTAINS the save and
      // close controls. `img` is a leaf role, so focusable descendants inside
      // it are an a11y violation and a screen reader stops at the label without
      // reaching the buttons. The picture itself is the inner <img>, which
      // carries its own alt.
      role="group"
      aria-label={current.file.name}
      onMouseMove={isLightbox ? onActivity : undefined}
      className={cn(
        'flex-1 h-full relative overflow-hidden outline-none',
        'focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-inset',
        isLightbox
          // Lightbox: a deep, slightly translucent vibrancy backdrop. The
          // saturate+blur is the macOS Quick Look recipe — the page behind
          // the dialog's scrim bleeds through softly so the image floats.
          ? cn(
              '[background-color:color-mix(in_oklab,#000_82%,transparent)]',
              'backdrop-blur-2xl backdrop-saturate-150',
            )
          // Embedded: the classic transparency checkerboard.
          : cn(
              'bg-[length:16px_16px]',
              '[background-color:color-mix(in_oklab,var(--muted)_20%,transparent)]',
              '[background-image:linear-gradient(45deg,color-mix(in_oklab,var(--muted)_40%,transparent)_25%,transparent_25%),linear-gradient(-45deg,color-mix(in_oklab,var(--muted)_40%,transparent)_25%,transparent_25%),linear-gradient(45deg,transparent_75%,color-mix(in_oklab,var(--muted)_40%,transparent)_75%),linear-gradient(-45deg,transparent_75%,color-mix(in_oklab,var(--muted)_40%,transparent)_75%)]',
              '[background-position:0_0,0_8px,8px_-8px,-8px_0px]',
            ),
      )}
    >
      {/* Dimensions badge — embedded only (lightbox keeps chrome minimal). */}
      {!isLightbox && src && <ImageInfo src={src} />}

      {useProgressiveLoading && !isFullyLoaded && (
        <div className="absolute top-3 left-3 z-10 px-2 py-1 bg-black/60 backdrop-blur-sm border border-white/10 rounded text-[10px] text-white/80 font-mono flex items-center gap-1.5">
          <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
          {labels.loading}
        </div>
      )}

      {/* Spinner while a non-progressive image is still decoding */}
      {!useProgressiveLoading && !imgDecoded && !loadError && (
        <div className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-2 pointer-events-none">
          <Loader2 className="w-8 h-8 text-muted-foreground/60 animate-spin" />
          <span className="text-xs text-muted-foreground">{labels.loading}</span>
        </div>
      )}

      <TransformWrapper
        initialScale={1}
        minScale={MIN_ZOOM}
        maxScale={MAX_ZOOM}
        centerOnInit
        centerZoomedOut
        // `smooth` (default) makes the wheel/trackpad zoom magnitude scale with
        // `|deltaY|`, i.e. 1:1 with the gesture. The raised `smoothStep` gives
        // a macOS trackpad pinch real reach in a single motion (the library's
        // 0.001 default felt dead). Focal-point anchoring is handled natively.
        smooth
        wheel={{ smoothStep: WHEEL_SMOOTH_STEP }}
        pinch={{ step: PINCH_STEP }}
        // The library's `toggle` zooms in only at scale === 1 exactly, so after
        // any zoom every double-click was another step OUT. Ours is handled in
        // `handleDoubleClick`: at rest zoom to the pointer, otherwise back to fit.
        doubleClick={{ disabled: true }}
        panning={{ velocityDisabled: false }}
        onTransformed={(ref, state) => {
          controlsRef.current = ref;
          // Avoid a re-render on every pan frame — only when zoom changes
          setScale((prev) => (prev === state.scale ? prev : state.scale));
        }}
        onInit={(ref) => { controlsRef.current = ref; }}
      >
        {/* Embedded editing toolbar (rotate/flip/expand) — not in the lightbox. */}
        {!isLightbox && (
          <ImageToolbar
            scale={scale}
            transform={transform}
            onRotate={rotate}
            onFlipH={flipH}
            onFlipV={flipV}
            onZoomPreset={handleZoomPreset}
            onExpand={!inDialog ? handleExpand : undefined}
          />
        )}

        <TransformComponent
          wrapperClass={cn(
            '!w-full !h-full',
            atRest ? 'cursor-zoom-in' : 'cursor-grab active:cursor-grabbing',
          )}
          wrapperProps={{ onDoubleClick: handleDoubleClick }}
          contentClass="!w-full !h-full flex items-center justify-center"
        >
          {/*
            Fill the TransformComponent content box so the children's
            `max-w-full / max-h-full` resolve against the actual viewport
            instead of the image's natural box. Without `w-full h-full`
            this wrapper shrink-fits the image, which collapses the
            max-* constraints and renders the image at intrinsic size —
            visible as cropping / half-height in tall containers.
          */}
          <div className="relative w-full h-full flex items-center justify-center">
            {useProgressiveLoading && lqip && !isFullyLoaded && (
              <img
                src={lqip}
                alt=""
                aria-hidden="true"
                className="absolute max-w-full max-h-full object-contain select-none"
                style={{ transform: transformStyle, filter: 'blur(20px)', transition: 'opacity 0.3s ease-out', opacity: isFullyLoaded ? 0 : 1, ...fitStyle }}
                draggable={false}
              />
            )}
            {src && (
              <img
                ref={imgRef}
                src={src}
                alt={current.file.name}
                className={cn(
                  'max-w-full max-h-full object-contain select-none',
                  // A soft drop shadow lifts the image off the dark lightbox
                  // backdrop (Preview / Photos do the same).
                  isLightbox && 'drop-shadow-[0_8px_40px_rgba(0,0,0,0.55)]',
                )}
                style={{
                  transform: transformStyle,
                  transition: 'transform 0.15s ease-out, opacity 0.3s ease-out',
                  opacity:
                    (useProgressiveLoading && !isFullyLoaded) || !imgDecoded ? 0 : 1,
                  ...fitStyle,
                }}
                draggable={false}
                onLoad={() => setImgDecoded(true)}
                onError={() => setLoadError(true)}
              />
            )}
          </div>
        </TransformComponent>
      </TransformWrapper>

      {/* Lightbox: restrained macOS-grade chrome that idle-fades. */}
      {isLightbox ? (
        <LightboxChrome
          active={chromeActive}
          index={currentIndex + 1}
          total={images.length}
          scale={scale}
          fileName={current.file.name}
          onPrev={prev}
          onNext={next}
          onClose={() => onRequestClose?.()}
          onDownload={handleDownload}
          onPinChange={setPinned}
          labels={{
            prev: labels.previous,
            next: labels.next,
            close: labels.close,
            download: labels.download,
          }}
        />
      ) : (
        hasMultiple && (
          // Embedded gallery nav (checkerboard canvas).
          <>
            <TooltipHint tooltip={{ content: labels.previous, side: 'right' }}>
              <button
                type="button"
                onClick={prev}
                aria-label={labels.previous}
                className="absolute left-2 top-1/2 -translate-y-1/2 z-10 bg-black/50 hover:bg-black/70 text-white rounded-full p-1.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
              >
                <ChevronLeft className="h-5 w-5" />
              </button>
            </TooltipHint>
            <TooltipHint tooltip={{ content: labels.next, side: 'left' }}>
              <button
                type="button"
                onClick={next}
                aria-label={labels.next}
                className="absolute right-2 top-1/2 -translate-y-1/2 z-10 bg-black/50 hover:bg-black/70 text-white rounded-full p-1.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white"
              >
                <ChevronRight className="h-5 w-5" />
              </button>
            </TooltipHint>
            <div className="absolute top-3 left-1/2 -translate-x-1/2 z-10 bg-black/60 backdrop-blur-sm border border-white/10 text-white/80 text-xs font-mono px-2 py-0.5 rounded-full pointer-events-none">
              {currentIndex + 1} / {images.length}
            </div>
          </>
        )
      )}

      {/* Embedded expand-to-fullscreen dialog (uses the lightbox presentation). */}
      {!inDialog && !lightbox && (
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent
            fullscreen
            closeButton={false}
            className="border-0 bg-transparent p-0 shadow-none"
          >
            <DialogTitle className="sr-only">{current.file.name}</DialogTitle>
            {dialogOpen && (
              <ImageViewer
                images={images}
                initialIndex={currentIndex}
                lightbox
                autoFocus
                onRequestClose={() => setDialogOpen(false)}
              />
            )}
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}
