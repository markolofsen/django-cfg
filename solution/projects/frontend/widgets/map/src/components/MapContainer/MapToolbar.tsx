'use client'

import { Layers, LocateFixed, MapPin, Maximize2, Mountain, RotateCcw, Search, X } from 'lucide-react'
import { cn } from '@djangocfg/ui-core/lib'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem,
  DropdownMenuTrigger,
  TooltipHint,
} from '@djangocfg/ui-core/components'

import { MAP_STYLE_LABELS } from '../../styles'
import type { MapStyleKey } from '../../types'
import { CompassChip } from '../CompassChip'
import { MAP_CONTROL_CLASS } from './constants'
import type { GeolocateState } from './GeolocateHandle'

/**
 * Map controls — one icon-only toolbar, top-right (Google-Maps style). All
 * chips are a uniform 36×36 square; labels live in tooltips (shown on the LEFT
 * so they never spill off the map's right edge). Sits above the scroll-lock
 * overlay so it stays clickable.
 *
 * The `data-map-control` attribute is load-bearing: the scroll-protection
 * re-lock skips clicks inside it.
 */
export function MapToolbar({
  onClose,
  fullscreenButton,
  fullscreenLabel,
  onFullscreenOpen,
  basemapSwitcher,
  basemapOptions,
  basemapLabel,
  activeKey,
  onBasemapPick,
  terrainButton,
  terrainLabel,
  terrainOn,
  onTerrainToggle,
  compassButton,
  isOriented,
  compassLabel,
  bearing,
  onResetNorth,
  geolocate,
  geolocateLabel,
  geolocateState,
  onGeolocateTrigger,
  geocoder,
  geocoderOpen,
  onGeocoderToggle,
  externalMapsUrl,
  externalMapsLabel,
  showResetButton,
  hasViewportChanged,
  onResetToInitial,
}: {
  onClose: (() => void) | undefined
  fullscreenButton: boolean
  fullscreenLabel: string
  onFullscreenOpen: () => void
  basemapSwitcher: boolean
  basemapOptions: MapStyleKey[]
  basemapLabel: string
  activeKey: MapStyleKey | undefined
  onBasemapPick: (key: string) => void
  terrainButton: boolean
  terrainLabel: string
  terrainOn: boolean
  onTerrainToggle: () => void
  compassButton: boolean
  isOriented: boolean
  compassLabel: string
  bearing: number
  onResetNorth: () => void
  geolocate: boolean
  geolocateLabel: string
  geolocateState: GeolocateState
  onGeolocateTrigger: () => void
  geocoder: boolean
  geocoderOpen: boolean
  onGeocoderToggle: () => void
  externalMapsUrl: string | undefined
  externalMapsLabel: string
  showResetButton: boolean
  hasViewportChanged: boolean
  onResetToInitial: () => void
}) {
  return (
    <div
      data-map-control
      className="absolute top-3 right-3 z-20 flex flex-col items-end gap-2"
    >
      {onClose && (
        <TooltipHint tooltip={{ content: 'Close', side: 'left' }}>
          <button
            type="button"
            onClick={onClose}
            aria-label="Close map"
            className={cn(MAP_CONTROL_CLASS, 'w-9 h-9')}
          >
            <X className="w-4 h-4" aria-hidden="true" />
          </button>
        </TooltipHint>
      )}

      {fullscreenButton && (
        <TooltipHint tooltip={{ content: fullscreenLabel, side: 'left' }}>
          <button
            type="button"
            onClick={onFullscreenOpen}
            aria-label={fullscreenLabel}
            className={cn(MAP_CONTROL_CLASS, 'w-9 h-9')}
          >
            <Maximize2 className="w-4 h-4" aria-hidden="true" />
          </button>
        </TooltipHint>
      )}

      {/* Search (geocoder) — Google-Maps-style magnifier that toggles an
          on-map autocomplete (rendered top-left by MapInner). Tinted
          text-primary while open; aria-pressed mirrors the open state. */}
      {geocoder && (
        <TooltipHint tooltip={{ content: geocoderOpen ? 'Close search' : 'Search', side: 'left' }}>
          <button
            type="button"
            onClick={onGeocoderToggle}
            aria-label="Search the map"
            aria-pressed={geocoderOpen}
            className={cn(
              MAP_CONTROL_CLASS,
              'w-9 h-9',
              geocoderOpen && 'bg-popover text-primary',
            )}
          >
            <Search className="w-4 h-4" aria-hidden="true" />
          </button>
        </TooltipHint>
      )}

      {/* Basemap switcher (Google-Maps "Layers") — pick the map style at
          runtime. Hidden if disabled or there's nothing to switch to. */}
      {basemapSwitcher && basemapOptions.length > 1 && (
        <DropdownMenu>
          <TooltipHint tooltip={{ content: basemapLabel, side: 'left' }}>
            <DropdownMenuTrigger
              aria-label={basemapLabel}
              className={cn(MAP_CONTROL_CLASS, 'w-9 h-9')}
            >
              <Layers className="w-4 h-4" aria-hidden="true" />
            </DropdownMenuTrigger>
          </TooltipHint>
          <DropdownMenuContent align="end" side="left" className="min-w-36">
            <DropdownMenuRadioGroup
              value={activeKey ?? ''}
              onValueChange={onBasemapPick}
            >
              {basemapOptions.map((key) => (
                <DropdownMenuRadioItem key={key} value={key}>
                  {MAP_STYLE_LABELS[key]}
                </DropdownMenuRadioItem>
              ))}
            </DropdownMenuRadioGroup>
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      {/* 3D terrain toggle (Mountain) — adds the free DEM terrain +
          hillshade and pitches the camera in so it reads as 3D. */}
      {terrainButton && (
        <TooltipHint tooltip={{ content: terrainLabel, side: 'left' }}>
          <button
            type="button"
            onClick={onTerrainToggle}
            aria-label={terrainLabel}
            aria-pressed={terrainOn}
            className={cn(
              MAP_CONTROL_CLASS,
              'w-9 h-9',
              terrainOn && 'bg-popover text-primary',
            )}
          >
            <Mountain className="w-4 h-4" aria-hidden="true" />
          </button>
        </TooltipHint>
      )}

      {/* Compass — shows only when rotated/tilted (gated here); the chip's
          needle reflects the bearing and tints accent as an off-north cue,
          click eases back to north-up + top-down (Google style). */}
      {compassButton && isOriented && (
        <CompassChip
          bearing={bearing}
          oriented={isOriented}
          onReset={onResetNorth}
          label={compassLabel}
        />
      )}

      {/* Locate me (GPS) — drives maplibre's hidden GeolocateControl via
          trigger(). Tinted text-primary while actively following (like the
          terrain chip); muted/disabled look on permission-denied or
          unavailable, with a tooltip explaining it. Opt-in only. */}
      {geolocate && (
        <TooltipHint tooltip={{ content: geolocateState === 'error' ? 'Location unavailable — check permission' : geolocateLabel, side: 'left' }}>
          <button
            type="button"
            onClick={onGeolocateTrigger}
            aria-label={geolocateLabel}
            aria-pressed={geolocateState === 'active'}
            className={cn(
              MAP_CONTROL_CLASS,
              'w-9 h-9',
              geolocateState === 'active' && 'bg-popover text-primary',
              geolocateState === 'error' && 'text-muted-foreground',
            )}
          >
            <LocateFixed className="w-4 h-4" aria-hidden="true" />
          </button>
        </TooltipHint>
      )}

      {externalMapsUrl && (
        <TooltipHint tooltip={{ content: externalMapsLabel, side: 'left' }}>
          <a
            href={externalMapsUrl}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={externalMapsLabel}
            className={cn(MAP_CONTROL_CLASS, 'w-9 h-9')}
          >
            <MapPin className="w-4 h-4" aria-hidden="true" />
          </a>
        </TooltipHint>
      )}

      {showResetButton && hasViewportChanged && (
        <TooltipHint tooltip={{ content: 'Reset to the initial view', side: 'left' }}>
          <button
            type="button"
            onClick={onResetToInitial}
            aria-label="Reset map view"
            className={cn(MAP_CONTROL_CLASS, 'w-9 h-9')}
          >
            <RotateCcw className="w-4 h-4" aria-hidden="true" />
          </button>
        </TooltipHint>
      )}
    </div>
  )
}
