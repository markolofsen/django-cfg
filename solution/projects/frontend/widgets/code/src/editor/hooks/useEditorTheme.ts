'use client';

import { useEffect, useState } from 'react';

/** Background used for the editor and its loading/error placeholders. */
export const EDITOR_BACKGROUND = '#0a0a0a';

/**
 * Hook that registers and returns the Monaco editor theme.
 *
 * The editor is always dark (Chrome devtools / VSCode convention) — its
 * palette does not follow the host app theme. Pass `themeOverride` only
 * if you need a specific Monaco built-in (e.g. `'hc-black'`).
 *
 * @param monaco - Monaco namespace (null during loading)
 * @param themeOverride - Optional explicit theme name
 * @returns Resolved Monaco theme name to pass to editor options
 */
export function useEditorTheme(
  monaco: typeof import('monaco-editor') | null,
  themeOverride?: string,
): string {
  // State (not ref) so consumers re-render once the custom theme is registered.
  const [registered, setRegistered] = useState(false);

  useEffect(() => {
    if (!monaco) return;

    try {
      const colors = readEditorColors();

      monaco.editor.defineTheme('app-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: [
          { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
          { token: 'keyword', foreground: 'C586C0' },
          { token: 'string', foreground: 'CE9178' },
          { token: 'number', foreground: 'B5CEA8' },
          { token: 'type', foreground: '4EC9B0' },
          { token: 'function', foreground: 'DCDCAA' },
          { token: 'variable', foreground: '9CDCFE' },
        ],
        colors: {
          'editor.background': colors.background,
          'editor.foreground': colors.foreground,
          'editor.lineHighlightBackground': colors.lineHighlight,
          'editor.selectionBackground': colors.selection,
          'editorCursor.foreground': colors.foreground,
          'editorLineNumber.foreground': colors.mutedForeground,
          'editorWidget.background': colors.card,
          'editorWidget.border': colors.border,
          'input.background': colors.card,
          'dropdown.background': colors.card,
        },
      });

      setRegistered(true);
    } catch {
      // Fallback — use the built-in dark theme.
      setRegistered(false);
    }
  }, [monaco]);

  if (themeOverride) return themeOverride;
  return registered ? 'app-dark' : 'vs-dark';
}

/**
 * Editor colors — hard-coded dark palette.
 *
 * Previously we resolved against CSS variables (`--background`, `--card`,
 * …) so the editor matched the host theme, but the editor MUST be dark
 * regardless of host theme (Chrome devtools / VSCode / Insomnia
 * convention). On a light-themed app `--background` resolves to white,
 * which Monaco then paints under `base: 'vs-dark'` — giving the broken
 * "white Monaco" look. Hard-coding keeps the dark contract honest and
 * removes a layout-time DOM probe.
 */
function readEditorColors() {
  return {
    background: EDITOR_BACKGROUND,
    foreground: '#f5f5f5',
    card: '#141414',
    border: '#262626',
    mutedForeground: '#858585',
    lineHighlight: '#1a1a1a',
    selection: '#264F78',
  };
}

