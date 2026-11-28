'use client'

import { memo, type ReactNode } from 'react'
import { Source, Layer, type LayerProps } from 'react-map-gl/maplibre'

export interface MapSourceProps {
  id: string
  data: GeoJSON.GeoJSON | string
  type?: 'geojson'
  children?: ReactNode
}

export const MapSource = memo(function MapSource({
  id,
  data,
  type = 'geojson',
  children,
}: MapSourceProps) {
  return (
    <Source id={id} type={type} data={data}>
      {children}
    </Source>
  )
})

export type MapLayerProps = LayerProps

export const MapLayer = memo(function MapLayer(props: MapLayerProps) {
  return <Layer {...props} />
})
