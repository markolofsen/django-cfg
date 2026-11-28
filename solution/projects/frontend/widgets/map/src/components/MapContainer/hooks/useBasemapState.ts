'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'

import { MAP_STYLES, resolveBasemapOptions } from '../../../styles'
import type { MapStyleKey } from '../../../types'

/**
 * Active basemap state. Seeded from `mapStyle`, then driven by the switcher.
 * If `mapStyle` is a built-in KEY we track it as the active key; a raw URL is
 * kept as-is (the switcher still works, just starts "unselected").
 */
export function useBasemapState({
  mapStyle,
  basemaps,
  onBasemapChange,
}: {
  mapStyle: MapStyleKey | string
  basemaps: MapStyleKey[] | undefined
  onBasemapChange: ((key: MapStyleKey) => void) | undefined
}) {
  const initialKey = (mapStyle in MAP_STYLES ? mapStyle : undefined) as MapStyleKey | undefined
  const [activeKey, setActiveKey] = useState<MapStyleKey | undefined>(initialKey)
  // Follow controlled `mapStyle` changes from the host.
  useEffect(() => {
    setActiveKey(mapStyle in MAP_STYLES ? (mapStyle as MapStyleKey) : undefined)
  }, [mapStyle])
  // The style actually rendered: the chosen key's URL, else the raw prop.
  const effectiveStyle = activeKey ?? mapStyle
  const basemapOptions = useMemo(
    () => resolveBasemapOptions(basemaps, activeKey ?? (mapStyle as MapStyleKey | string)),
    [basemaps, activeKey, mapStyle],
  )
  const handleBasemapPick = useCallback(
    (key: string) => {
      setActiveKey(key as MapStyleKey)
      onBasemapChange?.(key as MapStyleKey)
    },
    [onBasemapChange],
  )

  // Resolve the EFFECTIVE style (switcher-aware) to a URL/object.
  const resolvedStyle = effectiveStyle in MAP_STYLES
    ? MAP_STYLES[effectiveStyle as MapStyleKey]
    : effectiveStyle

  return { activeKey, effectiveStyle, resolvedStyle, basemapOptions, handleBasemapPick }
}
