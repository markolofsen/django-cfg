import type { HumanCheckScope, ScopeRule } from './types';

/**
 * Path pattern: exact (`/pricing`), prefix (`/app/*` matches `/app` and everything under it)
 * or bare-star suffix (`/sitemap*` matches `/sitemap.xml`, `/sitemap-1.xml`).
 */
export function matchPath(pattern: string, pathname: string): boolean {
  if (pattern.endsWith('/*')) {
    const base = pattern.slice(0, -2);
    return pathname === base || pathname.startsWith(`${base}/`);
  }
  if (pattern.endsWith('*')) return pathname.startsWith(pattern.slice(0, -1));
  return pathname === pattern;
}

export const matchAny = (patterns: readonly string[], pathname: string) => patterns.some((p) => matchPath(p, pathname));

/** Host pattern: exact or `*.example.com`. Case-insensitive, port ignored. */
export function matchHost(pattern: string, hostname: string): boolean {
  const h = hostname.toLowerCase();
  const p = pattern.toLowerCase();
  if (p.startsWith('*.')) return h.endsWith(p.slice(1)) && h.length > p.length - 1;
  return h === p;
}

function applyRule(rule: ScopeRule, pathname: string): boolean {
  if (rule === 'site') return true;
  if (rule.exclude && matchAny(rule.exclude, pathname)) return false;
  return matchAny(rule.include, pathname);
}

/** Is this host+path inside the gated scope? A host that is not listed in a `hosts` scope is not gated. */
export function inScope(scope: HumanCheckScope, hostname: string, pathname: string): boolean {
  switch (scope.kind) {
    case 'site':
      return true;
    case 'routes':
      return applyRule({ include: scope.include, exclude: scope.exclude }, pathname);
    case 'hosts': {
      for (const [host, rule] of Object.entries(scope.hosts)) {
        if (matchHost(host, hostname)) return applyRule(rule, pathname);
      }
      return false;
    }
  }
}

/** `next` must be a same-origin relative path. Anything else becomes `/`. */
export function safeNext(raw: string | null | undefined, gatePath: string): string {
  if (!raw || raw.length > 2048) return '/';
  if (!raw.startsWith('/') || raw.startsWith('//') || raw.startsWith('/\\')) return '/';
  // eslint-disable-next-line no-control-regex
  if (/[\u0000-\u001f\u007f\\]/.test(raw)) return '/';
  const path = raw.split(/[?#]/, 1)[0];
  if (path === gatePath) return '/';
  return raw;
}
