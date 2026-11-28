/**
 * The media `src` allowlist — a security boundary, mirrored from the server.
 *
 * SOURCE OF TRUTH: the server's own `src` allowlist and same-origin rule. This
 * is a deliberate second implementation, not a duplicated helper: the server
 * gates what a TOOL may emit, this side gates what a BROWSER will load, and a
 * block can reach the DOM through a stored transcript no live server process
 * re-validated.
 *
 * The stake, plainly: an unvalidated preview image is an exfil vector. A model-authored `<img src>` is an outbound GET the user never
 * asked for, carrying the page's referrer and cookies to whoever the model
 * names.
 *
 * The server also fixes the rendering contract, and it holds here too: blocks are
 * RENDER-ONLY. Nothing in this package may interpret a block as an action.
 *
 * Keep in lock-step with whatever the server enforces. Divergence in either
 * direction is a real defect — laxer here loads what the server rejected;
 * stricter here silently blanks media that is legitimately allowed.
 */

// The app's own scheme, read from the mention-link module rather than repeated:
// a second copy of the scheme is a second thing to change, and what it hides is
// media that silently blanks after a host reconfigures it.
import { mentionScheme } from "../links";

/**
 * Same-origin path prefixes a src may start with.
 *
 * A PARAMETER rather than a baked-in constant: the list belongs to whoever
 * serves the transcript, and hardcoding a copy here would create a second
 * source of truth that drifts silently the day the server adds a route.
 */
export type SameOriginPrefixes = readonly string[];

/**
 * Is this `src` safe to put in front of a browser?
 *
 * Accepts `https:`, an allowlisted same-origin absolute path, the app's own
 * mention scheme, and `data:image/`. Everything else is rejected — including
 * `javascript:`, non-image `data:`, plain `http:`, `file:` and `vbscript:`.
 */
export function isAllowedSrc(src: string, sameOriginPrefixes: SameOriginPrefixes): boolean {
  const trimmed = src.trim();
  if (trimmed === "") return false;

  const low = trimmed.toLowerCase();
  if (low.startsWith("https://")) return true;
  if (low.startsWith(`${mentionScheme()}://`)) return true;
  // `data:image/` only. A bare `data:` allows text/html, which is script.
  if (low.startsWith("data:image/")) return true;
  if (trimmed.startsWith("/")) return isAllowedSameOrigin(trimmed, sameOriginPrefixes);

  return false;
}

/**
 * A content address: lowercase hex sha256. Mirrored rather than parameterised
 * because it is a property of sha256, not a route a server is free to change.
 */
const CONTENT_ADDRESS = /^[0-9a-f]{64}$/;

/**
 * The attachment a src IS, or nothing.
 *
 * The server serves hosted bytes under a content address, so the last path
 * segment IS the id — this reads a key the src already carries rather than
 * minting one. The ROUTE is not spelled here: it arrives as a same-origin
 * prefix for the same reason `isAllowedSrc` takes one, since baking a server's
 * copy in would be a second source of truth that drifts the day it moves the
 * route.
 *
 * A segment that is not a full hash belongs to some other route, and claiming
 * it as an id would name a blob that does not exist.
 */
export function attachmentIdOf(
  src: string | undefined,
  sameOriginPrefixes: SameOriginPrefixes,
): string | undefined {
  if (src === undefined) return undefined;
  const path = src.split(/[?#]/, 1)[0] ?? "";
  const prefix = sameOriginPrefixes.find((candidate) => path.startsWith(candidate));
  if (prefix === undefined) return undefined;
  const id = path.slice(prefix.length);
  return CONTENT_ADDRESS.test(id) ? id : undefined;
}

/**
 * Gate an absolute-path src.
 *
 * Unlike a scheme, a path can be walked out of its prefix
 * (`/api/admin/../../etc`) or hijacked into another origin, so a plain
 * `startsWith` is NOT sufficient. Two escapes the server calls out by name:
 * `//evil.com/x` is protocol-relative, and `/\evil.com` is treated as such by
 * some browsers.
 */
function isAllowedSameOrigin(src: string, prefixes: SameOriginPrefixes): boolean {
  if (src.startsWith("//") || src.startsWith("/\\")) return false;

  // A query or fragment may legitimately follow; the gate applies to the path.
  const cut = src.search(/[?#]/);
  const path = cut >= 0 ? src.slice(0, cut) : src;

  // REJECT rather than normalise. A src that needs cleaning is not one we
  // minted, and normalising first is how a traversal becomes an allowed path.
  if (path !== cleanPath(path)) return false;

  return prefixes.some((prefix) => path.startsWith(prefix));
}

/**
 * The subset of Go's `path.Clean` this gate needs.
 *
 * Only used to answer "is this path already clean?", never to sanitise a path
 * for use — a caller that cleans and then trusts the result has re-introduced
 * exactly the bug the reject-don't-normalise rule prevents.
 */
export function cleanPath(path: string): string {
  if (path === "") return ".";

  const rooted = path.startsWith("/");
  const out: string[] = [];

  for (const segment of path.split("/")) {
    if (segment === "" || segment === ".") continue;
    if (segment === "..") {
      // At the root, `..` has nowhere to go and Go's Clean drops it.
      if (out.length > 0 && out[out.length - 1] !== "..") out.pop();
      else if (!rooted) out.push("..");
      continue;
    }
    out.push(segment);
  }

  const joined = out.join("/");
  if (rooted) return `/${joined}`;
  return joined === "" ? "." : joined;
}
