/**
 * Installed-app `<meta>` tags, applied by `BaseApp` so an app does not have to remember them.
 *
 * Next's App Router builds `<head>` from the server `viewport` / `metadata` exports; a client component such as
 * `BaseApp` cannot contribute to them, and a second `<meta name="viewport">` would fight Next's own. So this is a tiny
 * inline script (it runs while the HTML is parsed, before first paint) that completes what is missing in `<head>`:
 *
 *   viewport                              + `viewport-fit=cover` (without it every `--safe-*` inset is 0 and the
 *                                           installed iOS app letterboxes)
 *   apple-mobile-web-app-capable          yes   (Next 16 only emits `mobile-web-app-capable`; iOS < 26 needs the apple tag)
 *   mobile-web-app-capable                yes
 *   apple-mobile-web-app-status-bar-style black-translucent
 *
 * Existing tags are never overridden (an app's own `appleWebApp.statusBarStyle` wins); only `viewport-fit` is added to
 * an existing viewport that lacks it. A MutationObserver re-applies it if a client navigation rewrites the viewport tag.
 * Prefer exporting `viewport = createViewport(...)` (default `viewportFit: 'cover'`): that puts it in the server HTML;
 * this is the safety net for apps that forgot.
 */

import * as React from 'react';

export const PWA_META_SCRIPT = `(function(){try{
var d=document,h=d.head;if(!h)return;
function q(n){return h.querySelector('meta[name="'+n+'"]')}
function ensure(n,c){if(!q(n)){var m=d.createElement('meta');m.name=n;m.content=c;h.appendChild(m)}}
function fit(){var v=q('viewport');
if(!v){v=d.createElement('meta');v.name='viewport';v.content='width=device-width, initial-scale=1, viewport-fit=cover';h.appendChild(v);return}
var c=v.getAttribute('content')||'';
if(!/viewport-fit\\s*=/.test(c))v.setAttribute('content',(c?c+', ':'')+'viewport-fit=cover')}
fit();
ensure('apple-mobile-web-app-capable','yes');
ensure('mobile-web-app-capable','yes');
ensure('apple-mobile-web-app-status-bar-style','black-translucent');
if(window.MutationObserver){new MutationObserver(function(){var v=q('viewport');if(!v||!/viewport-fit\\s*=\\s*cover/.test(v.getAttribute('content')||''))fit()}).observe(h,{subtree:true,childList:true,attributes:true,attributeFilter:['content']})}
}catch(e){}})();`;

/** Renders the inline script. Server-rendered into the HTML; React does not re-run it on hydration. */
export function PwaMetaGuard() {
  return <script dangerouslySetInnerHTML={{ __html: PWA_META_SCRIPT }} suppressHydrationWarning />;
}

export const MANIFEST_HINT =
  "[djangocfg] No <link rel=\"manifest\"> in <head>, so the app is not installable. Add app/manifest.ts: " +
  "`import { createManifest } from '@djangocfg/nextjs/pwa/manifest'; export default createManifest({ name, ... })`. " +
  'Disable this check with <BaseApp pwaMeta={false} />.';

/** Pure check: true when the document is available and has no manifest link. */
export function isManifestMissing(doc: Pick<Document, 'head'> | null | undefined): boolean {
  const head = doc?.head;
  if (!head) return false;
  return !head.querySelector('link[rel~="manifest"]');
}

/** Dev-only, once per page load: warns when the app forgot `app/manifest.ts`. Renders nothing. */
export function PwaManifestCheck() {
  React.useEffect(() => {
    if (process.env.NODE_ENV === 'production') return;
    if (typeof document === 'undefined') return;
    const w = window as unknown as { __djangocfgManifestChecked?: boolean };
    if (w.__djangocfgManifestChecked) return;
    w.__djangocfgManifestChecked = true;
    if (isManifestMissing(document)) console.warn(MANIFEST_HINT);
  }, []);
  return null;
}
