/**
 * One locale across every host of one product family.
 *
 * `NEXT_LOCALE` is written host-only by default, so a reader who picked Russian on `hub.example.com` meets English on
 * `team.example.com`. The session tokens already live on the registrable domain (`@djangocfg/api` `createStorage`,
 * `cookieDomain: 'auto'`); the locale follows the same rule: the cookie gets `Domain=` the registrable domain, and the
 * host-only twin is expired so it cannot shadow the shared one.
 *
 * Pure and framework-free, so the proxy (server) and `useChangeLocale` (browser) agree on the domain.
 */

export const LOCALE_COOKIE = 'NEXT_LOCALE';
export const LOCALE_COOKIE_MAX_AGE = 60 * 60 * 24 * 365;

// Second-level public suffixes whose registrable domain has three labels. Not the whole Public Suffix List: the common
// ones; anything else sets NEXT_PUBLIC_COOKIE_DOMAIN.
const TWO_LABEL_SUFFIXES = new Set([
  'co.uk', 'org.uk', 'ac.uk', 'com.au', 'net.au', 'co.nz', 'co.jp', 'co.kr', 'or.kr', 'com.br', 'com.tr', 'com.cn', 'com.mx',
  'co.in', 'co.za', 'com.sg', 'com.hk', 'com.tw', 'com.ar', 'com.ua', 'co.il',
]);

/**
 * The domain a cookie must carry to be sent to every subdomain, or `null` for a host that cannot share (an IP, a bare
 * label such as `localhost`, or an apex with no subdomain in use: a host-only cookie already covers it).
 * `override` (`NEXT_PUBLIC_COOKIE_DOMAIN`) wins when set.
 */
export function sharedCookieDomain(hostname: string, override?: string | null): string | null {
  const forced = override?.trim().replace(/^\./, '');
  if (forced) return forced;
  const host = hostname.split(':')[0]!.toLowerCase();
  if (!host || /^\d+(\.\d+){3}$/.test(host) || host.includes(':')) return null;
  const labels = host.split('.');
  if (labels.length < 2) return null;
  const keep = TWO_LABEL_SUFFIXES.has(labels.slice(-2).join('.')) ? 3 : 2;
  return labels.slice(-keep).join('.');
}

/** The `Set-Cookie` value that writes the shared locale cookie. */
export function localeCookieHeader(locale: string, domain: string | null, secure: boolean): string {
  return `${LOCALE_COOKIE}=${encodeURIComponent(locale)}; Path=/; Max-Age=${LOCALE_COOKIE_MAX_AGE}; SameSite=Lax${domain ? `; Domain=${domain}` : ''}${secure ? '; Secure' : ''}`;
}

/** Expires the host-only twin of the cookie (a cookie is identified by name and Domain). */
export function expireHostOnlyLocaleCookie(secure: boolean): string {
  return `${LOCALE_COOKIE}=; Path=/; Max-Age=0; SameSite=Lax${secure ? '; Secure' : ''}`;
}
