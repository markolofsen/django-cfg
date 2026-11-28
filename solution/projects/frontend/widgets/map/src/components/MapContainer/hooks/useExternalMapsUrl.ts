'use client'

import type { MapViewport } from '../../../types'

/**
 * External-maps link. A host-supplied `openInMapsUrl` wins (Apple Maps, a
 * custom deep link); otherwise deep-link to Google Maps at the current center
 * so the button always works without configuration.
 */
export function useExternalMapsUrl({
  openInMapsUrl,
  openInMapsLabel,
  googleMapsButton,
  viewport,
}: {
  openInMapsUrl: string | undefined
  openInMapsLabel: string
  googleMapsButton: boolean
  viewport: MapViewport
}) {
  const externalMapsUrl =
    openInMapsUrl ??
    (googleMapsButton
      ? `https://www.google.com/maps/search/?api=1&query=${viewport.latitude},${viewport.longitude}`
      : undefined)
  const externalMapsLabel = openInMapsUrl ? openInMapsLabel : 'Open in Google Maps'

  return { externalMapsUrl, externalMapsLabel }
}
