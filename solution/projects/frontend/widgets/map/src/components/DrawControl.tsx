'use client'

/**
 * DrawControl - Drawing tools for polygon, line, point creation
 *
 * Requires: @mapbox/mapbox-gl-draw
 * CSS: @import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css'
 *
 * @example
 * ```tsx
 * import MapboxDraw from '@mapbox/mapbox-gl-draw'
 * import { useControl } from '@djangocfg/widget-map'
 *
 * function DrawControl(props) {
 *   useControl(
 *     () => new MapboxDraw(props),
 *     ({ map }) => {
 *       map.on('draw.create', props.onCreate)
 *       map.on('draw.update', props.onUpdate)
 *       map.on('draw.delete', props.onDelete)
 *     },
 *     ({ map }) => {
 *       map.off('draw.create', props.onCreate)
 *       map.off('draw.update', props.onUpdate)
 *       map.off('draw.delete', props.onDelete)
 *     },
 *     { position: props.position }
 *   )
 *   return null
 * }
 * ```
 */

// Re-export for documentation purposes
// Actual implementation requires user to install @mapbox/mapbox-gl-draw
export { }
