import type { BaseLayoutProps } from '../../types/layout.types';

/**
 * The API origin the realtime socket URL is derived from: `realtime.apiUrl`,
 * else `apiUrl`, else `auth.apiUrl`, else `NEXT_PUBLIC_API_URL`. Undefined when
 * none is set; the client then uses the page's own origin.
 */
export function resolveRealtimeApiUrl(
  props: Pick<BaseLayoutProps, 'auth' | 'apiUrl' | 'realtime'>,
): string | undefined {
  const pick = (v?: string) => (v && v.trim() ? v : undefined);
  return (
    pick(props.realtime === false ? undefined : props.realtime?.apiUrl) ??
    pick(props.apiUrl) ??
    pick(props.auth === false ? undefined : props.auth?.apiUrl) ??
    pick(process.env.NEXT_PUBLIC_API_URL)
  );
}
