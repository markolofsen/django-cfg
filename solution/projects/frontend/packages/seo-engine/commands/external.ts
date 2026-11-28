/**
 * External-link liveness check (network). Probes every distinct http(s) URL
 * authored in the content tree (MDX + `_meta.ts` href entries), with bounded
 * concurrency, a HEAD→GET fallback, and a per-run cache so each URL is hit once.
 *
 * A URL is "dead" on a 4xx/5xx final status or a network/DNS/timeout error.
 * 401/403/429 are reported but NOT counted dead — they usually mean bot
 * protection, not a broken link.
 */
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import fg from 'fast-glob';
import { extractExternalRefs } from '../core/extract.js';
import type { ExternalCheck, ExternalRef, ExternalResult, NextraSeoConfig } from '../core/types.js';

export interface ExternalOptions {
  concurrency: number;
  timeoutMs: number;
  /** User-agent for probes; defaults to the project name from config. */
  userAgent?: string;
}

const META_HREF_RE = /href\s*:\s*['"`](https?:\/\/[^'"`]+)['"`]/g;

/** Pull `href: 'https://…'` URLs out of the content tree's `_meta.ts` files. */
async function metaExternalRefs(contentRoot: string): Promise<ExternalRef[]> {
  const metas = await fg('**/_meta.{ts,js,json}', { cwd: contentRoot, absolute: true });
  const out: ExternalRef[] = [];
  for (const file of metas) {
    const src = await readFile(file, 'utf8');
    let m: RegExpExecArray | null;
    META_HREF_RE.lastIndex = 0;
    while ((m = META_HREF_RE.exec(src))) {
      const line = src.slice(0, m.index).split('\n').length;
      out.push({ url: m[1], file, line });
    }
  }
  return out;
}

/** Probe one URL: HEAD first, fall back to GET if HEAD is rejected/!ok. */
async function probe(url: string, timeoutMs: number, userAgent: string): Promise<{ status: number; note?: string }> {
  const attempt = async (method: 'HEAD' | 'GET') => {
    const ctrl = new AbortController();
    const t = setTimeout(() => ctrl.abort(), timeoutMs);
    try {
      const res = await fetch(url, {
        method,
        redirect: 'follow',
        signal: ctrl.signal,
        headers: { 'user-agent': userAgent },
      });
      return { status: res.status };
    } finally {
      clearTimeout(t);
    }
  };

  try {
    const head = await attempt('HEAD');
    // Some servers don't implement HEAD (405) or block it (403/400) — retry GET.
    if (head.status === 405 || head.status === 403 || head.status === 400 || head.status >= 500) {
      try {
        const get = await attempt('GET');
        return { status: get.status };
      } catch {
        return head; // GET failed too; keep the HEAD status
      }
    }
    return head;
  } catch (err: any) {
    const note = err?.name === 'AbortError' ? 'timeout' : (err?.cause?.code ?? err?.code ?? err?.message ?? 'network error');
    return { status: 0, note: String(note) };
  }
}

/** True when a final status (or 0) means the link is broken. */
function isDead(status: number): boolean {
  if (status === 0) return true; // network/DNS/timeout
  if (status === 401 || status === 403 || status === 429) return false; // bot-protection, not broken
  return status >= 400;
}

export async function checkExternal(
  config: NextraSeoConfig,
  opts: ExternalOptions,
): Promise<ExternalResult> {
  const contentRoot = resolve(process.cwd(), config.contentDir);
  const userAgent = opts.userAgent ?? `Mozilla/5.0 (compatible; ${config.name}/1.0; +link-check)`;

  const files = await fg('**/*.{mdx,md}', {
    cwd: contentRoot,
    ignore: ['**/node_modules/**', ...config.ignore],
    absolute: true,
  });

  // Gather every external ref (first occurrence per URL wins for reporting location).
  const refs: ExternalRef[] = [];
  for (const file of files) refs.push(...(await extractExternalRefs(file)));
  refs.push(...(await metaExternalRefs(contentRoot)));

  // All locations per URL — so a dead URL surfaces EVERY file/line that uses it,
  // not just the first (a fix sweep needs the full list).
  const refsOf = new Map<string, ExternalRef[]>();
  for (const r of refs) {
    const arr = refsOf.get(r.url) ?? [];
    arr.push(r);
    refsOf.set(r.url, arr);
  }
  const urls = [...refsOf.keys()];

  // Bounded-concurrency probe (each distinct URL hit once).
  const dead: ExternalCheck[] = [];
  let i = 0;
  async function worker() {
    while (i < urls.length) {
      const url = urls[i++];
      const { status, note } = await probe(url, opts.timeoutMs, userAgent);
      if (isDead(status)) {
        for (const ref of refsOf.get(url)!) dead.push({ ...ref, status, dead: true, note });
      }
    }
  }
  await Promise.all(Array.from({ length: Math.min(opts.concurrency, urls.length || 1) }, worker));

  dead.sort((a, b) => a.file.localeCompare(b.file) || a.line - b.line);
  return { total: urls.length, refs: refs.length, dead };
}
