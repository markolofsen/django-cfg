/**
 * Global runtime log-level control.
 *
 * One mutable level that every `@djangocfg/*` consola wrapper reads, so the
 * whole app's console verbosity can be changed at runtime (e.g. raised for an
 * admin, kept silent for a regular user in production) WITHOUT each package
 * hardcoding `isDev ? 4 : 1`.
 *
 * Lives in `@djangocfg/api` because it's the lowest shared package — api,
 * layouts, ui-core consumers can all import it without a cycle.
 *
 * consola levels: 0 silent · 1 error · 2 warn · 3 info · 4 debug · 5 trace.
 *
 * Default policy (before anyone calls setLogLevel):
 *   - dev / static build → 4 (debug)
 *   - production         → 1 (errors only)
 * App bootstrap should call `applyRoleLogPolicy({ isAdmin, isDev })` once auth
 * is known to raise verbosity for staff/superusers even in production.
 */

import { isDev, isStaticBuild } from './auth/utils/env';

export type ConsolaLevel = 0 | 1 | 2 | 3 | 4 | 5;

/** Dev or a static export → show verbose logs by default. */
const verboseByDefault = isDev || isStaticBuild;

const DEFAULT_LEVEL: ConsolaLevel = verboseByDefault ? 4 : 1;

let _level: ConsolaLevel = DEFAULT_LEVEL;

/** Subscribers (the wrapper loggers) notified when the level changes. */
const _subscribers = new Set<(level: ConsolaLevel) => void>();

/** Current global log level. Wrappers read this when constructing/refreshing. */
export function getLogLevel(): ConsolaLevel {
  return _level;
}

/** Set the global log level and notify all live loggers. */
export function setLogLevel(level: ConsolaLevel): void {
  _level = level;
  for (const fn of _subscribers) {
    try {
      fn(level);
    } catch {
      /* a bad subscriber must not break logging */
    }
  }
}

/**
 * Subscribe to level changes. Returns an unsubscribe fn. The callback fires
 * immediately with the current level so a logger can sync on registration.
 */
export function onLogLevelChange(fn: (level: ConsolaLevel) => void): () => void {
  _subscribers.add(fn);
  try {
    fn(_level);
  } catch {
    /* ignore */
  }
  return () => _subscribers.delete(fn);
}

/**
 * Apply the role-aware policy. Call once at bootstrap and whenever auth changes.
 *
 *   - admin (is_staff / is_superuser): full verbosity (debug) everywhere, even
 *     in production — so support/devs can diagnose live without a redeploy.
 *   - dev (non-admin): debug.
 *   - production regular user: errors only — a clean console, like big SaaS apps.
 */
export function applyRoleLogPolicy(opts: { isAdmin: boolean; isDev?: boolean }): void {
  const devMode = opts.isDev ?? verboseByDefault;
  if (opts.isAdmin || devMode) {
    setLogLevel(4);
  } else {
    setLogLevel(1);
  }
}
