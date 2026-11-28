import { attachmentIdOf, isAllowedSrc, type SameOriginPrefixes } from "./allowed-src";
import { isMediaKind, SRC_KINDS, type MediaKind } from "./kinds";

/**
 * Reading a media block, and gating it.
 *
 * VALIDATION HAPPENS ONCE, HERE — not in each renderer. That split is taken
 * from the archived chat, whose LinkBlock says outright that the payload "is
 * validated centrally at the registry dispatch point before this renderer runs,
 * so we can trust it here". Per-renderer checking is how one of eleven quietly
 * ends up missing its own.
 *
 * A rejected URL does not throw and does not render a broken element: the field
 * is dropped, so a block with an unsafe cover still plays its audio, and a block
 * with an unsafe `src` renders nothing at all.
 */

export interface MediaBlock {
  readonly kind: MediaKind;
  readonly src?: string;
  readonly cover?: string;
  readonly title?: string;
  readonly alt?: string;
  /** Textual kinds (json/code/markdown/text/mermaid) carry content, not a src. */
  readonly content?: string;
  /** `code` only. */
  readonly language?: string;
  readonly items?: readonly MediaGalleryItem[];
  /** `link` only — the destination and its pre-resolved unfurl. */
  readonly url?: string;
  readonly link?: MediaLinkPreview;
  readonly aspectRatio?: number;
  /** Present only when a tool produced the picture rather than found it. */
  readonly generation?: MediaGeneration;
  /**
   * The server-hosted blob these bytes ARE, when the src names one.
   *
   * Derived from the src, never authored: the server serves hosted bytes at
   * `/api/admin/attachments/<sha256>` and that sha256 IS the attachment id, so
   * the block already states its own key. Absent for a picture hosted
   * elsewhere — those bytes never reached this server and nothing here has
   * measured them.
   *
   * An IDENTITY, not a copy of the facts. The turn's file parts already carry
   * width, size and duration; duplicating them onto the block would give one
   * fact two homes and let them disagree.
   */
  readonly attachmentId?: string;
}

/**
 * How a picture came to exist: the request, and the model that answered it.
 *
 * `size` is a preference the provider may ignore and `quality` is an intent, so
 * a card must present both as the request they are. `model` is the one field
 * describing the RESULT — the router reports which model its ladder reached,
 * which the intent alone cannot say. Absent when the router did not report one.
 */
export interface MediaGeneration {
  readonly prompt: string;
  readonly size?: string;
  readonly quality?: string;
  readonly model?: string;
  /**
   * Where these bytes also live on the open internet. Carried here because the
   * server rewrites `src` when it hosts the bytes, so a card reading one finds
   * an internal path. Absent when the producer hosted nothing.
   */
  readonly publicUrl?: string;
}

export interface MediaGalleryItem {
  readonly src: string;
  readonly thumbnail?: string;
  readonly alt?: string;
}

export interface MediaLinkPreview {
  readonly title?: string;
  readonly description?: string;
  readonly image?: string;
  readonly favicon?: string;
  readonly siteName?: string;
}

const str = (value: unknown): string | undefined =>
  typeof value === "string" && value !== "" ? value : undefined;

/**
 * Read and GATE a media block.
 *
 * Returns null when the block cannot be rendered honestly — an unknown kind, a
 * src-bearing kind whose src is rejected, or a textual kind with no content.
 */
/**
 * The wire field a textual kind carries its payload in.
 *
 * The server does NOT send one `content` field. Each textual kind names its own
 * — a mermaid block sends `chart`, a markdown block `markdown`, a code block
 * `code` — while this model keeps a single `content`, because a renderer that
 * has already switched on `kind` gains nothing from a second name for "the
 * text". Translating at the boundary is what keeps that true.
 *
 * Reading only `content` is what made every one of these blocks vanish: the
 * field was always undefined, so the check below rejected the block and no
 * renderer ever ran. Silent, because a dropped block looks exactly like a block
 * the agent never sent.
 */
const CONTENT_FIELD: Partial<Record<MediaKind, string>> = {
  code: "code",
  markdown: "markdown",
  text: "text",
  mermaid: "chart",
};

/**
 * A textual kind's payload as a string, or undefined.
 *
 * `json` is the one kind whose payload is not text on the wire — the server
 * sends the parsed VALUE. It is serialised here so the block model can keep one
 * string field, and because a renderer showing JSON has to print it anyway.
 */
