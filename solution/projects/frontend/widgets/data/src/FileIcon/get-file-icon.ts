'use client';

/**
 * Resolver for VSCode-style file icons. Replaces the former optional
 * `material-file-icons` runtime dependency — the icon SVGs are now vendored
 * as a static data module (`./icons/icon-data`), so the bundler resolves them
 * deterministically with no dynamic `import()` and no `@vite-ignore`.
 *
 * Lookup matches the original `material-file-icons` algorithm:
 *   1. exact full-name match (`files[]`, lowercased)
 *   2. longest matching extension (`name.endsWith('.' + ext)`)
 *   3. fall back to the default file icon
 *
 * The `files` / `extensions` lookup maps are built lazily on first call.
 */

import {
  DEFAULT_FILE_ICON,
  FILE_ICONS,
  type FileIconDef,
} from './icons/icon-data';

export type { FileIconDef };
export { DEFAULT_FILE_ICON };

/** Full-name → icon (e.g. `dockerfile`, `.gitignore`). */
let fileMap: Map<string, FileIconDef> | null = null;
/** Extension → icon. When several icons share an extension, last wins. */
let extMap: Map<string, FileIconDef> | null = null;

function buildIndex(): void {
  fileMap = new Map();
  extMap = new Map();
  for (const icon of FILE_ICONS) {
    if (icon.files) {
      for (const f of icon.files) fileMap.set(f, icon);
    }
    if (icon.extensions) {
      for (const ext of icon.extensions) extMap.set(ext, icon);
    }
  }
}

/**
 * Resolve the icon definition for a file name. Always returns a definition —
 * unknown types yield {@link DEFAULT_FILE_ICON}.
 */
export function getFileIcon(filename: string): FileIconDef {
  if (typeof filename !== 'string' || filename.length === 0) {
    return DEFAULT_FILE_ICON;
  }
  if (fileMap === null || extMap === null) buildIndex();

  const lc = filename.toLowerCase();

  // 1. Exact full-name match.
  const byName = fileMap!.get(lc);
  if (byName) return byName;

  // 2. Longest matching extension.
  let match: FileIconDef | null = null;
  let matchLength = 0;
  for (const [ext, icon] of extMap!) {
    if (ext.length > matchLength && lc.endsWith(`.${ext}`)) {
      match = icon;
      matchLength = ext.length;
    }
  }
  if (match) return match;

  // 3. Fallback.
  return DEFAULT_FILE_ICON;
}
