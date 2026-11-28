/**
 * `MapNode` — a NotionEditor block ATOM node that renders an interactive map
 * (`LazyMapContainer`) from a serializable `MapBlockPayload` held in the
 * node's attrs. Inserted via the slash menu (`/map`) — NOT auto from paste,
 * since a map has no natural paste trigger.
 *
 * Markdown round-trip (a fenced ```` ```map ```` JSON block):
 *
 *   `renderMarkdown` emits a fenced code block tagged `map` whose body is the
 *   pretty-printed payload JSON. A custom block `markdownTokenizer` recognises
 *   that exact fence on parse and emits a `mapBlock` token (its OWN token
 *   type — it never collides with the `code` token the lowlight code block
 *   owns). `parseMarkdown` then turns the token back into the node with its
 *   attrs. So `getMarkdown()` ⇄ `setContent()` round-trips losslessly while
 *   staying human-readable in the markdown.
 *
 * Attrs are the flattened `MapBlockPayload` fields (`center`/`zoom`/`basemap`/
 * `terrain`/`markers`) — plain JSON, so they serialise to TipTap node attrs
 * and the fenced JSON cleanly.
 */

import { Node, mergeAttributes } from '@tiptap/core';
import type { MarkdownToken, MarkdownParseHelpers } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import type { MapBlockPayload } from '../blocks';
import { MapBlockPayloadSchema } from '../blocks';
import { MapView } from './MapView';

export interface MapNodeOptions {
  HTMLAttributes: Record<string, unknown>;
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    mapBlock: {
      /** Insert a map block from a payload (markers / center / zoom). */
      setMapBlock: (payload: MapBlockPayload) => ReturnType;
    };
  }
}

/** A sensible default payload so `/map` shows a live map immediately. */
export const DEFAULT_MAP_PAYLOAD: MapBlockPayload = {
  center: { lat: 48.8584, lng: 2.2945 },
  zoom: 13,
  markers: [{ id: 'm1', lat: 48.8584, lng: 2.2945, label: 'Eiffel Tower' }],
};

/** Pull the flattened payload off a node's attrs. */
function payloadFromAttrs(attrs: Record<string, unknown>): MapBlockPayload {
  return {
    center: (attrs.center as MapBlockPayload['center']) ?? DEFAULT_MAP_PAYLOAD.center,
    zoom: attrs.zoom as number | undefined,
    basemap: attrs.basemap as string | undefined,
    terrain: attrs.terrain as boolean | undefined,
    markers: (attrs.markers as MapBlockPayload['markers']) ?? [],
  };
}

/** Drop undefined fields so the serialised JSON stays tidy. */
function compactPayload(payload: MapBlockPayload): MapBlockPayload {
  const out: MapBlockPayload = { center: payload.center };
  if (payload.zoom !== undefined) out.zoom = payload.zoom;
  if (payload.basemap !== undefined) out.basemap = payload.basemap;
  if (payload.terrain !== undefined) out.terrain = payload.terrain;
  if (payload.markers && payload.markers.length) out.markers = payload.markers;
  if (payload.routes && payload.routes.length) out.routes = payload.routes;
  if (payload.polygons && payload.polygons.length) out.polygons = payload.polygons;
  return out;
}

// Matches a fenced ```map … ``` block at the START of the source. Captures the
// JSON body (group 1). Tolerates trailing whitespace + the optional closing
// newline before the fence.
const MAP_FENCE_RE = /^```map[ \t]*\r?\n([\s\S]*?)\r?\n?```[ \t]*(?:\r?\n|$)/;

