/**
 * Locale file utilities for CLI
 */

import * as fs from 'node:fs';
import * as path from 'node:path';
import { consola } from 'consola';
import { createJiti } from 'jiti';

// Create jiti instance for loading TypeScript files at runtime
const jiti = createJiti(import.meta.url);

export interface LocaleConfig {
  dir: string;
  fileExtension: '.ts' | '.json';
  locales: string[];
}

/**
 * Detect locale configuration from directory
 */
export function detectLocaleConfig(dir: string): LocaleConfig {
  if (!fs.existsSync(dir)) {
    throw new Error(`Directory not found: ${dir}`);
  }

  const files = fs.readdirSync(dir);

  // Check for .ts or .json files
  const tsFiles = files.filter((f) => f.endsWith('.ts') && f !== 'index.ts');
  const jsonFiles = files.filter((f) => f.endsWith('.json'));

  const fileExtension = tsFiles.length > 0 ? '.ts' : '.json';
  const localeFiles = fileExtension === '.ts' ? tsFiles : jsonFiles;

  const locales = localeFiles
    .map((f) => f.replace(fileExtension, ''))
    .sort((a, b) => {
      if (a === 'en') return -1;
      if (b === 'en') return 1;
      return a.localeCompare(b);
    });

  return { dir, fileExtension, locales };
}

/**
 * Get default locales directory (package locales)
 */
export function getDefaultLocalesDir(): string {
  // Try to find package root
  let current = process.cwd();

  while (current !== '/') {
    const packageJson = path.join(current, 'package.json');
    if (fs.existsSync(packageJson)) {
      const pkg = JSON.parse(fs.readFileSync(packageJson, 'utf-8'));
      if (pkg.name === '@djangocfg/i18n') {
        return path.join(current, 'src', 'locales');
      }
    }
    current = path.dirname(current);
  }

  // Fallback: relative to CLI file
  return path.resolve(__dirname, '../../locales');
}

/**
 * Get export name for locale (handles pt-BR -> ptBR)
 */
export function getExportName(locale: string): string {
  if (locale === 'pt-BR') return 'ptBR';
  return locale;
}

/**
 * Load locale translations
 */
export async function loadLocale(
  config: LocaleConfig,
  locale: string
): Promise<Record<string, unknown>> {
  const filePath = path.join(config.dir, `${locale}${config.fileExtension}`);

  if (!fs.existsSync(filePath)) {
    throw new Error(`Locale file not found: ${filePath}`);
  }

  if (config.fileExtension === '.json') {
    const content = fs.readFileSync(filePath, 'utf-8');
    return JSON.parse(content);
  }

  // TypeScript file - use jiti for runtime TypeScript loading
  try {
    const module = await jiti.import(filePath);
    const exportName = getExportName(locale);
    const m = module as Record<string, unknown>
    return (m[exportName] ?? m['default'] ?? {}) as Record<string, unknown>
  } catch (error) {
    consola.error(`Failed to load ${locale}:`, error);
    return {};
  }
}

/**
 * Read locale file content (for editing)
 */
export function readLocaleFile(
  config: LocaleConfig,
  locale: string
): { content: string; exportName: string } {
  const filePath = path.join(config.dir, `${locale}${config.fileExtension}`);

  if (!fs.existsSync(filePath)) {
    throw new Error(`Locale file not found: ${filePath}`);
  }

  const content = fs.readFileSync(filePath, 'utf-8');

  if (config.fileExtension === '.json') {
    return { content, exportName: '' };
  }

  // Destructured rather than indexed: `\w+` cannot match empty, so a match
  // always carries group 1 — but only the binding proves that to the compiler,
  // and the same `throw` covers both halves instead of asserting one of them.
  const [, exportName] = content.match(/export const (\w+)/) ?? [];
  if (!exportName) {
    throw new Error(`Could not find export in ${locale}${config.fileExtension}`);
  }

  return { content, exportName };
}

/**
 * Write locale file
 */
export function writeLocaleFile(
  config: LocaleConfig,
  locale: string,
  content: string
): void {
  const filePath = path.join(config.dir, `${locale}${config.fileExtension}`);
  fs.writeFileSync(filePath, content, 'utf-8');
}

/**
 * Get all keys from object as dot-notation paths
 */
export function getAllKeys(
  obj: Record<string, unknown>,
  prefix = ''
): Array<{ path: string; value: unknown }> {
  const keys: Array<{ path: string; value: unknown }> = [];

  for (const [key, value] of Object.entries(obj)) {
    const fullPath = prefix ? `${prefix}.${key}` : key;

    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      keys.push(...getAllKeys(value as Record<string, unknown>, fullPath));
    } else {
      keys.push({ path: fullPath, value });
    }
  }

  return keys;
}

