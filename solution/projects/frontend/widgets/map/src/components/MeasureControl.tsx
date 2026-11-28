'use client'

import { memo } from 'react'
import { Pentagon, Ruler, Spline, Trash2 } from 'lucide-react'
import { cn } from '@djangocfg/ui-core/lib'
import {
  TooltipHint,
} from '@djangocfg/ui-core/components'

import { MapSource, MapLayer } from './MapSource'
import { useMeasure, type MeasureMode } from '../hooks/useMeasure'
import { createLineLayer } from '../layers/line'
import { createPolygonLayer, createPolygonOutlineLayer } from '../layers/polygon'

export interface MeasureControlProps {
  /** Corner the control toolbar is pinned to. @default 'top-left' */
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  /** Mode the tool starts in. @default 'distance' */
  defaultMode?: MeasureMode
  /** Accent color for the measure overlay (line stroke / polygon fill). */
  accentColor?: string
  className?: string
}

const positionStyles: Record<
  NonNullable<MeasureControlProps['position']>,
  React.CSSProperties
> = {
  'top-left': { top: 12, left: 12 },
  'top-right': { top: 12, right: 12 },
  'bottom-left': { bottom: 12, left: 12 },
  'bottom-right': { bottom: 12, right: 12 },
}

// Same floating-chrome chip style MapContainer uses for its map controls
// (semantic `popover` tokens — reads like maplibre's own controls in light
// and dark themes). Kept in sync with MAP_CONTROL_CLASS there.
const MAP_CONTROL_CLASS = cn(
  'inline-flex items-center justify-center rounded-lg',
  'bg-popover/95 text-popover-foreground backdrop-blur-sm shadow-sm border border-border',
  'hover:bg-popover transition-colors',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
)

const SOURCE_ID = 'measure-source'

/**
 * On-map measure control — click to measure a path's length (km) or a
 * polygon's area (m²/km²), with a live total readout and a clear button.
 *
 * Drop it as a child of `MapContainer` / `MapView` (inside the
 * `MapProvider`), alongside `MapLegend` / `LayerSwitcher`:
 *
 * ```tsx
 * <MapContainer initialViewport={...}>
 *   <MeasureControl />
 * </MapContainer>
 * ```
 *
 * Renders the measure geometry through the existing `createLineLayer` /
 * `createPolygonLayer` factories — no bespoke layer code.
 */
function MeasureControlComponent({
  position = 'top-left',
  defaultMode = 'distance',
  accentColor = '#f97316',
  className = '',
}: MeasureControlProps) {
  const { mode, setMode, geojson, totalLabel, points, clear, active, setActive } =
    useMeasure(defaultMode)

  const hasMeasurement = points.length > 0

  return (
    <>
      {/* Overlay geometry — reuses the existing line / polygon factories. */}
      <MapSource id={SOURCE_ID} data={geojson}>
        {mode === 'area' ? (
          <>
            <MapLayer
              {...createPolygonLayer(`${SOURCE_ID}-fill`, SOURCE_ID, {
                fillColor: accentColor,
                fillOpacity: 0.2,
              })}
            />
            <MapLayer
              {...createPolygonOutlineLayer(`${SOURCE_ID}-outline`, SOURCE_ID, {
                color: accentColor,
                width: 2,
              })}
            />
          </>
        ) : (
          <MapLayer
            {...createLineLayer({
              id: `${SOURCE_ID}-line`,
              sourceId: SOURCE_ID,
              color: accentColor,
              width: 3,
            })}
          />
        )}
      </MapSource>

      {/* Toolbar — a single popover chip, same chrome as the map controls. */}
      <div
        className={cn(
          'absolute z-20 flex items-center gap-1 p-1',
          MAP_CONTROL_CLASS,
          'rounded-lg',
          className,
        )}
        style={positionStyles[position]}
        role="group"
        aria-label="Measure tool"
      >
        <TooltipHint tooltip={{ content: active ? 'Stop measuring' : 'Measure', side: 'bottom' }}>
          <button
            type="button"
            onClick={() => setActive(!active)}
            aria-pressed={active}
            aria-label={active ? 'Stop measuring' : 'Start measuring'}
            className={cn(
              'inline-flex h-8 w-8 items-center justify-center rounded-md transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              active
                ? 'bg-primary text-primary-foreground'
                : 'hover:bg-accent hover:text-accent-foreground',
            )}
          >
            <Ruler className="h-4 w-4" aria-hidden="true" />
          </button>
        </TooltipHint>

        {/* Mode switch — distance / area. */}
        <TooltipHint tooltip={{ content: 'Distance', side: 'bottom' }}>
          <button
            type="button"
            onClick={() => setMode('distance')}
            aria-pressed={mode === 'distance'}
            aria-label="Measure distance"
            className={cn(
              'inline-flex h-8 w-8 items-center justify-center rounded-md transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              mode === 'distance'
                ? 'bg-accent text-accent-foreground'
                : 'hover:bg-accent hover:text-accent-foreground',
            )}
          >
            <Spline className="h-4 w-4" aria-hidden="true" />
          </button>
        </TooltipHint>

        <TooltipHint tooltip={{ content: 'Area', side: 'bottom' }}>
          <button
            type="button"
            onClick={() => setMode('area')}
            aria-pressed={mode === 'area'}
            aria-label="Measure area"
            className={cn(
              'inline-flex h-8 w-8 items-center justify-center rounded-md transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              mode === 'area'
                ? 'bg-accent text-accent-foreground'
                : 'hover:bg-accent hover:text-accent-foreground',
            )}
          >
            <Pentagon className="h-4 w-4" aria-hidden="true" />
          </button>
        </TooltipHint>

        {/* Live total readout. */}
        <span
          className="px-2 text-xs font-medium tabular-nums"
          aria-live="polite"
          aria-label={`Measured ${mode}: ${totalLabel}`}
        >
          {totalLabel}
        </span>

        {/* Clear. */}
        <TooltipHint tooltip={{ content: 'Clear', side: 'bottom' }}>
          <button
            type="button"
            onClick={clear}
            disabled={!hasMeasurement}
            aria-label="Clear measurement"
            className={cn(
              'inline-flex h-8 w-8 items-center justify-center rounded-md transition-colors',
              'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
              'hover:bg-accent hover:text-accent-foreground',
              'disabled:pointer-events-none disabled:opacity-40',
            )}
          >
            <Trash2 className="h-4 w-4" aria-hidden="true" />
          </button>
        </TooltipHint>
      </div>
    </>
  )
}

export const MeasureControl = memo(MeasureControlComponent)
