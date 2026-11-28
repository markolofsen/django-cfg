'use client';

import { useMemo } from 'react';
import { getLanguageByFilename } from '../lib/languages';

/**
 * Hook to detect language from filename
 *
 * @param filename - File name or path
 * @returns Monaco language ID
 *
 * @example
 * ```tsx
 * const language = useLanguage('app.tsx');
 * // Returns: 'typescript'
 *
 * const language2 = useLanguage('/path/to/Dockerfile');
 * // Returns: 'dockerfile'
 * ```
 */
export function useLanguage(filename: string | undefined): string {
  return useMemo(() => {
    if (!filename) return 'plaintext';

    // Extract basename from path
    const basename = filename.split('/').pop() || filename;
    return getLanguageByFilename(basename);
  }, [filename]);
}
