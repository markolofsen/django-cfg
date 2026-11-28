/**
 * Which links in a message body read as a bare reference, and what a compact
 * label for one looks like.
 *
 * A bare url and `[the docs](…)` are indistinguishable in the tree: both are an
 * ordinary mdast `link`, and their hast properties are byte-identical. There is
 * no autolink marker to read. The signal is the CHILD — an autolink's sole text
 * child equals its url.
 *
 * Label shape adapted from the retired `@djangocfg/ui-tools`
 * (`src/tools/forms/MarkdownEditor/url/detect.ts`) (`splitUrl`, `normalizeHref`,
 * the Chrome-omnibox form). `truncateUrlLabel` is reworked here; `faviconUrl`
 * does not come across — it would make a third-party request per link.
 */

const ELLIPSIS = "…";

/** Default budget for a whole label. Wide enough for `domain/first/…/last`. */
const DEFAULT_MAX_CHARS = 40;

/** A url split into the parts a label is built from. */
export interface SplitUrl {
  /** Host without a leading `www.`. Empty when unparseable. */
  readonly domain: string;
  /** Path segments, empty ones dropped. */
  readonly segments: readonly string[];
  /** `#fragment` including the hash, or empty. */
  readonly hash: string;
  /** `mailto:` address without the scheme, or empty. */
  readonly mail: string;
}

/** Prepend a scheme to a schemeless `www.` host so `URL` can parse it. */
export function normalizeHref(raw: string): string {
  if (/^www\./i.test(raw)) return `https://${raw}`;
  return raw;
}

/**
 * Split an href into the label's parts.
 *
 * The hash is its OWN field, not fused into the path: that is what lets a label
 * shed a fragment before it sheds a path segment.
 */
export function splitUrl(href: string): SplitUrl {
  if (/^mailto:/i.test(href)) {
    const mail = href.slice("mailto:".length);
    const at = mail.lastIndexOf("@");
    return {
      domain: at >= 0 ? mail.slice(at + 1) : "",
      segments: [],
      hash: "",
      mail,
    };
  }
  try {
    const u = new URL(normalizeHref(href));
    return {
      domain: u.hostname.replace(/^www\./i, ""),
      segments: `${u.pathname}${u.search}`.split("/").filter((s) => s.length > 0),
      hash: u.hash,
      mail: "",
    };
  } catch {
    // A label is presentation and must not throw on a token `URL` refuses.
    const noScheme = normalizeHref(href).replace(/^[a-z][a-z0-9+.-]*:\/\//i, "");
    const hashAt = noScheme.indexOf("#");
    const body = hashAt >= 0 ? noScheme.slice(0, hashAt) : noScheme;
    const slash = body.indexOf("/");
    return {
      domain: (slash >= 0 ? body.slice(0, slash) : body).replace(/^www\./i, ""),
      segments: slash >= 0 ? body.slice(slash).split("/").filter((s) => s.length > 0) : [],
      hash: hashAt >= 0 ? noScheme.slice(hashAt) : "",
      mail: "",
    };
  }
}

/**
 * Join a domain with the segments a candidate keeps.
 *
 * `…` claims something was dropped, so it is emitted only when `total` exceeds
 * what was kept. An unconditional mark reads as correct while standing for
 * nothing.
 */
function join(domain: string, kept: readonly string[], total: number, hash: string): string {
  // The mark sits where the gap is: between two survivors, or leading when only
  // the last survives. Always after `kept[0]` would read as `last/…`.
  const marked =
    total <= kept.length
      ? [...kept]
      : kept.length <= 1
        ? [ELLIPSIS, ...kept]
        : [kept[0] as string, ELLIPSIS, ...kept.slice(1)];
  const body = marked.join("/");
  return `${domain}${body === "" ? "" : `/${body}`}${hash}`;
}

/**
 * A compact, Chrome-omnibox-style label for a url: the domain in full, the
 * path's middle collapsed, the last segment kept.
 *
 * A fragment is shed before a path segment: the last segment names the PAGE, a
 * fragment only locates a spot inside it. Fusing them into one string puts a
 * long fragment on the last segment and forces every candidate over budget.
 *
 * The last resort truncates the last segment and KEEPS it. Never a bare
 * `domain/…`, which identifies nothing when every link shares the domain.
 */
export function linkChipLabel(href: string, maxChars: number = DEFAULT_MAX_CHARS): string {
  const { domain, segments, hash, mail } = splitUrl(href);

  if (mail !== "") {
    if (mail.length <= maxChars) return mail;
    return `${ELLIPSIS}${mail.slice(mail.length - (maxChars - 1))}`;
  }

  const total = segments.length;
  if (total === 0) {
    const bare = `${domain}${hash}`;
    return bare.length <= maxChars ? bare : domain;
  }

  const last = segments[total - 1] as string;
  const first = segments[0] as string;
  // Widest first, and at each width the fragment goes before a path segment
  // does: `domain/cli/daemon/service` beats `domain/…/service#install-options`,
  // because the segments name the page and the fragment only locates a spot
  // inside it.
  const kept: readonly (readonly string[])[] = [
    segments,
    total >= 3 ? [first, last] : segments,
    [last],
  ];
  const candidates: readonly string[] = kept.flatMap((k) => [
    join(domain, k, total, hash),
    join(domain, k, total, ""),
  ]);
  for (const candidate of candidates) {
    if (candidate.length <= maxChars) return candidate;
  }

  // Nothing fit, so the last segment is itself too long. Keep the page's own
  // name, cut to what the domain leaves, so two links into the same domain
  // still read differently. The leading mark is still conditional: a
  // single-segment path dropped nothing, and claiming otherwise is the same
  // lie `join` exists to prevent.
  const lead = total > 1 ? `${ELLIPSIS}/` : "";
  const room = Math.max(4, maxChars - domain.length - lead.length - 2);
  return `${domain}/${lead}${last.slice(0, room)}${ELLIPSIS}`;
}

/**
 * Whether an anchor is a BARE url — the reader faces the raw string, with no
 * label the author chose.
 *
 * `text` is the anchor's sole text child, or undefined when the child is not a
 * lone text node. A formatted label (`**…**`, inline code, several children)
 * is never bare: the author who formatted a label meant it to read inline.
 *
 * The comparison runs on a normalised form so a schemeless `www.` host still
 * matches: gfm rewrites the URL and leaves the text alone, so raw equality
 * would fail on exactly the shape a model writes when it elides the scheme.
 * One comparison rather than a second rule — one place to be wrong.
 *
 * A label that IS the url counts, though it is technically a markdown link.
 * The rule is about what the READER faces, and that is the same either way.
 */
export function isBareUrlLink(href: string | undefined, text: string | undefined): boolean {
  if (href === undefined || text === undefined) return false;
  const label = text.trim();
  if (label === "") return false;
  return stripScheme(href) === stripScheme(label);
}

/** Drop a leading `http://` or `https://` and any trailing slash. */
function stripScheme(value: string): string {
  return value.replace(/^https?:\/\//i, "").replace(/\/+$/, "");
}

/**
 * Whether an href is a web target a new tab makes sense for.
 *
 * An in-app scheme opened with `target="_blank"` spawns a blank tab
 * the browser cannot navigate. This is about the navigation target, not about
 * safety — `rehype-harden` already decides which protocols survive at all.
 */
export function isExternalHref(href: string | undefined): boolean {
  if (href === undefined) return false;
  return /^(https?|mailto|tel):/i.test(href);
}
