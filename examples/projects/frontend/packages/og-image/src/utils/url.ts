/**
 * URL Generation Helpers for OG Images
 *
 * Utilities to generate OG image URLs with proper query parameters
 */

/**
 * OG Image URL parameters
 */
export interface OgImageUrlParams {
  /** Page title */
  title: string;
  /** Page description (optional) */
  description?: string;
  /** Site name (optional) */
  siteName?: string;
  /** Logo URL (optional) */
  logo?: string;
  /** Additional custom parameters */
  [key: string]: string | number | boolean | undefined;
}

/**
 * Generate OG image URL with query parameters or base64 encoding
 *
 * @param baseUrl - Base URL of the OG image API route (e.g., '/api/og' or 'https://example.com/api/og')
 * @param params - URL parameters for the OG image
 * @param useBase64 - If true, encode params as base64 for safer URLs (default: true)
 * @returns Complete OG image URL with encoded parameters
 *
 * @example
 * ```typescript
 * // Base64 encoding (safe, default)
 * const url = generateOgImageUrl('/api/og', {
 *   title: 'My Page Title',
 *   description: 'Page description here',
 * });
 * // Result: /api/og?data=eyJ0aXRsZSI6Ik15IFBhZ2UgVGl0bGUiLCJkZXNjcmlwdGlvbiI6IlBhZ2UgZGVzY3JpcHRpb24gaGVyZSJ9
 *
 * // Query params (legacy)
 * const url = generateOgImageUrl('/api/og', { title: 'Hello' }, false);
 * // Result: /api/og?title=Hello
 * ```
 */
export function generateOgImageUrl(
  baseUrl: string,
  params: OgImageUrlParams,
  useBase64: boolean = true
): string {
  if (useBase64) {
    // Clean params - remove undefined/null/empty values
    const cleanParams: Record<string, string | number | boolean> = {};
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        cleanParams[key] = value;
      }
    });

    // Encode as base64 (browser-safe)
    const jsonString = JSON.stringify(cleanParams);
    const base64Data = btoa(jsonString);

    return `${baseUrl}?data=${base64Data}`;
  } else {
    // Legacy query params mode
    const searchParams = new URLSearchParams();

    // Add all defined parameters
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        searchParams.append(key, String(value));
      }
    });

    const query = searchParams.toString();
    return query ? `${baseUrl}?${query}` : baseUrl;
  }
}

/**
 * Get absolute OG image URL from relative path
 *
 * Useful for generating absolute URLs required by Open Graph meta tags
 *
 * @param relativePath - Relative OG image path (e.g., '/api/og?title=Hello')
 * @param siteUrl - Base site URL (e.g., 'https://example.com')
 * @returns Absolute URL
 *
 * @example
 * ```typescript
 * const absolute = getAbsoluteOgImageUrl(
 *   '/api/og?title=Hello',
 *   'https://example.com'
 * );
 * // Result: https://example.com/api/og?title=Hello
 * ```
 */
export function getAbsoluteOgImageUrl(
  relativePath: string,
  siteUrl: string
): string {
  // Remove trailing slash from site URL
  const cleanSiteUrl = siteUrl.replace(/\/$/, '');

  // Ensure relative path starts with /
  const cleanPath = relativePath.startsWith('/')
    ? relativePath
    : `/${relativePath}`;

  return `${cleanSiteUrl}${cleanPath}`;
}

/**
 * Create OG image URL builder with preset configuration
 *
 * Useful when you want to reuse the same base URL and default parameters
 *
 * @param baseUrl - Base URL of the OG image API route
 * @param defaults - Default parameters to merge with each URL generation
 * @returns URL builder function
 *
 * @example
 * ```typescript
 * const buildOgUrl = createOgImageUrlBuilder('/api/og', {
 *   siteName: 'My Site',
 *   logo: '/logo.png'
 * });
 *
 * const url1 = buildOgUrl({ title: 'Page 1' });
 * const url2 = buildOgUrl({ title: 'Page 2', description: 'Custom desc' });
 * ```
 */
export function createOgImageUrlBuilder(
  baseUrl: string,
  defaults: Partial<OgImageUrlParams> = {}
) {
  return (params: OgImageUrlParams): string => {
    return generateOgImageUrl(baseUrl, {
      ...defaults,
      ...params,
    });
  };
}

/**
 * Parse OG image URL parameters from a URL string
 *
 * @param url - Full or relative URL with query parameters
 * @returns Parsed parameters object
 *
 * @example
 * ```typescript
 * const params = parseOgImageUrl('/api/og?title=Hello&description=World');
 * // Result: { title: 'Hello', description: 'World' }
 * ```
 */
export function parseOgImageUrl(url: string): Record<string, string> {
  try {
    const urlObj = new URL(url, 'http://dummy.com');
    const params: Record<string, string> = {};

    urlObj.searchParams.forEach((value, key) => {
      params[key] = value;
    });

    return params;
  } catch {
    return {};
  }
}
