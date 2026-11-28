export const DEFAULT_REALTIME_PATH = '/ws';

/**
 * The socket URL for an API origin: same host, `ws:` for `http:` and `wss:`
 * for `https:`. The path is absolute (django-cfg's `RealtimeConfig.path`), so
 * a base with a path of its own keeps only its origin.
 */
export function realtimeUrl(apiBase: string, path: string = DEFAULT_REALTIME_PATH): string {
  const url = new URL(path, apiBase);
  if (url.protocol === 'http:') url.protocol = 'ws:';
  else if (url.protocol === 'https:') url.protocol = 'wss:';
  return url.toString();
}
