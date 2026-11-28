export { useMap } from './useMap'
export { useMapControl } from './useMapControl'
export { useMarkers } from './useMarkers'
export { useMapEvents } from './useMapEvents'
export { useMapViewport } from './useMapViewport'
export { useMapLayers } from './useMapLayers'
export { useSpiderfy, type UseSpiderfyOptions, type UseSpiderfyResult } from './useSpiderfy'
export {
  useMapScrollProtection,
  type UseMapScrollProtectionResult,
  type MapScrollProtectionMode,
} from './useMapScrollProtection'
export { useMapTouchMode } from './useMapTouchMode'
export {
  useMapImages,
  type MapImage,
  type UseMapImagesResult,
} from './useMapImages'
export { useTerrain, type UseTerrainOptions } from './useTerrain'
export { useCompass, type UseCompassResult } from './useCompass'
export { useMeasure, type UseMeasureResult, type MeasureMode } from './useMeasure'
export {
  useGeolocation,
  type GeolocationFix,
  type GeolocationStatus,
  type UseGeolocationOptions,
  type UseGeolocationResult,
} from './useGeolocation'

export {
  useDraggableMarkers,
  type DraggablePoint,
  type UseDraggableMarkersOptions,
  type UseDraggableMarkersResult,
  type DraggableMarkerHandlers,
} from './useDraggableMarkers'

export {
  useGeocoder,
  type UseGeocoderOptions,
  type UseGeocoderResult,
} from './useGeocoder'

export { useMarkerCard, type UseMarkerCardResult } from './useMarkerCard'
export { useStyleFont } from './useStyleFont'
export { usePillImage, PILL_IMAGE_ID } from './usePillImage'

// Re-export useControl from react-map-gl for custom control creation
export { useControl } from 'react-map-gl/maplibre'
