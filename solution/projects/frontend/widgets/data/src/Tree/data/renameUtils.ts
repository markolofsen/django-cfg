'use client';

// =====================================================================
// Filename split — used by the inline-rename input to auto-select the
// "base" portion without the extension (Finder / macOS behaviour).
//
// Rules:
//   - dotfiles like ".env" or ".gitignore" → base = whole name, ext = ''
//   - "foo"                                → base = 'foo', ext = ''
//   - "foo.txt"                            → base = 'foo', ext = '.txt'
//   - "foo.bar.baz"                        → base = 'foo.bar', ext = '.baz'
//   - "folder/"  (trailing slash)          → trailing slash kept in ext
//
// We deliberately don't handle nested dots or multi-part extensions like
// ".tar.gz". Finder picks the last `.` and so do we — it's good enough
// for selection UX and consistent with the OS.
// =====================================================================

export interface SplitName {
  base: string;
  ext: string;
}

export function splitFileName(name: string): SplitName {
  if (name.length === 0) return { base: '', ext: '' };

  // Dotfiles — leading dot is part of the base, not an extension.
  if (name.startsWith('.')) {
    const rest = name.slice(1);
    const dot = rest.lastIndexOf('.');
    if (dot < 0) return { base: name, ext: '' };
    return { base: '.' + rest.slice(0, dot), ext: rest.slice(dot) };
  }

  const dot = name.lastIndexOf('.');
  if (dot <= 0) return { base: name, ext: '' };
  return { base: name.slice(0, dot), ext: name.slice(dot) };
}

/**
 * Returns the `[selectionStart, selectionEnd]` pair to use on focus of an
 * `<input>` so only the base name is highlighted (Finder behaviour).
 *
 * Folders pass `isFolder=true` to skip extension detection and select
 * the entire name — folders don't have file extensions semantically.
 */
export function autoSelectRange(name: string, isFolder: boolean): [number, number] {
  if (isFolder) return [0, name.length];
  const { base } = splitFileName(name);
  return [0, base.length];
}
