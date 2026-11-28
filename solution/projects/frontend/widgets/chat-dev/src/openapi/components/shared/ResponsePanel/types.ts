import type { Language } from '@djangocfg/widget-kit/pretty-code/lazy';

/** Panels the user can switch between in the response view.
 *
 *   - ``pretty``:  structured rendering — JsonTree for JSON, syntax-
 *                  highlighted code for HTML/XML/CSS/text.
 *   - ``raw``:     plain ``<pre>`` dump of whatever the server returned.
 *   - ``preview``: sandboxed iframe for HTML responses (when you want
 *                  to *see* an error page the server produced rather
 *                  than read its source). Tab is hidden for non-HTML. */
export type ViewMode = 'pretty' | 'raw' | 'preview';

/** Content categories derived from the server's ``Content-Type`` header.
 *  We project the rich MIME type space onto a short enum so the renderer
 *  and tab-list only have to switch on a handful of values. */
export type ContentKind = 'json' | 'html' | 'xml' | 'css' | 'javascript' | 'text';

export interface DetectedContent {
    kind: ContentKind;
    /** Prism ``Language`` id matching ``kind`` — fed into PrettyCode. */
    prism: Language;
    /** Full Content-Type header value, stripped of parameters (e.g.
     *  ``application/json`` without ``; charset=utf-8``). ``null`` when
     *  the server didn't send one. */
    contentType: string | null;
}
