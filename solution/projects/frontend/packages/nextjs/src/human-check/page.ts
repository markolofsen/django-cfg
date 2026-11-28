import type { HumanCheckLocale, HumanCheckMessages } from './types';

export interface PageOptions {
  locale: HumanCheckLocale;
  messages: HumanCheckMessages;
  mode: 'agent-visible' | 'plain';
  /** Null when the gate is misconfigured: the page then shows the error and no widget. */
  siteKey: string | null;
  action: string;
  /** Minimum time the message stays on screen after success, so a late snapshot still reads it. */
  dwellMs?: number;
}

const esc = (s: string) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');

/** JSON safe inside a <script> element. */
const scriptJson = (v: unknown) =>
  JSON.stringify(v)
    .replace(/</g, '\\u003c')
    .replace(new RegExp(String.fromCharCode(0x2028), 'g'), '\\u2028')
    .replace(new RegExp(String.fromCharCode(0x2029), 'g'), '\\u2029');

const CLIENT = `(function(){
var d=JSON.parse(document.getElementById('hc-data').textContent),m=d.m,s=document.getElementById('hc-status'),t0=Date.now(),id=null;
function say(t){s.textContent=t}
function go(n){setTimeout(function(){location.replace(n)},Math.max(0,d.dwell-(Date.now()-t0)))}
function tok(t){say(m.verifying);
fetch(location.pathname+location.search,{method:'POST',credentials:'same-origin',headers:{'content-type':'application/json'},body:JSON.stringify({token:t})})
.then(function(r){return r.json()}).then(function(j){
if(j&&j.ok){say(m.done);go(j.next)}else{say(m.failed);if(window.turnstile&&id!==null)window.turnstile.reset(id)}})
.catch(function(){say(m.failed);if(window.turnstile&&id!==null)window.turnstile.reset(id)})}
function mount(){if(!window.turnstile)return false;
id=window.turnstile.render('#hc-widget',{sitekey:d.siteKey,action:d.action,appearance:'always',callback:tok,
'error-callback':function(){say(m.blocked)},'expired-callback':function(){if(id!==null)window.turnstile.reset(id)}});return true}
var tries=0,iv=setInterval(function(){if(mount()){clearInterval(iv)}else if(++tries>100){clearInterval(iv);say(m.blocked)}},100);
})();`;

/**
 * Server-rendered gate page. The stop text and the h1 are in the first HTML,
 * before any script, and the same text is repeated in <noscript>. No hidden
 * text, no timers that move the page before verification succeeded.
 */
export function renderHumanCheckHtml(o: PageOptions): string {
  const m = o.messages;
  const agent = o.mode === 'agent-visible';
  const stop = agent ? `<p id="hc-stop">${esc(m.stop)}</p>` : '';
  const widget = o.siteKey
    ? `<div id="hc-widget"></div><p id="hc-status" role="status" aria-live="polite">${esc(m.checking)}</p>`
    : `<p id="hc-status" role="status">${esc(m.misconfigured)}</p>`;
  const scripts = o.siteKey
    ? `<script id="hc-data" type="application/json">${scriptJson({ m: { verifying: m.verifying, done: m.done, failed: m.failed, blocked: m.blocked }, siteKey: o.siteKey, action: o.action, dwell: o.dwellMs ?? 3000 })}</script>` +
      `<script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit" async defer></script>` +
      `<script>${CLIENT}</script>`
    : '';
  return (
    `<!doctype html><html lang="${o.locale}"><head><meta charset="utf-8">` +
    `<meta name="viewport" content="width=device-width,initial-scale=1">` +
    `<meta name="robots" content="noindex,nofollow">` +
    `<title>${esc(m.title)}</title>` +
    `<style>:root{color-scheme:light dark}body{margin:0;font:16px/1.5 system-ui,sans-serif;display:grid;min-height:100vh;place-items:center}` +
    `main{max-width:34rem;padding:1.5rem}h1{font-size:1.5rem;margin:0 0 1rem}p{margin:0 0 1rem}#hc-widget{min-height:65px;margin:1rem 0}</style>` +
    `</head><body><main>` +
    `<h1>${esc(m.title)}</h1>${stop}<p id="hc-human">${esc(m.human)}</p>` +
    `${widget}` +
    `<noscript>${agent ? `<p>${esc(m.stop)}</p>` : ''}<p>${esc(m.noscript)}</p></noscript>` +
    `</main>${scripts}</body></html>`
  );
}
