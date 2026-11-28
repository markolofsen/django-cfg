'use client';

/**
 * React NodeView for the NotionEditor `mapBlock` node. A wrapper around
 * `LazyMapContainer` (mirrors the chat `MapBlock` renderer) seeded from the
 * node's serializable `MapBlockPayload` attrs: viewport from `center`/`zoom`,
 * markers via `MapMarker`. The heavy MapLibre bundle only loads when the node
 * actually mounts (the lazy container handles that).
 *
 * INTERACTIVE when the editor is editable: markers render through the Map
 * tool's `DraggableMarkers` inside `<MapEditLayer>` and every edit (drag a pin,
 * add / remove a pin, switch basemap) is written back into the node attrs via
 * `useNodeAttrs().patch(...)`, so the change survives the ```map markdown
 * round-trip. READ-ONLY editors keep static, non-draggable pins.
 *
 * Payloads are validated through `MapBlockPayloadSchema` first — a corrupted
 * ```map JSON renders a safe `<BlockError>` card instead of throwing.
 */

import { useCallback } from 'react';
import { NodeViewWrapper, type NodeViewProps } from '@tiptap/react';
import { LazyMapContainer, MapMarker } from '@djangocfg/widget-map';
import type { MarkerData, MapStyleKey } from '@djangocfg/widget-map';
import type { MapContainerProps } from '@djangocfg/widget-map';
import { BlockError, MapBlockPayloadSchema, safeParseBlock } from '../blocks';
import type { MapMarkerPayload } from '../blocks';
import { useNodeAttrs } from '../tiptap';
import { MapEditLayer } from './MapEditLayer';

export function MapView(props: NodeViewProps) {
  const { node, editor } = props;
  const editable = editor.isEditable;

  // Single write-back seam: discrete edits (drag-end, add/remove pin, basemap)
  // commit immediately — they don't fire per-frame, so no debounce needed.
  const { patch } = useNodeAttrs<Record<string, unknown>>(props);

  const onMarkersChange = useCallback(
    (markers: MapMarkerPayload[]) => patch({ markers }),
    [patch],
  );
  const onBasemapChange = useCallback(
    (key: MapStyleKey) => patch({ basemap: key }),
    [patch],
  );

  // Validate the node's attrs through the shared schema BEFORE touching the
  // map — a hand-authored / corrupted ```map JSON renders a safe `<BlockError>`
  // card instead of throwing inside MapLibre and taking down the editor.
  const parsed = safeParseBlock(MapBlockPayloadSchema, node.attrs);
  if (!parsed.ok) {
    return (
      <NodeViewWrapper data-type="mapBlock" className="notion-map" draggable={false}>
        <BlockError label="map" reason={parsed.error} />
      </NodeViewWrapper>
    );
  }

  const payload = parsed.data;
  const markers = payload.markers ?? [];

  const initialViewport = {
    longitude: payload.center.lng,
    latitude: payload.center.lat,
    zoom: payload.zoom ?? 11,
  };

  // Build optional map props as ONE typed literal (same TS2769-avoidance
  // reasoning as the chat MapBlock renderer) before spreading. The basemap
  // switcher write-back is only wired when the editor is editable.
  const mapOptions: Partial<MapContainerProps> = {
    ...(payload.basemap ? { mapStyle: payload.basemap } : {}),
    ...(payload.terrain ? { terrain: true } : {}),
    ...(editable ? { onBasemapChange } : {}),
  };

  return (
    <NodeViewWrapper data-type="mapBlock" className="notion-map" draggable={false}>
      <div className="w-full overflow-hidden rounded-2xl border border-border" style={{ height: 360 }}>
        <LazyMapContainer initialViewport={initialViewport} fullscreenTitle="Map" {...mapOptions}>
          {editable ? (
            // Interactive: draggable pins + add/remove affordances, all writing
            // back through `onMarkersChange` → `patch({ markers })`.
            <MapEditLayer markers={markers} onMarkersChange={onMarkersChange} />
          ) : (
            // Read-only: static, non-draggable pins (original behaviour).
            markers.map((m) => {
              const marker: MarkerData = {
                id: m.id,
                longitude: m.lng,
                latitude: m.lat,
                data: m.label ? { label: m.label } : undefined,
              };
              return (
                <MapMarker key={m.id} marker={marker} color={m.color} ariaLabel={m.label} />
              );
            })
          )}
        </LazyMapContainer>
      </div>
    </NodeViewWrapper>
  );
}
