/**
 * The decision behind the locale hint: pure, no React, no storage, so every rule is a table row in a test.
 * Product rules and the rejected alternatives: `@dev/active/locale-suggestion/PLAN.md`.
 */

export const DEFAULT_TTL_DAYS = 180;
/** Dismissed pairs kept in storage; the oldest are dropped first. */
export const MAX_PAIRS = 24;
const DAY_MS = 24 * 60 * 60 * 1000;

/** What the browser remembers between visits (stored under `CFG_KEYS.uiLocaleHint`). */
export interface SuggestionMemory {
  v: 1;
  /** The last site locale this browser showed. A different one now means the visitor chose it. */
  seen?: string;
  /** `"<site locale suggested>><site locale shown>"` → when it was dismissed (epoch ms). */
  dismissed: Record<string, number>;
}

export const emptyMemory = (): SuggestionMemory => ({ v: 1, dismissed: {} });

/** Language tags hosts report that name a site locale under another code (same table as `resolveLocale`). */
const ALIASES: Readonly<Record<string, string>> = { nb: 'no', nn: 'no' };

const norm = (tag: string): string => tag.trim().replace('_', '-').toLowerCase();
const baseOf = (tag: string): string => norm(tag).split('-')[0] ?? '';

export interface SiteMatch {
  /** The site's own spelling of the locale (`pt-BR`). */
  locale: string;
  /** The browser tag named this very locale, not just its language. */
  exact: boolean;
}

/**
 * The site locale a browser language tag points at, or `null`.
 * Exact tag, then alias (`nb` → `no`), then the base language (`de-AT` → `de`), then a sibling of the same language
 * (`pt` → `pt-BR`). Chinese siblings are never guessed (`zh-TW` is not `zh-CN`). No "nearest language" beyond that:
 * a language the site does not have is silence, not a guess.
 */
export function matchSiteLocale(tag: string, siteLocales: readonly string[]): SiteMatch | null {
  const wanted = norm(tag);
  if (!wanted) return null;
  const byLower = new Map(siteLocales.map((l) => [norm(l), l] as const));

  const exact = byLower.get(wanted);
  if (exact) return { locale: exact, exact: true };

  const base = baseOf(wanted);
  const aliased = byLower.get(ALIASES[wanted] ?? ALIASES[base] ?? '');
  if (aliased) return { locale: aliased, exact: false };

  const baseHit = byLower.get(base);
  if (baseHit) return { locale: baseHit, exact: false };

  const hasRegion = wanted.includes('-');
  if (base === 'zh' && hasRegion) return null;
  const sibling = siteLocales.find((l) => baseOf(l) === base);
  return sibling ? { locale: sibling, exact: false } : null;
}

export interface CandidateInput {
  /** `navigator.languages`, preferred first. */
  browserLanguages: readonly string[];
  siteLocales: readonly string[];
  /** The locale the page is shown in. */
  current: string;
}

/**
 * The language to offer, ignoring memory. The first browser language the site speaks decides:
 * if that is already the page's language the visitor is served and nothing is offered, even when a lower-ranked
 * language differs. A regional variant of the page's language (`en-GB` on `en`) is not a reason to interrupt,
 * unless the site itself offers that exact variant.
 */
export function suggestLocale({ browserLanguages, siteLocales, current }: CandidateInput): string | null {
  if (siteLocales.length < 2) return null;
  for (const tag of browserLanguages) {
    const hit = matchSiteLocale(tag, siteLocales);
    if (!hit) continue;
    if (norm(hit.locale) === norm(current)) return null;
    if (baseOf(hit.locale) === baseOf(current) && !hit.exact) return null;
    return hit.locale;
  }
  return null;
}

export const pairKey = (suggested: string, current: string): string => `${norm(suggested)}>${norm(current)}`;

/**
 * Memory after this page view. Records `seen`; and when the visitor is on a different locale than last time, they
 * chose it (switcher, URL or our own button), so the pair is closed as if dismissed. Expired and surplus pairs go.
 */
export function reconcileMemory(
  memory: SuggestionMemory,
  input: { current: string; candidate: string | null; now: number; ttlDays?: number },
): SuggestionMemory {
  const ttl = (input.ttlDays ?? DEFAULT_TTL_DAYS) * DAY_MS;
  let dismissed = { ...memory.dismissed };
  if (memory.seen && norm(memory.seen) !== norm(input.current) && input.candidate) {
    dismissed[pairKey(input.candidate, input.current)] = input.now;
  }
  const live = Object.entries(dismissed)
    .filter(([, at]) => input.now - at < ttl)
    .sort((a, b) => b[1] - a[1])
    .slice(0, MAX_PAIRS);
  dismissed = Object.fromEntries(live);
  return { v: 1, seen: input.current, dismissed };
}

/** Memory after the visitor closed the hint for this pair. */
export function dismissPair(
  memory: SuggestionMemory,
  suggested: string,
  current: string,
  now: number,
): SuggestionMemory {
  return { ...memory, dismissed: { ...memory.dismissed, [pairKey(suggested, current)]: now } };
}

export interface DecideInput extends CandidateInput {
  memory: SuggestionMemory;
  now: number;
  ttlDays?: number;
}

/** The locale to offer now, or `null`. */
export function decideSuggestion(input: DecideInput): string | null {
  const candidate = suggestLocale(input);
  if (!candidate) return null;
  const at = input.memory.dismissed[pairKey(candidate, input.current)];
  const ttl = (input.ttlDays ?? DEFAULT_TTL_DAYS) * DAY_MS;
  if (at !== undefined && input.now - at < ttl) return null;
  return candidate;
}

const BOT_UA = /bot|crawl|spider|slurp|headless|lighthouse|pagespeed|preview|monitor|facebookexternalhit|python-requests|curl\//i;

/** Crawlers and automation get no hint: nothing to decide, nothing to render. */
export function isAutomated(userAgent: string | undefined, webdriver: boolean | undefined): boolean {
  return webdriver === true || BOT_UA.test(userAgent ?? '');
}

/** True when `pathname` is covered by an `exclude` entry (string prefix or RegExp). */
export function isExcludedPath(pathname: string, exclude: readonly (string | RegExp)[] | undefined): boolean {
  if (!exclude?.length) return false;
  return exclude.some((rule) => {
    if (typeof rule === 'string') return pathname.startsWith(rule);
    rule.lastIndex = 0;
    return rule.test(pathname);
  });
}
