import { readFile } from 'node:fs/promises';

const dataUriCache = new Map<string, string>();

/**
 * Reads a local image into a Satori-compatible data URI and caches the result.
 *
 * For a portrait or logo that ships with the app. Pass an absolute path built
 * from `process.cwd()` — a `.jpg` beside a route file is not traced into a
 * standalone build any more than a `.woff` is, so keep such assets somewhere
 * `outputFileTracingIncludes` covers, or prefer an absolute URL via
 * `ogImageUrl` when the image is already served.
 */
export async function loadImageDataUri(path: string, mimeType: string): Promise<string> {
  const cached = dataUriCache.get(path);
  if (cached) return cached;

  const data = await readFile(path);
  const uri = `data:${mimeType};base64,${data.toString('base64')}`;
  dataUriCache.set(path, uri);
  return uri;
}
