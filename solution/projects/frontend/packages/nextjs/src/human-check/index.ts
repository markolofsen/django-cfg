/**
 * Human-check gate (opt-in, off by default). See `./proxy.ts`.
 */
export { createHumanCheck, withHumanCheck, clientIp } from './proxy';
export type { HumanCheck, HumanCheckDeps, HumanCheckDecision } from './proxy';
export { resolveConfig, DEFAULT_CRAWLER_SOURCES, ALWAYS_OPEN_PATHS } from './types';
export type { HumanCheckConfig, HumanCheckScope, ScopeRule, HumanCheckMessages, HumanCheckLocale } from './types';
export { MESSAGES } from './messages';
export { renderHumanCheckHtml } from './page';
export { inScope, matchPath, matchHost, safeNext } from './scope';
export { createCrawlerMatcher, claimsCrawler, isPreviewBot } from './crawlers';
export type { CrawlerMatcher, CrawlerVerdict } from './crawlers';
export { signClearance, verifyClearance } from './cookie';
export { verifyTurnstile } from './turnstile';
