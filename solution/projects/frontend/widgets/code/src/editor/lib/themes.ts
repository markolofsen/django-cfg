/**
 * Editor Themes
 *
 * The editor is always dark (devtool-style), so only dark themes are exposed.
 */

export type EditorTheme = 'vs-dark' | 'hc-black' | 'cmdop-dark';

export const EDITOR_THEMES = {
  // Built-in themes
  'vs-dark': 'Dark (VS Code)',
  'hc-black': 'High Contrast Dark',
  // Custom themes
  'cmdop-dark': 'CMDOP Dark',
} as const;

/**
 * CMDOP Dark Theme Definition
 * Can be registered with monaco.editor.defineTheme()
 */
export const cmdopDarkTheme = {
  base: 'vs-dark' as const,
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
    'editor.background': '#1a1a1a',
    'editor.foreground': '#D4D4D4',
    'editor.lineHighlightBackground': '#2d2d2d',
    'editor.selectionBackground': '#264F78',
    'editorCursor.foreground': '#AEAFAD',
    'editorLineNumber.foreground': '#858585',
    'editorLineNumber.activeForeground': '#C6C6C6',
  },
};
