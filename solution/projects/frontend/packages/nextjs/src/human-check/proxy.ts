/**
 * Human-check gate for Next.js (proxy / middleware).
 *
 * ```ts
 * // proxy.ts
 * import { createHumanCheck, withHumanCheck } from '@djangocfg/nextjs/human-check';
 *
 * const humanCheck = createHumanCheck({ enabled: true, scope: { kind: 'hosts', hosts: { 'app.example.com': 'site' } } });
 * export default withHumanCheck(humanCheck, intlProxy);
 * ```
 *
 * The proxy serves the gate route itself (GET page, POST verify), so no app
 * route is needed (an `app/__human-check` folder would be a private folder
 * and never routable). Order: disabled -> dev skip -> always-open paths ->
 * gate route -> scope -> crawler/preview bypass -> valid cookie -> 302 to gate.
 */

import { isDev as apiIsDev } from '@djangocfg/api';
import { NextResponse } from 'next/server';

import { parseSecrets, signClearance, verifyClearance } from './cookie';
import { createCrawlerMatcher, isPreviewBot, type CrawlerMatcher } from './crawlers';
import { MESSAGES, pickLocale } from './messages';
import { renderHumanCheckHtml } from './page';
import { ALWAYS_OPEN_PATHS, resolveConfig, type HumanCheckConfig, type ResolvedHumanCheckConfig } from './types';
import { inScope, matchAny, safeNext } from './scope';
import { verifyTurnstile } from './turnstile';

import type { NextRequest } from 'next/server';

export interface HumanCheckDeps {
  /** Test seam. Default: `isDev` from `@djangocfg/api`. */
  isDev?: boolean;
  fetch?: typeof fetch;
  now?: () => number;
  env?: Record<string, string | undefined>;
  crawlers?: CrawlerMatcher;
  log?: (msg: string) => void;
}

export type HumanCheckDecision = 'disabled' | 'dev' | 'open' | 'out-of-scope' | 'crawler' | 'preview' | 'cleared' | 'gate';

const GATE_HEADERS = {
  'Content-Type': 'text/html; charset=utf-8',
  'X-Robots-Tag': 'noindex, nofollow',
  'Cache-Control': 'private, no-store',
  'Referrer-Policy': 'no-referrer',
};

export function clientIp(h: Headers, trustCloudflare: boolean): string | null {
  if (trustCloudflare) {
    const cf = h.get('cf-connecting-ip');
    if (cf) return cf.trim();
  }
  return h.get('x-real-ip')?.trim() ?? h.get('x-forwarded-for')?.split(',')[0]?.trim() ?? null;
}