/**
 * Get value at nested path
 */
export function getValueAtPath(obj: Record<string, unknown>, keyPath: string): unknown {
  const keys = keyPath.split('.');
  let current: unknown = obj;

  for (const key of keys) {
    if (current === null || typeof current !== 'object') {
      return undefined;
    }
    current = (current as Record<string, unknown>)[key];
  }

  return current;
}

/**
 * Set value at nested path.
 *
 * `isPlainRecord` rather than `typeof x === 'object'`: that test is true for
 * `null` and for arrays. A `null` on the path crashed with "Cannot set
 * properties of null", and an array swallowed the write silently — the value
 * went nowhere and the CLI reported success.
 *
 * An empty `keyPath` writes nothing. `''.split('.')` yields `['']`, and the
 * previous code indexed `keys[-1]`, producing a literal `"undefined"` key in
 * the locale file.
 */
export function setValueAtPath(
  obj: Record<string, unknown>,
  keyPath: string,
  value: unknown
): void {
  const keys = keyPath.split('.').filter(Boolean);
  const leaf = keys.pop();
  if (leaf === undefined) return;

  let current = obj;
  for (const key of keys) {
    const next = current[key];
    current = isPlainRecord(next) ? next : (current[key] = {});
  }

  current[leaf] = value;
}

/** A value that can carry nested keys: an object, but not `null` and not an array. */
function isPlainRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/** Object keys that need no quoting in a TS/JS object literal. */
const BARE_KEY = /^[A-Za-z_$][A-Za-z0-9_$]*$/;

/**
 * Serialise a translations object back to a TypeScript object literal.
 *
 * Locale leaves are always strings and branches always plain objects, so this
 * needs no general-purpose value support — anything else is a bug upstream and
 * `JSON.stringify` is the honest fallback rather than a silent `[object]`.
 */
function toObjectLiteral(value: unknown, indent: string): string {
  if (!isPlainRecord(value)) return JSON.stringify(value ?? null);

  const inner = indent + '  ';
  const body = Object.entries(value)
    .map(([key, child]) => {
      const name = BARE_KEY.test(key) ? key : JSON.stringify(key);
      return `${inner}${name}: ${toObjectLiteral(child, inner)},`;
    })
    .join('\n');

  return body ? `{\n${body}\n${indent}}` : '{}';
}

/**
 * Replace the exported object literal in a TS locale file, keeping everything
 * around it — the type import, the doc comment, and the `: I18nTranslations`
 * annotation — untouched.
 *
 * The previous approach edited the text with `indexOf` and brace counting, and
 * inserted a whole nested chain at the outermost level: adding `ui.form.cancel`
 * to a file that already had `ui.form.save` produced a SECOND `form:` block
 * inside `ui`. In a TS object literal the later key wins, so the existing
 * translation was silently dropped — a data-loss bug, not a formatting one.
 * The file's own comment said "for complex cases, consider AST parsing".
 * Serialising the object `loadLocale` already parsed removes the need for both.
 */
export function renderTsLocale(
  originalContent: string,
  exportName: string,
  translations: Record<string, unknown>
): string {
  const declaration = new RegExp(`(export\\s+const\\s+${exportName}\\b[^=]*=\\s*)`);
  const match = originalContent.match(declaration);
  if (!match || match.index === undefined) {
    throw new Error(`Could not find "export const ${exportName}" to update`);
  }

  const bodyStart = match.index + match[0].length;
  if (originalContent[bodyStart] !== '{') {
    throw new Error(`Expected an object literal after "export const ${exportName}"`);
  }

  const bodyEnd = matchBrace(originalContent, bodyStart);
  return (
    originalContent.slice(0, bodyStart) +
    toObjectLiteral(translations, '') +
    originalContent.slice(bodyEnd + 1)
  );
}

/**
 * Index of the `}` closing the `{` at `start`.
 *
 * String-aware: a brace inside a translation (`"{count} items"`) would
 * otherwise unbalance the count and truncate the file.
 */
function matchBrace(source: string, start: number): number {
  let depth = 0;
  let quote: string | null = null;

  for (let i = start; i < source.length; i++) {
    const char = source[i];

    if (quote) {
      if (char === '\\') i++;
      else if (char === quote) quote = null;
      continue;
    }

    if (char === '"' || char === "'" || char === '`') quote = char;
    else if (char === '{') depth++;
    else if (char === '}' && --depth === 0) return i;
  }

  throw new Error('Unbalanced braces in locale file');
}
