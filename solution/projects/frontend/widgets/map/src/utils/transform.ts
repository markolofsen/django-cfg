/**
 * Convert an array of items to GeoJSON FeatureCollection
 */
export function toGeoJSON<T>(
  items: T[],
  getLngLat: (item: T) => [number, number],
  getProperties?: (item: T) => Record<string, unknown>
): GeoJSON.FeatureCollection {
  return {
    type: 'FeatureCollection',
    features: items.map((item, index) => {
      const [lng, lat] = getLngLat(item)
      return {
        type: 'Feature',
        id: index,
        geometry: {
          type: 'Point',
          coordinates: [lng, lat],
        },
        properties: getProperties ? getProperties(item) : {},
      }
    }),
  }
}

/**
 * Convert GeoJSON FeatureCollection to array of items
 */
export function fromGeoJSON<T>(
  fc: GeoJSON.FeatureCollection,
  transform: (feature: GeoJSON.Feature) => T
): T[] {
  return fc.features.map(transform)
}

/**
 * Create a GeoJSON Point
 */
export function createPoint(
  coordinates: [number, number],
  properties: Record<string, unknown> = {}
): GeoJSON.Feature<GeoJSON.Point> {
  return {
    type: 'Feature',
    geometry: {
      type: 'Point',
      coordinates,
    },
    properties,
  }
}

/**
 * Create a GeoJSON Polygon
 */
export function createPolygon(
  coordinates: [number, number][],
  properties: Record<string, unknown> = {}
): GeoJSON.Feature<GeoJSON.Polygon> {
  // Ensure the polygon is closed. Bind both ends once: indexing is what tells
  // the compiler nothing about `length > 0`, and a ring is closed when its
  // last vertex equals its first.
  const closed = [...coordinates]
  const first = coordinates[0]
  const last = coordinates[coordinates.length - 1]
  if (first !== undefined && last !== undefined && (first[0] !== last[0] || first[1] !== last[1])) {
    closed.push(first)
  }

  return {
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [closed],
    },
    properties,
  }
}

/**
 * Create a GeoJSON LineString
 */
export function createLineString(
  coordinates: [number, number][],
  properties: Record<string, unknown> = {}
): GeoJSON.Feature<GeoJSON.LineString> {
  return {
    type: 'Feature',
    geometry: {
      type: 'LineString',
      coordinates,
    },
    properties,
  }
}

/**
 * Create an empty FeatureCollection
 */
export function createFeatureCollection(
  features: GeoJSON.Feature[] = []
): GeoJSON.FeatureCollection {
  return {
    type: 'FeatureCollection',
    features,
  }
}
