/**
 * The mention URL scheme: how a chip in a message names a thing outside it.
 *
 * A mention has to survive a round trip through markdown — a chip is written as
 * a link, sent as text, parsed back, and re-drawn as a chip. That needs a URL
 * shape both halves agree on, and a plain `https:` link cannot carry it: the
 * host must be able to tell "open this thing I know about" from "follow this
 * link", and only a distinct scheme says so.
 *
 * ## Why the scheme is configurable and the shapes are not
 *
 * The SCHEME is the host's — it is their product's name, and it is what their
 * desktop shell or deep-link handler registers. The SHAPES are ours: the chat
 * writes them and the chat parses them, so a host redefining them would break
 * its own round trip.
 *
 * ```
 * <scheme>://tool/<id>               a tool the user picked
 * ```
 *
 * One shape, because only one thing here is the chat's own. A host that mentions
 * users, documents or tickets addresses them with its own scheme and resolves
 * them itself; this module would only be guessing at their grammar. The other
 * shapes that used to live here were one product's nouns and left with it.
 *
 * Nothing here reaches a network. These are addresses the host resolves when a
 * chip is clicked; this module only writes and reads them.
 */

/** The default scheme. Override with {@link configureMentionScheme}. */
const DEFAULT_SCHEME = "app";

let scheme = DEFAULT_SCHEME;

/**
 * Set the URL scheme mentions are written with.
 *
 * Call once at startup, before any message is rendered. Changing it later
 * leaves already-written messages addressing the old scheme, which then parse
 * as plain links — which is the honest outcome, but not one to arrive at by
 * accident.
 */
export function configureMentionScheme(next: string): void {
  scheme = next.replace(/:$/, "");
}

/** The scheme in force. Exposed so a link-hardening allowlist can name it. */
export function mentionScheme(): string {
  return scheme;
}

const HOST_TOOL = "tool";

// --- Writers ---------------------------------------------------------------

/**
 * `<scheme>://tool/<id>`.
 *
 * An empty id returns the bare host, which parses but names no tool; a renderer
 * leaves that as plain text rather than minting a chip that stands for nothing.
 */
export function toolURL(id: string): string {
  return id ? `${scheme}://${HOST_TOOL}/${encodeURIComponent(id)}` : `${scheme}://${HOST_TOOL}`;
}

// --- Reader ----------------------------------------------------------------

export type ParsedMention = { readonly kind: "tool"; readonly toolID: string };

export type ParseResult =
  | { readonly ok: true; readonly parsed: ParsedMention }
  | { readonly ok: false; readonly error: "malformed" | "not-mention-url" | "missing-id" };

/**
 * Read a mention URL back into its parts.
 *
 * A result rather than a throw: an ordinary link in a message reaches here on
 * every render, and "this is not one of ours" is the common case, not a fault.
 */
export function parse(href: string): ParseResult {
  let url: URL;
  try {
    url = new URL(href);
  } catch {
    return { ok: false, error: "malformed" };
  }
  // `URL.protocol` carries the trailing colon.
  if (url.protocol !== `${scheme}:`) return { ok: false, error: "not-mention-url" };

  // `URL.pathname` opens with "/", so the first split entry is always empty.
  const segments = url.pathname.split("/").filter((segment) => segment.length > 0);

  if (url.hostname !== HOST_TOOL) return { ok: false, error: "not-mention-url" };

  const [rawID] = segments;
  if (rawID === undefined) return { ok: false, error: "missing-id" };
  return { ok: true, parsed: { kind: "tool", toolID: decodeURIComponent(rawID) } };
}
