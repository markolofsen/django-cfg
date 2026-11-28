/**
 * Path normalization for auth routing.
 *
 * next-intl may keep a 2-letter locale prefix in the URL (e.g. `/ru/auth`), and
 * paths arrive with or without trailing slashes. To match a pathname against a
 * fixed allow-list (like `['/auth']`) reliably, strip the locale segment and
 * trailing slashes first. Extracted from useAutoAuth so it can be unit-tested
 * and reused.
 */

/**
 * Strip a leading 2-letter locale segment and trailing slashes.
 * '/ru/auth/' → '/auth', '/auth' → '/auth', '/' → '/', '' → ''.
 */
export const normalizePath = (path: string | null | undefined): string => {
  if (!path) return '';
  const withoutLocale = path.replace(/^\/[a-z]{2}(?=\/|$)/, '');
  const trimmed = withoutLocale.replace(/\/+$/, '');
  return trimmed || '/';
};

/**
 * True when `pathname` (after locale/slash normalization) is one of the allowed
 * paths, or nested under one of them (`/auth` matches `/auth/callback`).
 */
export const isAllowedAuthPath = (
  pathname: string | null | undefined,
  allowedPaths: string[],
): boolean => {
  const normalized = normalizePath(pathname);
  return allowedPaths.some(
    (p) => normalized === p || normalized.startsWith(p + '/'),
  );
};
