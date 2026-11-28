'use client';

/**
 * `MapEditLayer` — the EDITABLE inner layer of the NotionEditor `mapBlock`
 * NodeView. Rendered as a child of `LazyMapContainer` (so it sits inside the
 * `MapProvider` and can use the map's hooks). Composes the Map tool's existing
 * `DraggableMarkers` + `useMapEvents`; it does NOT rebuild map internals.
 *
 * Two-way binding: every edit (drag a pin, add a pin, remove a pin) is mapped
 * back to the node's `MapMarkerPayload[]` and committed through the
 * `onMarkersChange` callback, which the NodeView wires to
 * `useNodeAttrs().patch({ markers })` → the ```map JSON updates.
 *
 * Affordances (editable only; keyboard-reachable, semantic tokens):
 *  - "Add pin" toggles a click-to-place mode; the next map click appends a
 *    marker at the clicked lng/lat.
 *  - "Remove" toggles a delete mode; a small ✕ badge appears on each pin and
 *    clicking it drops that marker.
 * The basemap switch is handled by `LazyMapContainer`'s own switcher (the
 * NodeView wires `onBasemapChange`), so it isn't duplicated here.
 */

import { useCallback, useMemo, useState, type ReactNode } from 'react';
import { MapPin, Plus, Trash2, X } from 'lucide-react';
import {
  DraggableMarkers,
  useMapEvents,
  type DraggablePoint,
  type MarkerData,
} from '@djangocfg/widget-map';
import type { MapMarkerPayload } from '../blocks';

export interface MapEditLayerProps {
  /** Current markers (the node's committed payload). */
  markers: MapMarkerPayload[];
  /** Commit a new marker array back to the node (→ markdown). */
  onMarkersChange: (next: MapMarkerPayload[]) => void;
}

/** Generate a stable-ish unique marker id. */
function nextMarkerId(existing: MapMarkerPayload[]): string {
  let n = existing.length + 1;
  const ids = new Set(existing.map((m) => m.id));
  let id = `m${n}`;
  while (ids.has(id)) {
    n += 1;
    id = `m${n}`;
  }
  return id;
}

export function MapEditLayer({ markers, onMarkersChange }: MapEditLayerProps) {
  // Mutually-exclusive edit modes. `null` = plain drag-only editing.
  const [mode, setMode] = useState<'add' | 'delete' | null>(null);

  // ── Map → payload: DraggablePoint {id,lng,lat} ⇄ MapMarkerPayload ──────────
  // DraggableMarkers is controlled by `positions`; on drag-END it hands back
  // the full updated array. We map each point back onto its source payload so
  // labels / colours / icons / cards are PRESERVED (DraggablePoint only carries
  // id/lng/lat/label).
  const positions = useMemo<DraggablePoint[]>(
    () =>
      markers.map((m) => ({
        id: m.id,
        lng: m.lng,
        lat: m.lat,
        ...(m.label !== undefined ? { label: m.label } : {}),
      })),
    [markers],
  );

  const handleDragChange = useCallback(
    (next: DraggablePoint[]) => {
      const byId = new Map(markers.map((m) => [m.id, m]));
      const merged: MapMarkerPayload[] = next.map((p) => {
        const prev = byId.get(p.id);
        // Preserve everything but the moved coordinates.
        return prev
          ? { ...prev, lat: p.lat, lng: p.lng }
          : { id: p.id, lat: p.lat, lng: p.lng, ...(p.label ? { label: p.label } : {}) };
      });
      onMarkersChange(merged);
    },
    [markers, onMarkersChange],
  );

  // ── Click-to-place (add mode) ──────────────────────────────────────────────
  useMapEvents({
    onClick: (event) => {
      if (mode !== 'add') return;
      const { lng, lat } = event.lngLat;
      const id = nextMarkerId(markers);
      onMarkersChange([...markers, { id, lat, lng }]);
    },
  });

  // ── Remove (delete mode): a ✕ badge per pin ────────────────────────────────
  const removeMarker = useCallback(
    (id: string) => {
      onMarkersChange(markers.filter((m) => m.id !== id));
    },
    [markers, onMarkersChange],
  );

  // Only supplied to DraggableMarkers in delete mode (see render below), so it
  // always renders the ✕ badge that replaces the default pin.
  const renderMarker = useCallback(
    (marker: MarkerData) => {
      return (
        <button
          type="button"
          aria-label={`Remove pin ${marker.id}`}
          // Stop the click from reaching the map / starting a drag.
          onMouseDown={(e) => e.stopPropagation()}
          onPointerDown={(e) => e.stopPropagation()}
          onClick={(e) => {
            e.stopPropagation();
            removeMarker(marker.id);
          }}
          className="flex h-6 w-6 items-center justify-center rounded-full border border-border bg-destructive text-destructive-foreground shadow-md transition-transform hover:scale-110 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          <X className="h-3.5 w-3.5" aria-hidden="true" />
        </button>
      );
    },
    [removeMarker],
  );

  return (
    <>
      <DraggableMarkers
        positions={positions}
        onChange={handleDragChange}
        renderMarker={mode === 'delete' ? renderMarker : undefined}
      />

      {/* Edit control overlay — top-left so it clears the map toolbar chips. */}
      <div className="pointer-events-none absolute left-2 top-2 z-10 flex flex-col gap-1">
        <div className="pointer-events-auto flex gap-1 rounded-lg border border-border bg-card/95 p-1 shadow-md backdrop-blur">
          <ControlButton
            active={mode === 'add'}
            label="Add pin"
            onClick={() => setMode((m) => (m === 'add' ? null : 'add'))}
          >
            <Plus className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Add pin</span>
          </ControlButton>
          <ControlButton
            active={mode === 'delete'}
            label="Remove pins"
            disabled={markers.length === 0}
            onClick={() => setMode((m) => (m === 'delete' ? null : 'delete'))}
          >
            <Trash2 className="h-3.5 w-3.5" aria-hidden="true" />
            <span>Remove</span>
          </ControlButton>
        </div>
        {mode ? (
          <div className="pointer-events-none flex items-center gap-1.5 self-start rounded-md border border-border bg-card/95 px-2 py-1 text-xs text-muted-foreground shadow-sm backdrop-blur">
            <MapPin className="h-3 w-3" aria-hidden="true" />
            {mode === 'add' ? 'Click the map to place a pin' : 'Click a ✕ to remove a pin'}
          </div>
        ) : null}
      </div>
    </>
  );
}

function ControlButton({
  active,
  disabled,
  label,
  onClick,
  children,
}: {
  active: boolean;
  disabled?: boolean;
  label: string;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      aria-label={label}
      aria-pressed={active}
      disabled={disabled}
      onClick={onClick}
      className={
        'inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 ' +
        (active
          ? 'bg-primary text-primary-foreground'
          : 'text-foreground hover:bg-muted')
      }
    >
      {children}
    </button>
  );
}
