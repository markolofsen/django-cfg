/**
 * IndexNow key file, served by Django.
 *
 * The protocol proves host ownership by fetching `https://<host>/<key>.txt`.
 * Django answers it at `/cfg/sitemap/indexnow/<key>.txt` from
 * `IndexNowConfig` — only the configured key, every other name 404s — so the
 * key lives in one place and the frontend ships no file.
 *
 * Put it in `fallback`: real public files and routes (`robots.txt`,
 * `llms-full.txt`) match the same shape and must win.
 *
 * @example
 * ```ts
 * import { indexNowKeyRewrite } from '@djangocfg/nextjs/config';
 *
 * async rewrites() {
 *   return { beforeFiles: [], afterFiles: [], fallback: [indexNowKeyRewrite(API_URL)] };
 * }
 * ```
 */
export function indexNowKeyRewrite(apiUrl: string): { source: string; destination: string } {
  return {
    // The protocol's key alphabet and length, at the site root only.
    source: '/:key([A-Za-z0-9-]{8,128}).txt',
    destination: `${apiUrl.replace(/\/+$/, '')}/cfg/sitemap/indexnow/:key.txt`,
  };
}
