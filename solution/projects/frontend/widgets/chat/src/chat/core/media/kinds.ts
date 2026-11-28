/**
 * The media block vocabulary — one event type (8), eleven kinds.
 *
 * SOURCE OF TRUTH: the server's `Kind` vocabulary and its supported-kinds set.
 * Mirrored here so the discriminant lives in ONE place on this
 * side too, instead of being re-spelled inside each renderer.
 *
 * This is why media is a REGISTRY rather than a widget: eleven kinds behind one
 * event type is exactly the shape the O(1) rule exists for. A twelfth kind adds
 * a registry entry and a renderer — never a prop on `<Chat>`.
 */

export const MEDIA_KINDS = [
  "image",
  "audio",
  "video",
  "map",
  "json",
  "code",
  "markdown",
  "text",
  "mermaid",
  "gallery",
  "link",
] as const;

export type MediaKind = (typeof MEDIA_KINDS)[number];

const SUPPORTED = new Set<string>(MEDIA_KINDS);

/**
 * Is this a kind this build knows how to render?
 *
 * An unknown kind is not an error: the server's vocabulary grows, and a
 * transcript stored by a newer agent may reach an older client. The caller
 * renders nothing rather than guessing — the same degrade the server applies
 * ("an unsupported kind is rejected by Validate").
 */
export function isMediaKind(value: unknown): value is MediaKind {
  return typeof value === "string" && SUPPORTED.has(value);
}

/**
 * Kinds whose payload is TEXT, not a `src`.
 *
 * They are routed to the content renderer instead of a media element, which is
 * the seam where `widgets/` and `content/` meet. Getting this list wrong grows a
 * second markdown path — the exact duplication the registry exists to prevent.
 */
export const TEXTUAL_KINDS = new Set<MediaKind>([
  "json",
  "code",
  "markdown",
  "text",
  "mermaid",
]);

/** Kinds that load a URL, and therefore MUST pass the allowlist. */
export const SRC_KINDS = new Set<MediaKind>(["image", "audio", "video", "gallery", "link"]);

/**
 * Every URL-bearing field per kind — NOT just `src`.
 *
 * Checked against the server's own validation, and that is the reason to write
 * it out: the secondary URLs are the ones a renderer forgets. The server gates
 * `cover` on audio/video, `thumbnail` on each gallery item, and BOTH
 * `image` and `favicon` inside a link preview — every one of them is an
 * outbound request the browser makes on behalf of a model-authored block.
 *
 * A renderer that validates `src` and then drops an unvalidated `favicon` into
 * an `<img>` has left the exfil vector open while looking careful.
 */
export const URL_FIELDS: Readonly<Record<MediaKind, readonly string[]>> = {
  image: ["src"],
  audio: ["src", "cover"],
  video: ["src", "cover"],
  gallery: ["items[].src", "items[].thumbnail"],
  link: ["url", "link.image", "link.favicon"],
  map: [],
  json: [],
  code: [],
  markdown: [],
  text: [],
  mermaid: [],
};
