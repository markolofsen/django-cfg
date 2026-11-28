/**
 * Human-check gate: configuration types and defaults.
 *
 * Off by default. The gate is a request, not a wall: the enforcement is the
 * server-verified Turnstile cookie, the visible text only asks cooperating
 * agents to stop. See `@dev/planned/bot-check-gate/PLAN.md`.
 */

export type HumanCheckLocale = 'en' | 'ru';

export interface HumanCheckMessages {
  title: string;
  /** Stop text for agents. Rendered server-side, before any script. */
  stop: string;
  /** Text for people. */
  human: string;
  checking: string;
  verifying: string;
  done: string;
  failed: string;
  blocked: string;
  misconfigured: string;
  noscript: string;
}

export type ScopeRule = 'site' | { include: string[]; exclude?: string[] };

export type HumanCheckScope =
  | { kind: 'site' }
  | { kind: 'routes'; include: string[]; exclude?: string[] }
  /** Per host. A host that is not listed is NOT gated (e.g. the marketing host). */
  | { kind: 'hosts'; hosts: Record<string, ScopeRule> };

export interface HumanCheckConfig {
  /** Master switch. Default false. */
  enabled?: boolean;
  /**
   * `production` (default): the gate never runs when `isDev` from
   * `@djangocfg/api` is true. `all`: it runs in development too.
   * Note `NODE_ENV=production` is also what staging builds use; limit staging
   * with `scope: { kind: 'hosts' }`.
   */
  enabledIn?: 'production' | 'all';
  scope?: HumanCheckScope;
  /** Path of the gate route, served by the proxy itself. Default `/__human-check`. */
  gatePath?: string;
  message?: {
    mode?: 'agent-visible' | 'plain';
    /** Per-locale overrides. */
    overrides?: Partial<Record<HumanCheckLocale, Partial<HumanCheckMessages>>>;
    defaultLocale?: HumanCheckLocale;
  };
  cookie?: {
    name?: string;
    ttlSeconds?: number;
    /** Env var holding the signing secret. Comma-separated: first signs, all verify (rotation). */
    secretEnv?: string;
  };
  turnstile?: {
    siteKeyEnv?: string;
    secretKeyEnv?: string;
    /** Informational: the mode is a property of the widget in Cloudflare. */
    mode?: 'non-interactive' | 'managed';
    action?: string;
    /** Hostnames Turnstile may report. Default: the request hostname. */
    hostnames?: string[];
  };
  bypass?: {
    crawlers?: boolean;
    previewBots?: boolean;
    /** Extra always-open paths (same pattern syntax as scope). */
    paths?: string[];
    /** Crawler IP lists (JSON with `prefixes`). Default: Google and Bing lists. */
    crawlerSources?: string[];
    /**
     * When no crawler list has ever loaded: `allow-claimed` (default) lets a
     * UA that claims to be a crawler through, so an outage cannot de-index the
     * site; `gate` gates it.
     */
    onListUnavailable?: 'allow-claimed' | 'gate';
    /** Trust `cf-connecting-ip` (only when the origin accepts Cloudflare traffic only). */
    trustCloudflareIp?: boolean;
  };
  /** `private` (default): in-scope responses get `Cache-Control: private, no-store`. `leave`: do not touch. */
  cache?: 'private' | 'leave';
}

export interface ResolvedHumanCheckConfig {
  enabled: boolean;
  enabledIn: 'production' | 'all';
  scope: HumanCheckScope;
  gatePath: string;
  message: { mode: 'agent-visible' | 'plain'; overrides: Partial<Record<HumanCheckLocale, Partial<HumanCheckMessages>>>; defaultLocale: HumanCheckLocale };
  cookie: { name: string; ttlSeconds: number; secretEnv: string };
  turnstile: { siteKeyEnv: string; secretKeyEnv: string; mode: 'non-interactive' | 'managed'; action: string; hostnames?: string[] };
  bypass: {
    crawlers: boolean;
    previewBots: boolean;
    paths: string[];
    crawlerSources: string[];
    onListUnavailable: 'allow-claimed' | 'gate';
    trustCloudflareIp: boolean;
  };
  cache: 'private' | 'leave';
}

export const DEFAULT_CRAWLER_SOURCES = [
  'https://developers.google.com/static/search/apis/ipranges/googlebot.json',
  'https://developers.google.com/static/search/apis/ipranges/special-crawlers.json',
  'https://developers.google.com/static/search/apis/ipranges/user-triggered-fetchers.json',
  'https://developers.google.com/static/search/apis/ipranges/user-triggered-fetchers-google.json',
  'https://www.bing.com/toolbox/bingbot.json',
];

/** Paths that are never gated: crawl infrastructure, assets, OG images, health, webhooks. */
export const ALWAYS_OPEN_PATHS = [
  '/robots.txt',
  '/sitemap.xml',
  '/sitemap*',
  '/favicon.ico',
  '/.well-known/*',
  '/_next/*',
  '/api/og/*',
  '/health',
  '/healthz',
  '/api/health',
  '/api/webhooks/*',
];

export function resolveConfig(c: HumanCheckConfig = {}): ResolvedHumanCheckConfig {
  const gatePath = c.gatePath ?? '/__human-check';
  if (!gatePath.startsWith('/') || gatePath.startsWith('//')) {
    throw new Error(`human-check: gatePath must be an absolute path, got "${gatePath}"`);
  }
  return {
    enabled: c.enabled ?? false,
    enabledIn: c.enabledIn ?? 'production',
    scope: c.scope ?? { kind: 'site' },
    gatePath,
    message: {
      mode: c.message?.mode ?? 'agent-visible',
      overrides: c.message?.overrides ?? {},
      defaultLocale: c.message?.defaultLocale ?? 'en',
    },
    cookie: {
      name: c.cookie?.name ?? '__hc',
      ttlSeconds: c.cookie?.ttlSeconds ?? 86400,
      secretEnv: c.cookie?.secretEnv ?? 'HUMAN_CHECK_SECRET',
    },
    turnstile: {
      siteKeyEnv: c.turnstile?.siteKeyEnv ?? 'NEXT_PUBLIC_TURNSTILE_SITE_KEY',
      secretKeyEnv: c.turnstile?.secretKeyEnv ?? 'TURNSTILE_SECRET_KEY',
      mode: c.turnstile?.mode ?? 'non-interactive',
      action: c.turnstile?.action ?? 'human-check',
      hostnames: c.turnstile?.hostnames,
    },
    bypass: {
      crawlers: c.bypass?.crawlers ?? true,
      previewBots: c.bypass?.previewBots ?? true,
      paths: c.bypass?.paths ?? [],
      crawlerSources: c.bypass?.crawlerSources ?? DEFAULT_CRAWLER_SOURCES,
      onListUnavailable: c.bypass?.onListUnavailable ?? 'allow-claimed',
      trustCloudflareIp: c.bypass?.trustCloudflareIp ?? false,
    },
    cache: c.cache ?? 'private',
  };
}
