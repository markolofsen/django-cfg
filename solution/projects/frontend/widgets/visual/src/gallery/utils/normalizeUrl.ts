/**
 * URL normalization utilities for Gallery
 *
 * Handles Mixed Content issues by upgrading HTTP to HTTPS
 * when the page is served over HTTPS.
 */

/**
 * Normalize image URL to prevent Mixed Content errors
 * Upgrades HTTP to HTTPS when page is served over HTTPS
 */
export function normalizeImageUrl(url: string | undefined): string {
  if (!url) return ''

  // Check if we're on HTTPS page
  const isSecurePage = typeof window !== 'undefined' && window.location.protocol === 'https:'

  // Upgrade HTTP to HTTPS if on secure page
  if (isSecurePage && url.startsWith('http://')) {
    return url.replace('http://', 'https://')
  }

  return url
}

/**
 * Normalize array of URLs
 */
export function normalizeImageUrls(urls: (string | undefined)[]): string[] {
  return urls.map(normalizeImageUrl).filter(Boolean) as string[]
}
