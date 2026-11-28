'use client'

import { memo, useCallback, type ReactNode } from 'react'
import { MapMarker } from './MapMarker'
import { MapPopup, type MapPopupProps } from './MapPopup'
import { MarkerCard } from './MarkerCard'
import { useMarkerCard } from '../hooks/useMarkerCard'
import type { MarkerData } from '../types'
import type { MarkerCard as MarkerCardType } from '../cards/types'

/** A marker plus its optional info-card data. */
export type MarkerWithCard = MarkerData & { card?: MarkerCardType }

export interface MapMarkersProps {
  /** Markers to render; any with a `card` (or when `renderCard` is set) opens a popup on click. */
  markers: MarkerWithCard[]
  /**
   * Custom card content. When provided it overrides the default `MarkerCard`
   * for the open marker. `close` dismisses the popup.
   */
  renderCard?: (marker: MarkerWithCard, close: () => void) => ReactNode
  /** Popup anchor — default `'bottom'` so the card sits ABOVE the pin. */
  cardAnchor?: MapPopupProps['anchor']
  /** Notified on every marker click (in addition to opening its card). */
  onMarkerClick?: (marker: MarkerWithCard) => void
  /** Default-pin color (ignored when a marker supplies `children`-style icon — N/A here). */
  color?: string
  /** Default-pin size in px. */
  size?: number
}

/**
 * MapMarkers — the "just works" marker layer. Renders one `MapMarker` per
 * entry and, on click, opens a `MapPopup` ANCHORED ABOVE the pin showing the
 * marker's `card` (default `MarkerCard`) or `renderCard` output. Selection is
 * driven by `useMarkerCard`, so only ONE card is open at a time and clicking
 * the same pin toggles it. Outside-click / Esc / the popup close button all
 * dismiss. Must live inside a `<MapProvider>` (a child of MapContainer/MapView,
 * like `MapLegend`).
 */
export const MapMarkers = memo(function MapMarkers({
  markers,
  renderCard,
  cardAnchor = 'bottom',
  onMarkerClick,
  color,
  size,
}: MapMarkersProps) {
  const { openId, toggle, close } = useMarkerCard()

  const handleClick = useCallback(
    (marker: MarkerData) => {
      toggle(marker.id)
      onMarkerClick?.(marker as MarkerWithCard)
    },
    [toggle, onMarkerClick]
  )

  const openMarker = openId ? markers.find((m) => m.id === openId) : undefined
  const hasCard = openMarker && (Boolean(openMarker.card) || Boolean(renderCard))

  return (
    <>
      {markers.map((marker) => (
        <MapMarker
          key={marker.id}
          marker={marker}
          onClick={handleClick}
          color={color}
          size={size}
          ariaLabel={
            (marker.card?.title as string | undefined) ??
            (marker.data?.label as string | undefined) ??
            `Map marker ${marker.id}`
          }
        />
      ))}

      {openMarker && hasCard && (
        <MapPopup
          longitude={openMarker.longitude}
          latitude={openMarker.latitude}
          anchor={cardAnchor}
          onClose={close}
          maxWidth="none"
        >
          {renderCard
            ? renderCard(openMarker, close)
            : openMarker.card && <MarkerCard {...openMarker.card} />}
        </MapPopup>
      )}
    </>
  )
})
