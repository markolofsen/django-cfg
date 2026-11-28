'use client';

import { Info, ShieldCheck } from 'lucide-react';
import { useMemo } from 'react';

interface PreviewViewProps {
    html: string;
}

/** Heuristic: does ``html`` look like a JS-only single-page app shell?
 *
 *  SPAs (Vite, CRA, Next-app dev index) ship a near-empty ``<body>``
 *  with a mount div + a ``<script type="module">`` that hydrates the
 *  page at runtime. Previewing those in a ``sandbox=""`` iframe is
 *  pointless because scripts can't run — the reader sees a blank
 *  page and assumes preview is broken.
 *
 *  We detect this by extracting body content, stripping scripts, and
 *  checking what's left. If it's basically just a mount div, we show
 *  an explanatory empty-state instead of an empty iframe. */
function looksLikeSpaShell(html: string): boolean {
    const bodyMatch = html.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    const bodyContent = (bodyMatch?.[1] ?? html)
        // Strip all script tags with their contents — runtime-only code
        // doesn't count as visible markup for this check.
        .replace(/<script[\s\S]*?<\/script>/gi, '')
        // Strip comments.
        .replace(/<!--[\s\S]*?-->/g, '')
        .trim();

    if (bodyContent.length === 0) return true;

    // A single empty container (``<div id="root"></div>`` and friends)
    // is the classic SPA mount point. Anything else — including static
    // server-rendered pages with real content — won't match.
    const singleEmptyContainer = /^<(div|main|section)[^>]*>\s*<\/\1>$/i;
    if (singleEmptyContainer.test(bodyContent)) return true;

    return false;
}

/** Render an HTML response inside a sandboxed iframe so the reader can
 *  see what the server's error page or template actually looks like.
 *
 *  Security model — ``sandbox`` is intentionally **empty**:
 *    - no ``allow-scripts`` → JavaScript in the response cannot run
 *    - no ``allow-same-origin`` → the page can't read parent cookies
 *    - no ``allow-forms`` / ``allow-popups`` → can't phish the user
 *
 *  We feed the HTML via ``srcDoc`` (not ``src``) so we never issue a
 *  network request to render it — the string is already local. */
export function PreviewView({ html }: PreviewViewProps) {
    const isSpaShell = useMemo(() => looksLikeSpaShell(html), [html]);

    if (!html) {
        return (
            <div className="py-10 text-center text-xs text-muted-foreground">
                Empty response body
            </div>
        );
    }

    if (isSpaShell) {
        return (
            <div className="flex flex-col items-center justify-center py-16 px-6 text-center gap-3 min-h-[400px]">
                <div className="inline-flex items-center justify-center h-10 w-10 rounded-full bg-muted">
                    <Info className="h-5 w-5 text-muted-foreground" />
                </div>
                <div className="max-w-sm space-y-1.5">
                    <p className="text-sm font-medium text-foreground">
                        Looks like a single-page app shell
                    </p>
                    <p className="text-xs text-muted-foreground leading-relaxed">
                        This page renders its content with JavaScript at runtime.
                        Scripts are disabled in the sandbox, so Preview would show
                        a blank page. Switch to <strong>Pretty</strong> or{' '}
                        <strong>Raw</strong> to inspect the HTML source.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full min-h-[400px]">
            <div className="shrink-0 flex items-center gap-1.5 px-3 py-1.5 bg-muted/30 border-b text-[10px] text-muted-foreground/70">
                <ShieldCheck className="h-3 w-3" />
                Sandboxed preview — scripts, forms and popups are disabled
            </div>
            {/*
              * Checker-pattern background so "black on black" responses
              * still show a clear iframe bounding box, and so readers
              * can tell the iframe has loaded even if the page itself
              * is empty / fully transparent.
              */}
            <div
                className="flex-1 min-h-[360px] p-2"
                style={{
                    backgroundColor: '#fff',
                    backgroundImage:
                        'linear-gradient(45deg, #f3f4f6 25%, transparent 25%), linear-gradient(-45deg, #f3f4f6 25%, transparent 25%), linear-gradient(45deg, transparent 75%, #f3f4f6 75%), linear-gradient(-45deg, transparent 75%, #f3f4f6 75%)',
                    backgroundSize: '16px 16px',
                    backgroundPosition: '0 0, 0 8px, 8px -8px, -8px 0px',
                }}
            >
                <iframe
                    title="Response preview"
                    srcDoc={html}
                    sandbox=""
                    className="w-full h-full min-h-[360px] bg-white border-0 rounded shadow-sm"
                />
            </div>
        </div>
    );
}
