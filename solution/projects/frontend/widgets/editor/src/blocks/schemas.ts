/**
 * Zod schemas for the shared, serializable block payloads in `./types.ts` and
 * the link-preview data contract. These are the runtime VALIDATORS that let a
 * block NodeView render a safe `<BlockError>` fallback instead of throwing when
 * it's handed a hand-authored / corrupted payload (a bad ```map JSON, a
 * malformed wire block).
 *
 * The TS payload types stay the source of truth in `./types.ts` (and
 * `common/link-preview/types.ts`); these schemas are kept in SYNC with them and
 * `satisfies`-checked below so they can't silently drift. We deliberately do
 * NOT re-export `z.infer` types under the same names — existing imports
 * (`MapBlockPayload`, `LinkPreviewData`) keep coming from their type homes.
 *
 * Schemas are permissive on optional/extra fields (`.passthrough` is implied by
 * Zod object stripping unknowns) but STRICT on the load-bearing shape: numbers
 * are numbers, `center`/`url` are required. Anything that wouldn't render
 * cleanly fails `safeParse`.
 */

import { z } from 'zod';
import type {
  MapMarkerPayload,
  MapRoutePayload,
  MapPolygonPayload,
  MapBlockPayload,
} from './types';
import type { LinkPreviewData } from '../link-preview';

/** A finite number — rejects NaN/Infinity that would break the map camera. */
const finiteNumber = z.number().finite();

/** `{ lat, lng }` — a geographic point; both finite numbers, required. */
const LatLngSchema = z.object({
  lat: finiteNumber,
  lng: finiteNumber,
});

/** Marker info-card (pure JSON; `href`-only actions). */
const MarkerCardSchema = z.object({
  title: z.string(),
  description: z.string().optional(),
  image: z.string().optional(),
  badge: z.string().optional(),
  actions: z
    .array(z.object({ label: z.string(), href: z.string().optional() }))
    .optional(),
});

/** A single map marker — pin + optional label / icon / colour / card. */
export const MapMarkerPayloadSchema = z.object({
  id: z.string(),
  lat: finiteNumber,
  lng: finiteNumber,
  label: z.string().optional(),
  icon: z.string().optional(),
  color: z.string().optional(),
  card: MarkerCardSchema.optional(),
});

/** An ordered polyline (route / path). */
export const MapRoutePayloadSchema = z.object({
  id: z.string(),
  points: z.array(LatLngSchema),
  color: z.string().optional(),
  label: z.string().optional(),
});

/** A filled polygon (zone), auto-closed. */
export const MapPolygonPayloadSchema = z.object({
  id: z.string(),
  points: z.array(LatLngSchema),
  fillColor: z.string().optional(),
  strokeColor: z.string().optional(),
  label: z.string().optional(),
});

/** The serializable map payload — center + optional viewport + overlays. */
export const MapBlockPayloadSchema = z.object({
  center: LatLngSchema,
  zoom: finiteNumber.optional(),
  basemap: z.string().optional(),
  terrain: z.boolean().optional(),
  markers: z.array(MapMarkerPayloadSchema).optional(),
  routes: z.array(MapRoutePayloadSchema).optional(),
  polygons: z.array(MapPolygonPayloadSchema).optional(),
});

/** Resolved link-preview metadata — `url` required, rest optional. */
export const LinkPreviewDataSchema = z.object({
  url: z.string(),
  title: z.string().optional(),
  description: z.string().optional(),
  image: z.string().optional(),
  favicon: z.string().optional(),
  siteName: z.string().optional(),
});

// ── Drift guards ──────────────────────────────────────────────────────────
// A type-level assertion that each schema's inferred output is assignable to
// the canonical TS payload type. If `./types.ts` and a schema diverge, the
// corresponding `Extends<…>` resolves to `never` and the assignment fails to
// compile — keeping the schemas and types in lockstep.
type Extends<A, B> = A extends B ? true : never;
const _markerOk: Extends<z.infer<typeof MapMarkerPayloadSchema>, MapMarkerPayload> = true;
const _routeOk: Extends<z.infer<typeof MapRoutePayloadSchema>, MapRoutePayload> = true;
const _polygonOk: Extends<z.infer<typeof MapPolygonPayloadSchema>, MapPolygonPayload> = true;
const _mapOk: Extends<z.infer<typeof MapBlockPayloadSchema>, MapBlockPayload> = true;
const _linkOk: Extends<z.infer<typeof LinkPreviewDataSchema>, LinkPreviewData> = true;
// Reference the guards so `noUnusedLocals` stays happy without exporting them.
void [_markerOk, _routeOk, _polygonOk, _mapOk, _linkOk];

/**
 * Discriminated result of a guarded parse — never throws.
 *
 * The mutually-exclusive `?: never` fields make narrowing robust: a plain
 * `if (!r.ok)` flows into the error branch even when `T` is a deep object type
 * (TS's discriminant else-narrowing otherwise mis-fires on very large `data`
 * shapes). Callers can therefore use `!r.ok` / `r.ok` freely.
 */
export type SafeParseResult<T> =
  | { ok: true; data: T; error?: never }
  | { ok: false; error: string; data?: never };

/**
 * Validate `data` against `schema`, returning a discriminated result instead of
 * throwing. On failure `error` is a short, human-readable reason (the first
 * Zod issue) suitable for a `<BlockError reason=…>` card.
 *
 * The output type is taken from the schema (`z.infer`) so callers get the
 * precisely-typed `data` on the success branch with no extra type argument.
 */
export function safeParseBlock<S extends z.ZodTypeAny>(
  schema: S,
  data: unknown,
): SafeParseResult<z.infer<S>> {
  const result = schema.safeParse(data);
  if (result.success) return { ok: true, data: result.data };
  const first = result.error.issues[0];
  const reason = first
    ? `${first.path.length ? first.path.map(String).join('.') + ': ' : ''}${first.message}`
    : 'Invalid payload';
  return { ok: false, error: reason };
}
