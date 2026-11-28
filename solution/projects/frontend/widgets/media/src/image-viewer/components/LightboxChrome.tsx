'use client';

/**
 * LightboxChrome - Restrained, macOS-grade floating controls for the
 * fullscreen image lightbox.
 *
 * Design intent (Apple HIG / Quick Look / Preview):
 * - Minimal chrome: a single close affordance (top-right), prev/next only
 *   when there is more than one image, and one unobtrusive status pill
 *   (counter + live zoom %).
 * - Everything floats on liquid-glass and fades together when the pointer
 *   goes idle, reappearing on the slightest movement.
 * - No checkerboard, no rotate/flip slab — the image is the subject.
 */

import { ChevronLeft, ChevronRight, Download, X } from 'lucide-react';

import { cn } from '@djangocfg/ui-core/lib';

import { MiddleEllipsis } from './MiddleEllipsis';

interface LightboxChromeProps {
  /** Visible (recent pointer activity) vs faded (idle). */
  active: boolean;
  /** 1-based index for the counter. */
  index: number;
  total: number;
  /** Live zoom scale (1 = fit). The % pill only shows when zoomed in/out. */
  scale: number;
  fileName?: string;
  onPrev: () => void;
  onNext: () => void;
  onClose: () => void;
  /** Save the shown image. Undefined hides the control: a viewer with no
   *  resolved source has nothing to save, and a button that cannot act is
   *  worse than an absent one. */
  onDownload?: () => void;
  /** Pin chrome open while the pointer hovers a control. */
  onPinChange: (pinned: boolean) => void;
  labels: { prev: string; next: string; close: string; download: string };
}

// Liquid-glass circular control — light icon on translucent vibrancy so it
// stays legible over any photo (bright or dark) without a hard slab.
const GLASS_BTN =
  'glass-liquid pointer-events-auto inline-flex items-center justify-center ' +
  'rounded-full text-white/90 transition-[background-color,transform,opacity] ' +
  'hover:text-white hover:bg-white/15 active:scale-95 ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70';

export function LightboxChrome({
  active,
  index,
  total,
  scale,
  fileName,
  onPrev,
  onNext,
  onClose,
  onDownload,
  onPinChange,
  labels,
}: LightboxChromeProps) {
  const hasMultiple = total > 1;
  // Only surface the zoom pill once the image is meaningfully off fit — at
  // exactly fit (1.0) the % is noise.
  const zoomed = Math.abs(scale - 1) > 0.01;
  const zoomPct = `${Math.round(scale * 100)}%`;

  // Whole chrome layer fades as one. `pointer-events-none` on the layer means
  // the faded state never eats clicks meant for the image (pan/double-click).
  return (
    <div
      className={cn(
        'pointer-events-none absolute inset-0 z-20 transition-opacity duration-300 ease-out',
        active ? 'opacity-100' : 'opacity-0',
      )}
      onMouseEnter={() => onPinChange(true)}
      onMouseLeave={() => onPinChange(false)}
    >
      {/* Top bar: filename (left, whisper-quiet) + close (right).
          The chip caps its width and middle-truncates long names so the start
          and extension stay readable (Finder convention); `gap` + the pinned
          close button guarantee no overlap. */}
      <div className="absolute inset-x-0 top-0 flex items-start justify-between gap-3 p-3 sm:p-4">
        {fileName ? (
          <MiddleEllipsis
            text={fileName}
            className="glass-liquid pointer-events-auto max-w-[clamp(8rem,40vw,28rem)] rounded-full px-3 py-1.5 text-xs font-medium text-white/85"
          />
        ) : (
          <span aria-hidden />
        )}
        {/* Save sits beside close, not in the bottom pill: that pill is status
            (counter, zoom) and reads as output, while these two are what the
            viewer can DO. Close stays rightmost so its position is unchanged. */}
        <div className="flex items-center gap-2">
          {onDownload && (
            <button
              type="button"
              aria-label={labels.download}
              onClick={onDownload}
              className={cn(GLASS_BTN, 'h-9 w-9')}
            >
              <Download className="h-[18px] w-[18px]" />
            </button>
          )}
          <button
            type="button"
            aria-label={labels.close}
            onClick={onClose}
            className={cn(GLASS_BTN, 'h-9 w-9')}
          >
            <X className="h-[18px] w-[18px]" />
          </button>
        </div>
      </div>

      {/* Prev / next — edge-anchored, only when there is a gallery. */}
      {hasMultiple && (
        <>
          <button
            type="button"
            aria-label={labels.prev}
            onClick={onPrev}
            className={cn(GLASS_BTN, 'absolute left-3 top-1/2 h-11 w-11 -translate-y-1/2 sm:left-5')}
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <button
            type="button"
            aria-label={labels.next}
            onClick={onNext}
            className={cn(GLASS_BTN, 'absolute right-3 top-1/2 h-11 w-11 -translate-y-1/2 sm:right-5')}
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </>
      )}

      {/* Bottom status pill: counter + live zoom %. One quiet line. */}
      {(hasMultiple || zoomed) && (
        <div className="absolute inset-x-0 bottom-0 flex justify-center p-3 sm:p-4">
          <div className="glass-liquid flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium tabular-nums text-white/85">
            {hasMultiple && (
              <span>
                {index} / {total}
              </span>
            )}
            {hasMultiple && zoomed && <span className="h-3 w-px bg-white/25" />}
            {zoomed && <span className="font-mono text-white/70">{zoomPct}</span>}
          </div>
        </div>
      )}
    </div>
  );
}
