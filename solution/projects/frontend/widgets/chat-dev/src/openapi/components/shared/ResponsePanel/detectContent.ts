import type { ContentKind, DetectedContent } from './types';

/** Strip Content-Type parameters (``; charset=utf-8`` etc.) and lower-case. */
function normaliseContentType(raw: string | null): string | null {
    if (!raw) return null;
    const semi = raw.indexOf(';');
    return (semi === -1 ? raw : raw.slice(0, semi)).trim().toLowerCase();
}

/** Pull Content-Type out of the headers bag. We accept both plain
 *  objects (``{ "content-type": "..." }``) and ``Headers``-like shapes
 *  with a ``.get`` method. The context type is ``any`` so we can't be
 *  stricter without plumbing a proper type through the response code
 *  path. */
function readContentType(headers: unknown): string | null {
    if (!headers) return null;
    // Headers instance — use ``.get`` (case-insensitive).
    if (typeof (headers as Headers).get === 'function') {
        return (headers as Headers).get('content-type');
    }
    // Plain object — look up with case-insensitive key match so both
    // ``Content-Type`` and ``content-type`` work.
    if (typeof headers === 'object') {
        for (const [k, v] of Object.entries(headers as Record<string, unknown>)) {
            if (k.toLowerCase() === 'content-type') {
                return typeof v === 'string' ? v : null;
            }
        }
    }
    return null;
}

/** Map a normalised MIME type to our short ``ContentKind``. Unknown
 *  types fall back to ``text`` so PrettyCode still shows something
 *  sensible (plain text is a valid Prism language). */
function kindFromContentType(mime: string | null): ContentKind {
    if (!mime) return 'text';
    if (mime === 'application/json' || mime.endsWith('+json')) return 'json';
    if (mime === 'text/html' || mime === 'application/xhtml+xml') return 'html';
    if (
        mime === 'application/xml' ||
        mime === 'text/xml' ||
        mime.endsWith('+xml')
    ) return 'xml';
    if (mime === 'text/css') return 'css';
    if (
        mime === 'application/javascript' ||
        mime === 'text/javascript' ||
        mime === 'application/x-javascript'
    ) return 'javascript';
    return 'text';
}

/** Heuristic fallback when ``Content-Type`` is missing or opaque.
 *  Returns ``null`` when nothing firm can be inferred; the caller
 *  then defaults to ``text``. */
function kindFromBody(body: string): ContentKind | null {
    const trimmed = body.trimStart();
    if (!trimmed) return null;
    if (trimmed.startsWith('<!DOCTYPE') || /^<html[\s>]/i.test(trimmed)) return 'html';
    if (trimmed.startsWith('<?xml')) return 'xml';
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        // Cheap validity check — full parse happens in ResponsePanel.
        try { JSON.parse(trimmed); return 'json'; } catch { /* fall through */ }
    }
    return null;
}

const PRISM_BY_KIND: Record<ContentKind, DetectedContent['prism']> = {
    json: 'json',
    // ``markup`` is Prism's HTML/XML grammar — there isn't a separate
    // ``html`` language. XML piggy-backs on the same tokeniser.
    html: 'markup',
    xml: 'markup',
    css: 'css',
    javascript: 'javascript',
    text: 'markup',
};

/** Detect content kind from headers, falling back to body sniffing
 *  when the header is missing. Pure function — safe to call inside
 *  ``useMemo`` deps on the raw body and headers. */
export function detectContent(headers: unknown, rawBody: string): DetectedContent {
    const contentType = normaliseContentType(readContentType(headers));
    const headerKind = kindFromContentType(contentType);

    // If headers say it's text/plain but the body looks like HTML or
    // JSON, trust the body — a lot of framework 500 pages claim
    // text/html but some setups default to text/plain for errors.
    const kind = headerKind === 'text' ? (kindFromBody(rawBody) ?? 'text') : headerKind;

    return {
        kind,
        prism: PRISM_BY_KIND[kind],
        contentType,
    };
}
