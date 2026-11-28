/**
 * Server-safe cookie header parsing, for SSR code that has the raw `Cookie` header
 * (Next.js `headers()`, a Node request) and wants the shared session cookie.
 * No DOM, no dependencies.
 */

/** The value of cookie `name` in a `Cookie` request header, or `null`. */
export function readCookie(cookieHeader: string | null | undefined, name: string): string | null {
  if (!cookieHeader) return null;
  const wanted = encodeURIComponent(name);
  for (const part of cookieHeader.split(';')) {
    const eq = part.indexOf('=');
    if (eq < 0) continue;
    if (part.slice(0, eq).trim() !== wanted) continue;
    try {
      return decodeURIComponent(part.slice(eq + 1).trim());
    } catch {
      return null;
    }
  }
  return null;
}
