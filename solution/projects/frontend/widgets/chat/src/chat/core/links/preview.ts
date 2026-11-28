// The title and icon of a link, as a host resolves them. Pure data and checks; the fetching is the host's
// (`ChatCapabilities.links`), the drawing is `content/chat-link`. No React and no network here.

/** What a host knows about a page. `favicon` is an inline image (`data:`), never an address the browser would have to contact. */
export interface LinkPreview {
  readonly title: string;
  /** The site's own name, when it states one. */
  readonly siteName?: string;
  readonly favicon?: string;
}

/**
 * Looks one web address up. Resolves to `undefined` when there is nothing to show (a private page, a failure, a limit): the chip
 * then keeps the short address. Never rejects the render; a rejection is treated as `undefined`.
 */
export type ResolveLinkPreview = (url: string, signal?: AbortSignal) => Promise<LinkPreview | undefined>;

/**
 * Titles and icons for the links in a message.
 *
 * Absent ⇒ a link is only its short address and the chat makes no request, which is the right default: a lookup leaves the
 * device, so only a host that has a server it trusts for it passes one.
 */
export interface LinksCapability {
  readonly preview?: ResolveLinkPreview;
}

/** Only https addresses are looked up; the server refuses the rest, and asking would only spend its budget. */
export function previewable(href: string): boolean {
  return /^https:\/\//i.test(href);
}

const ICON = /^data:image\/(?:png|gif|jpeg|webp|x-icon|svg\+xml);base64,[A-Za-z0-9+/]+={0,2}$/;

/** An icon is drawn only if it is an inline image of a plain kind, whatever the host handed over. */
export function safeIcon(favicon: string | undefined): string | undefined {
  return favicon !== undefined && favicon.length <= 40_000 && ICON.test(favicon) ? favicon : undefined;
}

/** `www.example.com` → `example.com`: the host as a reader names it. */
export function linkHost(href: string): string {
  try {
    return new URL(href).hostname.replace(/^www\./i, "");
  } catch {
    return "";
  }
}

/** A title worth showing: one plain line, not just the address again. */
export function usableTitle(preview: LinkPreview | undefined): string | undefined {
  const title = preview?.title.replace(/\s+/g, " ").trim();
  return title === undefined || title === "" ? undefined : title.slice(0, 140);
}
