import { defaultSchema } from 'rehype-sanitize';

/** Sanitize schema. Typed loosely (`Record<string, unknown>`) so this
 *  package's published types don't try to re-export
 *  `hast-util-sanitize`'s internal Schema type — that breaks consumers
 *  whose TS doesn't have the transitive dependency in scope. */
export type SanitizeSchema = Record<string, unknown>;

// Allow-list HTML that OpenAPI descriptions commonly use — we want
// `<b>`/`<code>`/`<br>` to render, not to appear as literal text.
// Built on top of rehype-sanitize's default schema so we keep the
// XSS protection (no `<script>`, no `on*` handlers, no `javascript:`
// URLs); we just extend the tag allow-list with safe presentational
// elements that are in wide use in API docs.
export const HTML_SCHEMA_BASE: SanitizeSchema = {
  ...defaultSchema,
  tagNames: [
    ...(defaultSchema.tagNames ?? []),
    'br',
    'b',
    'i',
    'u',
    's',
    'sub',
    'sup',
    'small',
    'mark',
    'kbd',
    'code',
    'pre',
    'details',
    'summary',
  ],
};

/** Build a sanitize schema with extra href-URL protocols allowed on
 *  `<a>`. Default whitelists `http(s)/mailto/xmpp/irc(s)` — pass extras
 *  here (e.g. `'cmdop'`, `'obsidian'`) to opt them in. */
export function buildSchema(extraProtocols: readonly string[] | undefined): SanitizeSchema {
  if (!extraProtocols || extraProtocols.length === 0) return HTML_SCHEMA_BASE;
  const baseProtocols =
    (HTML_SCHEMA_BASE as { protocols?: Record<string, string[]> }).protocols
    ?? (defaultSchema as { protocols?: Record<string, string[]> }).protocols
    ?? {};
  const baseHref = baseProtocols.href ?? ['http', 'https', 'mailto', 'xmpp', 'irc', 'ircs'];
  return {
    ...HTML_SCHEMA_BASE,
    protocols: {
      ...baseProtocols,
      href: [...baseHref, ...extraProtocols],
    },
  };
}

/** Build a `urlTransform` for ReactMarkdown that lets opted-in schemes
 *  pass through verbatim. react-markdown's default strips `href` for
 *  unrecognised schemes BEFORE sanitize runs — even with our extended
 *  sanitize schema, custom schemes would arrive with `href=""`. */
export function buildUrlTransform(extraProtocols: readonly string[] | undefined) {
  if (!extraProtocols || extraProtocols.length === 0) return undefined;
  const lower = extraProtocols.map((p) => p.toLowerCase() + ':');
  return (url: string): string => {
    const u = url.trim().toLowerCase();
    for (const p of lower) {
      if (u.startsWith(p)) return url;
    }
    // Fallback: replicate react-markdown's defaults for safe schemes
    // and relative paths. Anything else → empty string so the
    // anchor's href is dropped (XSS guard).
    //
    // The bare-name branch must NOT contain `:`. It exists for a relative
    // target like `intro.md`, and with a colon in the class the whole of
    // `javascript:alert(1)` matched it — the guard returned the payload
    // verbatim, which is the one thing this function exists to prevent.
    // (rehype-sanitize's `protocols.href` allow-list caught it downstream, so
    // nothing shipped exploitable; a layer of defence-in-depth that does not
    // defend is still broken.) A scheme is what a colon before the first
    // `/`, `?` or `#` means, so excluding it here leaves relative paths
    // intact and rejects every scheme not named above.
    if (
      /^(https?:|mailto:|tel:|xmpp:|irc:|ircs:|#|\/|\.\/|\.\.\/|\?)/i.test(u)
      || /^[a-z0-9._~!$&'()*+,;=@%-]+$/i.test(u)
    ) {
      return url;
    }
    return '';
  };
}