function readContent(row: Record<string, unknown>, kind: MediaKind): string | undefined {
  if (kind === "json") {
    if (row.data === undefined) return undefined;
    try {
      return JSON.stringify(row.data, null, 2);
    } catch {
      // A cycle cannot survive the wire, so this is unreachable through the
      // server — it guards a hand-built block in a story or a test.
      return undefined;
    }
  }

  const field = CONTENT_FIELD[kind] ?? "content";
  const value = row[field];
  // Not `str()`: that treats "" as absent, and an empty code block is a
  // legitimate thing for an agent to show.
  if (typeof value === "string") return value;
  // The generic name is accepted as a fallback for every kind, so a hand-built
  // block and a story keep working against the model's own vocabulary.
  return typeof row.content === "string" ? row.content : undefined;
}

export function readMediaBlock(
  data: unknown,
  prefixes: SameOriginPrefixes,
): MediaBlock | null {
  if (typeof data !== "object" || data === null) return null;
  const row = data as Record<string, unknown>;
  if (!isMediaKind(row.kind)) return null;

  const kind = row.kind;
  const safe = (value: unknown): string | undefined => {
    const url = str(value);
    if (url === undefined) return undefined;
    return isAllowedSrc(url, prefixes) ? url : undefined;
  };

  const block: MediaBlock = {
    kind,
    src: safe(row.src),
    // Secondary URLs are gated exactly like the primary one. They are the ones
    // a renderer forgets, and each is an outbound request made on behalf of a
    // model-authored block.
    cover: safe(row.cover),
    title: str(row.title),
    alt: str(row.alt),
    content: readContent(row, kind),
    language: str(row.language),
    items: readItems(row.items, safe),
    url: safe(row.url),
    link: readLink(row.link, safe),
    aspectRatio: typeof row.aspectRatio === "number" && row.aspectRatio > 0
      ? row.aspectRatio
      : undefined,
    generation: readGeneration(row.generation, safe),
    attachmentId: attachmentIdOf(safe(row.src), prefixes),
  };

  // A src-bearing kind with no surviving src has nothing to show. Rendering an
  // empty frame would claim media exists that the gate just refused.
  if (SRC_KINDS.has(kind)) {
    const hasSource =
      block.src !== undefined ||
      block.url !== undefined ||
      (block.items?.length ?? 0) > 0;
    if (!hasSource) return null;
  } else if (kind !== "map" && block.content === undefined) {
    return null;
  }

  return block;
}

function readItems(
  raw: unknown,
  safe: (value: unknown) => string | undefined,
): readonly MediaGalleryItem[] | undefined {
  if (!Array.isArray(raw)) return undefined;
  const items: MediaGalleryItem[] = [];
  for (const entry of raw) {
    if (typeof entry !== "object" || entry === null) continue;
    const row = entry as Record<string, unknown>;
    const src = safe(row.src);
    // An item whose src was rejected is dropped rather than shown as a gap:
    // the gallery stays honest about what it can actually display.
    if (src === undefined) continue;
    items.push({ src, thumbnail: safe(row.thumbnail), alt: str(row.alt) });
  }
  return items.length > 0 ? items : undefined;
}

/**
 * A generation is its prompt. Without one there is nothing a card could show,
 * so the field is dropped rather than kept as an empty shell a renderer would
 * then have to decide how to draw.
 */
function readGeneration(
  raw: unknown,
  safe: (value: unknown) => string | undefined,
): MediaGeneration | undefined {
  if (typeof raw !== "object" || raw === null) return undefined;
  const row = raw as Record<string, unknown>;
  const prompt = str(row.prompt);
  if (prompt === undefined) return undefined;
  return {
    prompt,
    size: str(row.size),
    quality: str(row.quality),
    model: str(row.model),
    // Gated like every other src on this block: a provenance field is written
    // by a tool, so an unvalidated one would be an address a model chose.
    publicUrl: safe(row.publicUrl),
  };
}

function readLink(
  raw: unknown,
  safe: (value: unknown) => string | undefined,
): MediaLinkPreview | undefined {
  if (typeof raw !== "object" || raw === null) return undefined;
  const row = raw as Record<string, unknown>;
  const preview: MediaLinkPreview = {
    title: str(row.title),
    description: str(row.description),
    image: safe(row.image),
    favicon: safe(row.favicon),
    siteName: str(row.siteName),
  };
  // The server's own note: a preview with no title/description/image still
  // renders as a bare URL card, so an all-empty preview is not an error.
  return preview;
}
