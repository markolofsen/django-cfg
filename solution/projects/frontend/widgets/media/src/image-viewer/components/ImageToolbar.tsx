'use client';

/**
 * ImageToolbar - Floating toolbar for image controls
 */

import { useMemo, type ReactNode } from 'react';
import { ZoomIn, ZoomOut, RotateCw, FlipHorizontal, FlipVertical, Maximize2, Expand } from 'lucide-react';
import { useControls } from 'react-zoom-pan-pinch';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  TooltipHint,
} from '@djangocfg/ui-core/components';
import { useMediaCopy } from '../../i18n';
import { cn } from '@djangocfg/ui-core/lib';
import { ZOOM_PRESETS } from '../utils';
import type { ImageToolbarProps } from '../types';

// =============================================================================
// COMPONENT
// =============================================================================

// The toolbar floats over the image, whose brightness is unknown and
// unrelated to the host theme. A theme-bound `bg-background` surface
// would clash with a dark photo (white slab) or a light photo in dark
// mode. A fixed dark-glass overlay with light icons stays readable on
// any content — the same model the gallery nav arrows and media
// players use.
const TB_BUTTON =
  'inline-flex items-center justify-center rounded-md text-white/90 ' +
  'transition-colors hover:bg-white/15 hover:text-white ' +
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70 ' +
  'disabled:opacity-40 disabled:pointer-events-none';

// Small helper so each icon button shares the same Tooltip wrapper +
// accessibility shape (visible tooltip on hover/focus, aria-label for AT).
function TbIconButton({
  label,
  onClick,
  className,
  children,
}: {
  label: string;
  onClick: () => void;
  className?: string;
  children: ReactNode;
}) {
  return (
    <TooltipHint tooltip={{ content: label, side: 'top' }}>
      <button
        type="button"
        aria-label={label}
        onClick={onClick}
        className={cn(TB_BUTTON, 'h-7 w-7', className)}
      >
        {children}
      </button>
    </TooltipHint>
  );
}

export function ImageToolbar({
  scale,
  transform,
  onRotate,
  onFlipH,
  onFlipV,
  onZoomPreset,
  onExpand,
  copy,
}: ImageToolbarProps) {
  const { zoomIn, zoomOut, resetTransform } = useControls();
  const labels = useMediaCopy(copy);

  const zoomLabel = useMemo(() => {
    const percent = Math.round(scale * 100);
    return `${percent}%`;
  }, [scale]);

  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-0.5 bg-black/60 backdrop-blur-sm border border-white/10 rounded-lg p-1 shadow-lg">
      {/* Zoom controls */}
      <TbIconButton label={labels.zoomOut} onClick={() => zoomOut()}>
        <ZoomOut className="h-3.5 w-3.5" />
      </TbIconButton>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            className={cn(TB_BUTTON, 'h-7 px-2 min-w-[52px] font-mono text-xs')}
          >
            {zoomLabel}
          </button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="center" className="min-w-[80px]">
          {ZOOM_PRESETS.map((preset) => (
            <DropdownMenuItem
              key={preset.label}
              onClick={() => onZoomPreset(preset.value)}
              className="text-xs justify-center"
            >
              {preset.label}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <TbIconButton label={labels.zoomIn} onClick={() => zoomIn()}>
        <ZoomIn className="h-3.5 w-3.5" />
      </TbIconButton>

      <div className="w-px h-4 bg-white/20 mx-1" />

      {/* Fit to view */}
      <TbIconButton label={labels.fitToView} onClick={() => resetTransform()}>
        <Maximize2 className="h-3.5 w-3.5" />
      </TbIconButton>

      <div className="w-px h-4 bg-white/20 mx-1" />

      {/* Transform controls */}
      <TbIconButton
        label={labels.flipHorizontal}
        onClick={onFlipH}
        className={transform.flipH ? 'bg-white/20 text-white' : undefined}
      >
        <FlipHorizontal className="h-3.5 w-3.5" />
      </TbIconButton>

      <TbIconButton
        label={labels.flipVertical}
        onClick={onFlipV}
        className={transform.flipV ? 'bg-white/20 text-white' : undefined}
      >
        <FlipVertical className="h-3.5 w-3.5" />
      </TbIconButton>

      <TbIconButton label={labels.rotate} onClick={onRotate}>
        <RotateCw className="h-3.5 w-3.5" />
      </TbIconButton>

      {transform.rotation !== 0 && (
        <span className="text-[10px] text-white/60 font-mono pl-1">
          {transform.rotation}°
        </span>
      )}

      {onExpand && (
        <>
          <div className="w-px h-4 bg-white/20 mx-1" />
          <TbIconButton label={labels.fullscreen} onClick={onExpand}>
            <Expand className="h-3.5 w-3.5" />
          </TbIconButton>
        </>
      )}
    </div>
  );
}