export const MapNode = Node.create<MapNodeOptions>({
  name: 'mapBlock',
  group: 'block',
  atom: true,
  draggable: true,
  selectable: true,

  addOptions() {
    return { HTMLAttributes: {} };
  },

  addAttributes() {
    return {
      center: {
        default: DEFAULT_MAP_PAYLOAD.center,
        parseHTML: (el) => safeJson(el.getAttribute('data-center')) ?? DEFAULT_MAP_PAYLOAD.center,
        renderHTML: (attrs) => ({ 'data-center': JSON.stringify(attrs.center) }),
      },
      zoom: {
        default: DEFAULT_MAP_PAYLOAD.zoom,
        parseHTML: (el) => numAttr(el.getAttribute('data-zoom')),
        renderHTML: (attrs) => (attrs.zoom != null ? { 'data-zoom': String(attrs.zoom) } : {}),
      },
      basemap: {
        default: undefined,
        parseHTML: (el) => el.getAttribute('data-basemap') ?? undefined,
        renderHTML: (attrs) => (attrs.basemap ? { 'data-basemap': attrs.basemap as string } : {}),
      },
      terrain: {
        default: undefined,
        parseHTML: (el) => el.getAttribute('data-terrain') === 'true' || undefined,
        renderHTML: (attrs) => (attrs.terrain ? { 'data-terrain': 'true' } : {}),
      },
      markers: {
        default: [],
        parseHTML: (el) => safeJson(el.getAttribute('data-markers')) ?? [],
        renderHTML: (attrs) =>
          attrs.markers ? { 'data-markers': JSON.stringify(attrs.markers) } : {},
      },
    };
  },

  parseHTML() {
    return [{ tag: 'div[data-type="mapBlock"]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes({ 'data-type': 'mapBlock' }, this.options.HTMLAttributes, HTMLAttributes),
    ];
  },

  addNodeView() {
    return ReactNodeViewRenderer(MapView);
  },

  addCommands() {
    return {
      setMapBlock:
        (payload: MapBlockPayload) =>
        ({ commands }) =>
          commands.insertContent({ type: this.name, attrs: { ...payload } }),
    };
  },

  // ── Markdown round-trip ────────────────────────────────────────────────
  // Own token type — never collides with the lowlight `code` token.
  markdownTokenName: 'mapBlock',

  markdownTokenizer: {
    name: 'mapBlock',
    level: 'block',
    start: (src: string) => {
      const idx = src.indexOf('```map');
      return idx;
    },
    tokenize: (src: string) => {
      const match = MAP_FENCE_RE.exec(src);
      if (!match) return undefined;
      return {
        type: 'mapBlock',
        raw: match[0],
        text: match[1] ?? '',
      };
    },
  },

  parseMarkdown(token: MarkdownToken, helpers: MarkdownParseHelpers) {
    // Never throw during parse. Three cases:
    //  1. Empty/whitespace body → a default map (a bare ```map``` fence).
    //  2. Valid JSON matching the schema → the parsed payload (compacted).
    //  3. Malformed JSON or a payload that fails the schema → pass the raw
    //     parsed value straight through as attrs so the NodeView's own schema
    //     check renders `<BlockError>` (a visible, non-crashing error block)
    //     rather than silently masquerading as the default map. If JSON.parse
    //     itself fails we keep an obviously-invalid sentinel so the same path
    //     surfaces the error.
    const text = (token.text ?? '').trim();
    if (!text) return helpers.createNode('mapBlock', { ...DEFAULT_MAP_PAYLOAD });

    const raw = safeJson(token.text);
    const result = MapBlockPayloadSchema.safeParse(raw);
    if (result.success) {
      return helpers.createNode('mapBlock', { ...compactPayload(result.data) });
    }
    // Invalid: surface the broken payload as attrs (a plain object so it
    // serialises). `center` must be PRESENT-but-invalid — if it were
    // `undefined`/absent TipTap would substitute the attr default and the
    // NodeView schema would wrongly pass. When the broken payload has no
    // usable center we inject an explicit invalid marker object so the
    // NodeView's `safeParse` fails and renders `<BlockError>`.
    const broken = raw && typeof raw === 'object' ? (raw as Record<string, unknown>) : {};
    const center =
      broken.center !== undefined ? broken.center : { __invalid: true };
    return helpers.createNode('mapBlock', { ...broken, center });
  },

  // `attrs` is optional in tiptap's `JSONContent`; `payloadFromAttrs` already
  // defaults every field, so an absent object is the same as an empty one.
  renderMarkdown(node: { attrs?: Record<string, unknown> }) {
    const payload = compactPayload(payloadFromAttrs(node.attrs ?? {}));
    return '```map\n' + JSON.stringify(payload, null, 2) + '\n```';
  },
});

/** Parse a JSON string, returning null on any failure (never throws). */
function safeJson(value: string | null | undefined): unknown {
  if (!value) return null;
  try {
    return JSON.parse(value);
  } catch {
    return null;
  }
}

/** Parse a numeric attribute, or undefined. */
function numAttr(value: string | null): number | undefined {
  if (value == null) return undefined;
  const n = Number(value);
  return Number.isFinite(n) ? n : undefined;
}

export default MapNode;
