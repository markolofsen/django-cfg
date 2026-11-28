import type { BaseLayoutProps } from '../types/layout.types';

/**
 * The ingest origin for devtools: an explicit `devtools.baseUrl`, else the
 * `apiUrl` prop (apps with `auth={false}`), else `auth.apiUrl`. Undefined when
 * none is set, and `@djangocfg/devtools` then falls back to NEXT_PUBLIC_API_URL
 * and warns in the console if that is empty too.
 */
export function resolveDevtoolsBaseUrl(
  props: Pick<BaseLayoutProps, 'auth' | 'apiUrl' | 'devtools'>,
): string | undefined {
  const pick = (v?: string) => (v && v.trim() ? v : undefined);
  return (
    pick(props.devtools?.baseUrl) ??
    pick(props.apiUrl) ??
    pick(props.auth === false ? undefined : props.auth?.apiUrl)
  );
}
