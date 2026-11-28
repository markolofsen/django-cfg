/**
 * Verified-crawler matcher: IP ranges from the crawlers' own published JSON
 * lists. A User-Agent alone proves nothing, so a UA that claims to be a
 * crawler but comes from outside the ranges is gated.
 *
 * Edge-safe: no Node APIs. State lives in the closure (one per isolate).
 * A failed refresh keeps the last good list; an alert fires when the list is
 * older than `staleAfterMs`.
 */

export interface Cidr {
  v: 4 | 6;
  net: bigint;
  bits: number;
}

export function parseIp(input: string): { v: 4 | 6; n: bigint } | null {
  const s = input.trim().replace(/^\[|\]$/g, '').split('%')[0] ?? '';
  if (s.includes('.') && !s.includes(':')) return parseV4(s);
  if (s.includes(':')) {
    const mapped = /^(?:::ffff:)(\d+\.\d+\.\d+\.\d+)$/i.exec(s);
    if (mapped) return parseV4(mapped[1] ?? '');
    return parseV6(s);
  }
  return null;
}

function parseV4(s: string) {
  const p = s.split('.');
  if (p.length !== 4) return null;
  let n = 0n;
  for (const part of p) {
    if (!/^\d{1,3}$/.test(part) || Number(part) > 255) return null;
    n = (n << 8n) | BigInt(part);
  }
  return { v: 4 as const, n };
}

function parseV6(s: string) {
  const halves = s.split('::');
  if (halves.length > 2) return null;
  const head = halves[0] ? halves[0].split(':') : [];
  const tail = halves.length === 2 && halves[1] ? halves[1].split(':') : [];
  const missing = 8 - head.length - tail.length;
  if (halves.length === 1 ? head.length !== 8 : missing < 1) return null;
  const groups = halves.length === 1 ? head : [...head, ...Array(missing).fill('0'), ...tail];
  let n = 0n;
  for (const g of groups) {
    if (!/^[0-9a-f]{1,4}$/i.test(g)) return null;
    n = (n << 16n) | BigInt(`0x${g}`);
  }
  return { v: 6 as const, n };
}

export function parseCidr(s: string): Cidr | null {
  const [addr = '', len] = s.split('/');
  const ip = parseIp(addr);
  if (!ip) return null;
  const max = ip.v === 4 ? 32 : 128;
  const bits = len === undefined ? max : Number(len);
  if (!Number.isInteger(bits) || bits < 0 || bits > max) return null;
  return { v: ip.v, net: ip.n, bits };
}

export function inCidr(ip: { v: 4 | 6; n: bigint }, c: Cidr): boolean {
  if (ip.v !== c.v) return false;
  const total = ip.v === 4 ? 32n : 128n;
  const shift = total - BigInt(c.bits);
  return ip.n >> shift === c.net >> shift;
}

/** `{ prefixes: [{ ipv4Prefix } | { ipv6Prefix }] }`, the format Google and Bing publish. */
export function parseRanges(json: unknown): Cidr[] {
  const out: Cidr[] = [];
  const prefixes = (json as { prefixes?: Array<{ ipv4Prefix?: string; ipv6Prefix?: string }> })?.prefixes;
  if (!Array.isArray(prefixes)) return out;
  for (const p of prefixes) {
    const c = parseCidr(p.ipv4Prefix ?? p.ipv6Prefix ?? '');
    if (c) out.push(c);
  }
  return out;
}

const CRAWLER_UA = /googlebot|google-inspectiontool|googleother|storebot-google|adsbot-google|mediapartners-google|apis-google|google-read-aloud|bingbot|adidxbot|bingpreview/i;
const PREVIEW_UA = /telegrambot|slackbot|slack-imgproxy|twitterbot|facebookexternalhit|facebot|linkedinbot|whatsapp|discordbot|skypeuripreview|vkshare/i;

export const claimsCrawler = (ua: string | null) => !!ua && CRAWLER_UA.test(ua);
export const isPreviewBot = (ua: string | null) => !!ua && PREVIEW_UA.test(ua);

export type CrawlerVerdict = 'verified' | 'spoofed' | 'unknown' | 'none';

export interface CrawlerMatcherOptions {
  sources: string[];
  ttlMs?: number;
  staleAfterMs?: number;
  timeoutMs?: number;
  fetch?: typeof fetch;
  now?: () => number;
  /** Called (at most once per hour) when the last good list is older than `staleAfterMs`. */
  onStale?: (ageMs: number) => void;
}

export function createCrawlerMatcher(opts: CrawlerMatcherOptions) {
  const ttl = opts.ttlMs ?? 6 * 3600_000;
  const staleAfter = opts.staleAfterMs ?? 7 * 86400_000;
  const timeout = opts.timeoutMs ?? 2000;
  const now = opts.now ?? Date.now;
  const doFetch = opts.fetch ?? fetch;
  let ranges: Cidr[] = [];
  let loadedAt = 0;
  let attemptedAt = 0;
  let alertedAt = -Infinity;
  let inflight: Promise<void> | null = null;

  async function refresh() {
    attemptedAt = now();
    const results = await Promise.allSettled(
      opts.sources.map(async (url) => {
        const res = await doFetch(url, { signal: AbortSignal.timeout(timeout) });
        if (!res.ok) throw new Error(`${url}: ${res.status}`);
        const list = parseRanges(await res.json());
        if (list.length === 0) throw new Error(`${url}: no prefixes`);
        return list;
      }),
    );
    const fresh = results.flatMap((r) => (r.status === 'fulfilled' ? r.value : []));
    // Replace only when every source answered: a partial list would silently drop a crawler.
    if (results.every((r) => r.status === 'fulfilled') && fresh.length > 0) {
      ranges = fresh;
      loadedAt = now();
    } else if (loadedAt === 0 && fresh.length > 0) {
      ranges = fresh; // first load, partial beats nothing
      loadedAt = now();
    }
  }

  async function ensure() {
    const t = now();
    if (loadedAt === 0 || t - attemptedAt > ttl) {
      inflight ??= refresh().finally(() => {
        inflight = null;
      });
      await inflight;
    }
    if (loadedAt > 0 && now() - loadedAt > staleAfter && now() - alertedAt > 3600_000) {
      alertedAt = now();
      (opts.onStale ?? ((age) => console.error(`[human-check] crawler IP list is ${Math.round(age / 86400_000)} days old; Googlebot/Bingbot may be gated`)))(now() - loadedAt);
    }
  }

  return {
    /** `verified`: IP is in a published range. `spoofed`: UA claims a crawler, lists loaded, IP not in them. `unknown`: UA claims a crawler, no list ever loaded. `none`: not a crawler claim and not in ranges. */
    async check(ip: string | null, ua: string | null): Promise<CrawlerVerdict> {
      const claims = claimsCrawler(ua);
      await ensure();
      const parsed = ip ? parseIp(ip) : null;
      if (parsed && ranges.some((c) => inCidr(parsed, c))) return 'verified';
      if (!claims) return 'none';
      return loadedAt === 0 ? 'unknown' : 'spoofed';
    },
    state: () => ({ loadedAt, attemptedAt, ranges: ranges.length }),
  };
}

export type CrawlerMatcher = ReturnType<typeof createCrawlerMatcher>;
