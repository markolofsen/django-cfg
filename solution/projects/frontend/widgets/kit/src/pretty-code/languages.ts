import type { Language } from 'prism-react-renderer';

/**
 * ONE answer to "which grammar, and what is it called" for every Prism
 * surface: `PrettyCode`, the chat's fenced blocks and the diff viewer.
 *
 * It used to be answered three times (two `switch` blocks in `PrettyCode` and a
 * third in the diff viewer) and they disagreed on `shell` and `tsx`.
 */
const LANGUAGES: Readonly<Record<string, { readonly prism: string; readonly label: string }>> = {
  javascript: { prism: 'javascript', label: 'JavaScript' },
  js: { prism: 'javascript', label: 'JavaScript' },
  jsx: { prism: 'jsx', label: 'JSX' },
  typescript: { prism: 'typescript', label: 'TypeScript' },
  ts: { prism: 'typescript', label: 'TypeScript' },
  tsx: { prism: 'tsx', label: 'TSX' },
  python: { prism: 'python', label: 'Python' },
  py: { prism: 'python', label: 'Python' },
  json: { prism: 'json', label: 'JSON' },
  css: { prism: 'css', label: 'CSS' },
  html: { prism: 'markup', label: 'HTML' },
  xml: { prism: 'markup', label: 'XML' },
  bash: { prism: 'bash', label: 'Bash' },
  shell: { prism: 'bash', label: 'Bash' },
  sh: { prism: 'bash', label: 'Bash' },
  zsh: { prism: 'bash', label: 'Bash' },
  ruby: { prism: 'ruby', label: 'Ruby' },
  rb: { prism: 'ruby', label: 'Ruby' },
  java: { prism: 'java', label: 'Java' },
  php: { prism: 'php', label: 'PHP' },
  go: { prism: 'go', label: 'Go' },
  golang: { prism: 'go', label: 'Go' },
  sql: { prism: 'sql', label: 'SQL' },
  yaml: { prism: 'yaml', label: 'YAML' },
  yml: { prism: 'yaml', label: 'YAML' },
  markdown: { prism: 'markdown', label: 'Markdown' },
  md: { prism: 'markdown', label: 'Markdown' },
  plaintext: { prism: 'text', label: 'Text' },
  text: { prism: 'text', label: 'Text' },
  txt: { prism: 'text', label: 'Text' },
  // Drawn by the surface's diagram branch, never highlighted here.
  mermaid: { prism: 'text', label: 'Mermaid' },
};

/** The Prism grammar key for a free-form fence language. Unknown names pass through: Prism renders an unregistered grammar as plain text. */
export function normalizePrismLanguage(language: string | undefined): Language {
  const key = (language ?? '').trim().toLowerCase();
  return LANGUAGES[key]?.prism ?? (key || 'text');
}

/** The label a header shows for a fence language ("ts" -> "TypeScript"). */
export function languageLabel(language: string | undefined): string {
  const key = (language ?? '').trim().toLowerCase();
  const known = LANGUAGES[key];
  if (known) return known.label;
  return key ? key.charAt(0).toUpperCase() + key.slice(1) : 'Text';
}
