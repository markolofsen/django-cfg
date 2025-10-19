/**
 * Font Utilities for OG Image Generation
 *
 * Provides dynamic font loading from Google Fonts without requiring files in public/
 * Based on Vercel's official @vercel/og documentation
 */

export interface FontConfig {
  name: string;
  weight?: 400 | 500 | 600 | 700 | 800 | 900;
  style?: 'normal' | 'italic';
  data: ArrayBuffer;
}

/**
 * Load a Google Font dynamically
 *
 * @param font - Font family name (e.g., "Inter", "Roboto", "Manrope")
 * @param text - Text to optimize font for (optional, reduces file size)
 * @param weight - Font weight (default: 700)
 * @returns ArrayBuffer of font data
 *
 * @example
 * const fontData = await loadGoogleFont('Manrope', 'Hello World', 700);
 */
export async function loadGoogleFont(
  font: string,
  text?: string,
  weight: number = 700
): Promise<ArrayBuffer> {
  // Construct Google Fonts API URL
  let url = `https://fonts.googleapis.com/css2?family=${font}:wght@${weight}`;

  // Add text parameter to optimize font subset (reduces size)
  if (text) {
    url += `&text=${encodeURIComponent(text)}`;
  }

  try {
    // Fetch CSS containing font URL
    const css = await fetch(url, {
      headers: {
        // Required to get TTF format instead of WOFF2
        'User-Agent':
          'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; de-at) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1',
      },
    }).then((res) => res.text());

    // Extract font URL from CSS
    const resource = css.match(/src: url\((.+)\) format\('(opentype|truetype)'\)/);

    if (!resource || !resource[1]) {
      throw new Error(`Failed to parse font URL from CSS for font: ${font}`);
    }

    // Fetch actual font file
    const response = await fetch(resource[1]);

    if (response.status !== 200) {
      throw new Error(`Failed to fetch font data: HTTP ${response.status}`);
    }

    return await response.arrayBuffer();
  } catch (error) {
    console.error(`Error loading Google Font "${font}":`, error);
    throw new Error(`Failed to load font "${font}": ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

/**
 * Load multiple Google Fonts
 *
 * @param fonts - Array of font configurations to load
 * @returns Array of FontConfig objects ready for ImageResponse
 *
 * @example
 * const fonts = await loadGoogleFonts([
 *   { family: 'Manrope', weight: 700 },
 *   { family: 'Inter', weight: 400 }
 * ]);
 */
export async function loadGoogleFonts(
  fonts: Array<{
    family: string;
    weight?: 400 | 500 | 600 | 700 | 800 | 900;
    style?: 'normal' | 'italic';
    text?: string;
  }>
): Promise<FontConfig[]> {
  const fontConfigs = await Promise.all(
    fonts.map(async ({ family, weight = 700, style = 'normal', text }) => {
      const data = await loadGoogleFont(family, text, weight);
      return {
        name: family,
        weight,
        style,
        data,
      };
    })
  );

  return fontConfigs;
}

/**
 * Create a font loader with caching
 *
 * Useful for reusing font data across multiple OG image requests
 *
 * @example
 * const fontLoader = createFontLoader();
 * const font = await fontLoader.load('Manrope', 700);
 */
export function createFontLoader() {
  const cache = new Map<string, Promise<ArrayBuffer>>();

  return {
    /**
     * Load a font with caching
     */
    async load(
      family: string,
      weight: number = 700,
      text?: string
    ): Promise<ArrayBuffer> {
      const cacheKey = `${family}-${weight}-${text || 'all'}`;

      if (!cache.has(cacheKey)) {
        cache.set(cacheKey, loadGoogleFont(family, text, weight));
      }

      return cache.get(cacheKey)!;
    },

    /**
     * Clear the cache
     */
    clear() {
      cache.clear();
    },

    /**
     * Get cache size
     */
    size() {
      return cache.size;
    },
  };
}
