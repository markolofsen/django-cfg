/**
 * Shared, serializable block payload TYPES — the wire shapes that more than
 * one surface (chat message blocks + the NotionEditor block NodeViews) must
 * agree on. Defining them ONCE here keeps the shapes from drifting: chat's
 * `tools/chat/types/block.ts` and the Notion nodes both reference these.
 *
 * Plain JSON only (no Date / no functions / no React nodes) so payloads
 * survive history persistence, SSE transport, AND TipTap node attrs +
 * markdown round-trips.
 */

/** A single map marker — a pin plus optional label / icon / colour / card. */
export interface MapMarkerPayload {
  id: string;
  lat: number;
  lng: number;
  label?: string;
  /** Image URL rendered as the marker pin (rounded thumbnail). */
  icon?: string;
  /** CSS color for the default pin (ignored when `icon` is set). */
  color?: string;
  /**
   * Info-card opened above the pin on click (Google-Maps style). Pure JSON —
   * strings/URLs only; actions are `href`-only links (no `onClick`/`icon`,
   * which can't cross the wire). Rendered by the map's default `MarkerCard`.
   */
  card?: {
    title: string;
    description?: string;
    image?: string;
    badge?: string;
    actions?: Array<{ label: string; href?: string }>;
  };
}

/** An ordered polyline (route / path). */
export interface MapRoutePayload {
  id: string;
  points: Array<{ lat: number; lng: number }>;
  color?: string;
  label?: string;
}

/** A filled polygon (zone), auto-closed. */
export interface MapPolygonPayload {
  id: string;
  points: Array<{ lat: number; lng: number }>;
  fillColor?: string;
  strokeColor?: string;
  label?: string;
}

/**
 * Serializable map payload shared by the chat `MapBlock` and the NotionEditor
 * `mapBlock` node. A center + optional zoom / basemap / terrain / markers /
 * routes / polygons. The chat block extends this with chat-only concerns
 * (a `caption`, `userLocation` opt-in); the Notion node serializes this whole
 * object to/from a fenced ```` ```map ```` JSON block.
 */
export interface MapBlockPayload {
  center: { lat: number; lng: number };
  zoom?: number;
  /**
   * Basemap style — a built-in key (`'light'`/`'dark'`/`'streets'` ·
   * `'liberty'`/`'bright'`/`'positron'`) or a full style-JSON URL. When
   * omitted the map uses its default basemap.
   */
  basemap?: string;
  /** Enable 3D terrain + hillshade (free AWS Terrarium DEM, no key). */
  terrain?: boolean;
  markers?: MapMarkerPayload[];
  /** Polylines (routes / paths). */
  routes?: MapRoutePayload[];
  /** Filled zones (polygons). */
  polygons?: MapPolygonPayload[];
}