export function createHumanCheck(userConfig: HumanCheckConfig = {}, deps: HumanCheckDeps = {}) {
  const cfg: ResolvedHumanCheckConfig = resolveConfig(userConfig);
  const env = deps.env ?? process.env;
  const dev = () => deps.isDev ?? apiIsDev;
  const now = deps.now ?? Date.now;
  const log = deps.log ?? ((m: string) => console.error(m));

  /** The dev check comes first, before scope, cookie and Turnstile. */
  const active = () => cfg.enabled && !(dev() && cfg.enabledIn !== 'all');

  const crawlers =
    deps.crawlers ??
    (cfg.bypass.crawlers
      ? createCrawlerMatcher({ sources: cfg.bypass.crawlerSources, fetch: deps.fetch, now: deps.now })
      : null);

  const secrets = () => parseSecrets(env[cfg.cookie.secretEnv]);
  const siteKey = () => env[cfg.turnstile.siteKeyEnv] || null;
  const turnstileSecret = () => env[cfg.turnstile.secretKeyEnv] || null;
  const misconfigured = () => secrets().length === 0 || !siteKey() || !turnstileSecret();

  // Fail closed and loud: gate on, never a silent pass.
  if (active() && misconfigured()) {
    log(
      `[human-check] ENABLED but misconfigured: set ${cfg.cookie.secretEnv}, ${cfg.turnstile.siteKeyEnv} and ${cfg.turnstile.secretKeyEnv}. ` +
        'Every in-scope request will be sent to the gate and no one can pass.',
    );
  }

  const page = (req: NextRequest, status = 200) => {
    const locale = pickLocale(req.nextUrl.searchParams.get('lang'), req.headers.get('accept-language'), cfg.message.defaultLocale);
    const messages = { ...MESSAGES[locale], ...(cfg.message.overrides[locale] ?? {}) };
    const key = misconfigured() ? null : siteKey();
    const html = renderHumanCheckHtml({ locale, messages, mode: cfg.message.mode, siteKey: key, action: cfg.turnstile.action });
    return new NextResponse(req.method === 'HEAD' ? null : html, { status, headers: GATE_HEADERS });
  };

  async function verifyPost(req: NextRequest): Promise<NextResponse> {
    const json = (body: unknown, status: number) =>
      NextResponse.json(body, { status, headers: { 'Cache-Control': 'private, no-store', 'X-Robots-Tag': 'noindex, nofollow' } });
    const origin = req.headers.get('origin');
    if (origin) {
      let host = '';
      try {
        host = new URL(origin).host;
      } catch {
        /* invalid origin falls through to the mismatch below */
      }
      if (host !== req.nextUrl.host) return json({ ok: false, reason: 'bad-origin', retry: false }, 403);
    }
    if (misconfigured()) return json({ ok: false, reason: 'misconfigured', retry: false }, 503);
    let token = '';
    try {
      const body = (await req.json()) as { token?: unknown };
      if (typeof body.token === 'string') token = body.token;
    } catch {
      /* empty token is rejected below */
    }
    if (!token || token.length > 4096) return json({ ok: false, reason: 'no-token', retry: true }, 400);
    const result = await verifyTurnstile({
      secret: turnstileSecret()!,
      token,
      remoteIp: clientIp(req.headers, cfg.bypass.trustCloudflareIp),
      expectedHostnames: cfg.turnstile.hostnames ?? [req.nextUrl.hostname],
      expectedAction: cfg.turnstile.action,
      fetch: deps.fetch,
    });
    if (!result.ok) return json({ ok: false, reason: result.reason, retry: result.retry }, 403);
    const signer = secrets()[0];
    if (!signer) return json({ ok: false, reason: 'misconfigured', retry: false }, 503);
    const value = await signClearance(signer, req.headers.get('user-agent'), cfg.cookie.ttlSeconds, now());
    const res = json({ ok: true, next: safeNext(req.nextUrl.searchParams.get('next'), cfg.gatePath) }, 200);
    res.cookies.set(cfg.cookie.name, value, {
      httpOnly: true,
      secure: req.nextUrl.protocol === 'https:',
      sameSite: 'lax',
      path: '/',
      maxAge: cfg.cookie.ttlSeconds,
    });
    return res;
  }

  async function decide(req: NextRequest): Promise<HumanCheckDecision> {
    if (!cfg.enabled) return 'disabled';
    if (!active()) return 'dev';
    const { pathname } = req.nextUrl;
    if (matchAny(ALWAYS_OPEN_PATHS, pathname) || matchAny(cfg.bypass.paths, pathname)) return 'open';
    if (!inScope(cfg.scope, req.nextUrl.hostname, pathname)) return 'out-of-scope';
    const ua = req.headers.get('user-agent');
    if (cfg.bypass.previewBots && (req.method === 'GET' || req.method === 'HEAD') && isPreviewBot(ua)) return 'preview';
    if (crawlers) {
      const verdict = await crawlers.check(clientIp(req.headers, cfg.bypass.trustCloudflareIp), ua);
      if (verdict === 'verified' || (verdict === 'unknown' && cfg.bypass.onListUnavailable === 'allow-claimed')) return 'crawler';
    }
    if (await verifyClearance(secrets(), req.cookies.get(cfg.cookie.name)?.value, ua, now())) return 'cleared';
    return 'gate';
  }

  /**
   * Returns a response when the gate handles the request (gate page, verify, redirect, or a
   * pass-through with cache headers) and `undefined` when the request is none of its business.
   */
  async function proxy(req: NextRequest): Promise<NextResponse | undefined> {
    const { pathname } = req.nextUrl;
    if (pathname === cfg.gatePath) {
      // Off and dev: the route does not exist.
      if (!active()) return new NextResponse(null, { status: 404, headers: { 'Cache-Control': 'private, no-store' } });
      if (req.method === 'POST') return verifyPost(req);
      if (req.method !== 'GET' && req.method !== 'HEAD') return new NextResponse(null, { status: 405, headers: { Allow: 'GET, HEAD, POST' } });
      if (await verifyClearance(secrets(), req.cookies.get(cfg.cookie.name)?.value, req.headers.get('user-agent'), now())) {
        const to = req.nextUrl.clone();
        const [p, q] = safeNext(req.nextUrl.searchParams.get('next'), cfg.gatePath).split('?');
        to.pathname = p ?? '/';
        to.search = q ? `?${q}` : '';
        return NextResponse.redirect(to, 302);
      }
      return page(req);
    }

    const decision = await decide(req);
    switch (decision) {
      case 'gate': {
        const to = req.nextUrl.clone();
        const next = `${pathname}${req.nextUrl.search}`;
        to.pathname = cfg.gatePath;
        to.search = `?next=${encodeURIComponent(next)}`;
        const res = NextResponse.redirect(to, 302);
        res.headers.set('Cache-Control', 'private, no-store');
        res.headers.set('X-Robots-Tag', 'noindex, nofollow');
        return res;
      }
      case 'crawler':
      case 'preview':
      case 'cleared': {
        if (cfg.cache === 'leave') return undefined;
        // A crawler response must not be cached and served to a human without a cookie.
        const res = NextResponse.next();
        res.headers.set('Cache-Control', 'private, no-store');
        res.headers.append('Vary', 'Cookie, User-Agent');
        return res;
      }
      default:
        return undefined;
    }
  }

  return { proxy, decide, config: cfg };
}

export type HumanCheck = ReturnType<typeof createHumanCheck>;

/** Compose with another proxy (e.g. the i18n one): the gate runs first. */
export function withHumanCheck<A extends unknown[], R>(
  humanCheck: HumanCheck,
  next: (req: NextRequest, ...args: A) => R | Promise<R>,
) {
  return async (req: NextRequest, ...args: A): Promise<NextResponse | R> => (await humanCheck.proxy(req)) ?? next(req, ...args);
}
