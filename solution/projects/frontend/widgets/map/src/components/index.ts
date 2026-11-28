/**
 * The whole component surface, container included.
 *
 * Anything reached from the LAZY entry must import `./light` instead: this
 * barrel holds a static edge to MapLibre GL through `MapContainer`.
 */

export * from './light'
export { MapContainer, MapView } from './MapContainer'
