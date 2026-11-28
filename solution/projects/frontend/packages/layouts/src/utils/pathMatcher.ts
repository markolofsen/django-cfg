/**
 * Path Matcher Utility
 *
 * Functions for matching URL paths against patterns with glob support.
 */

/**
 * Match pathname against glob pattern
 *
 * @param pathname - The URL pathname to match (e.g., '/projects/123/edit')
 * @param pattern - The pattern to match against (e.g., '/projects/＊/edit')
 * @returns true if pathname matches the pattern
 *
 * Glob patterns:
 * - `*` matches any single path segment
 * - `**` matches any number of path segments (zero or more)
 *
 * @example
 * ```ts
 * matchGlobPattern('/projects/123/edit', '/projects/＊/edit') // true
 * matchGlobPattern('/projects/abc/edit', '/projects/＊/edit') // true
 * matchGlobPattern('/admin/users/1/settings', '/admin/＊＊') // true
 * matchGlobPattern('/projects/edit', '/projects/＊/edit') // false
 * ```
 */
export function matchGlobPattern(pathname: string, pattern: string): boolean {
  // Normalize paths (remove trailing slashes)
  const normalizedPath = pathname.replace(/\/+$/, '');
  const normalizedPattern = pattern.replace(/\/+$/, '');

  // Split into segments
  const pathParts = normalizedPath.split('/').filter(Boolean);
  const patternParts = normalizedPattern.split('/').filter(Boolean);

  let pathIdx = 0;
  let patternIdx = 0;

  while (patternIdx < patternParts.length && pathIdx < pathParts.length) {
    const patternPart = patternParts[patternIdx];

    if (patternPart === '**') {
      // '**' matches zero or more segments
      // If it's the last pattern part, it matches everything remaining
      if (patternIdx === patternParts.length - 1) {
        return true;
      }
      // Otherwise, try to match the next pattern part against remaining path parts
      const nextPatternPart = patternParts[patternIdx + 1];
      while (pathIdx < pathParts.length) {
        if (pathParts[pathIdx] === nextPatternPart || nextPatternPart === '*') {
          break;
        }
        pathIdx++;
      }
      patternIdx++;
    } else if (patternPart === '*') {
      // '*' matches exactly one segment
      pathIdx++;
      patternIdx++;
    } else {
      // Literal match
      if (pathParts[pathIdx] !== patternPart) {
        return false;
      }
      pathIdx++;
      patternIdx++;
    }
  }

  // Check if we've consumed both arrays
  // Pattern can have trailing '**' which matches empty
  if (patternIdx < patternParts.length) {
    // Remaining pattern parts must all be '**'
    for (let i = patternIdx; i < patternParts.length; i++) {
      if (patternParts[i] !== '**') {
        return false;
      }
    }
  }

  return pathIdx === pathParts.length;
}

/**
 * Check if pathname matches any of the enabled paths
 *
 * @param pathname - The URL pathname to check
 * @param enabledPath - Single path, array of paths, or undefined
 * @returns true if pathname matches any enabled path
 *
 * Supports:
 * - Exact match: '/dashboard' matches '/dashboard'
 * - Prefix match: '/dashboard' matches '/dashboard/settings'
 * - Glob patterns: '/projects/＊/edit' matches '/projects/123/edit'
 *
 * @example
 * ```ts
 * matchesPath('/dashboard', '/dashboard') // true
 * matchesPath('/dashboard/settings', '/dashboard') // true
 * matchesPath('/projects/123/edit', '/projects/＊/edit') // true
 * matchesPath('/home', ['/dashboard', '/admin']) // false
 * ```
 */
export function matchesPath(pathname: string, enabledPath?: string | string[]): boolean {
  if (!enabledPath) return false;

  const matchSinglePath = (path: string): boolean => {
    // Normalize both sides — strip trailing slash (except root)
    const normalPath = pathname.length > 1 ? pathname.replace(/\/+$/, '') : pathname;
    const normalPattern = path.length > 1 ? path.replace(/\/+$/, '') : path;
    // If pattern contains glob characters, use pattern matching
    if (normalPattern.includes('*')) {
      return matchGlobPattern(normalPath, normalPattern);
    }
    // Otherwise, exact or prefix match
    return normalPath === normalPattern || normalPath.startsWith(normalPattern + '/');
  };

  if (typeof enabledPath === 'string') {
    return matchSinglePath(enabledPath);
  }

  // Array of paths
  return enabledPath.some(matchSinglePath);
}
