// Adapted from jalcoui (MIT) — github.com/jal-co/ui

import type { TypeTag } from './types';

/**
 * Classify a single type token (e.g. `string`, `number[]`, `MyType<X>`,
 * `null`) into a semantic {@link TypeTag}. The classification is
 * intentionally loose — it only sees the bare token and ignores generic
 * parameters / array brackets / optional `?`.
 */
export function classifyTypeToken(token: string): TypeTag {
  // `split` always yields at least one segment, so index 0 is present.
  const base = (token.replace(/[[\]?]/g, '').split('<')[0] ?? '').trim().toLowerCase();

  if (!base) return 'other';
  if (base === 'string') return 'string';
  if (base === 'number' || base === 'bigint') return 'number';
  if (base === 'boolean' || base === 'true' || base === 'false') return 'boolean';
  if (base === 'function' || base === '() => void' || base.endsWith('=> void')) return 'function';
  if (base === 'reactnode' || base === 'react.reactnode' || base === 'jsx.element' || base === 'reactelement') {
    return 'reactnode';
  }
  if (base === 'null' || base === 'undefined' || base === 'void' || base === 'never') {
    return 'nullish';
  }
  // String literal like `"foo"` or `'bar'` → enum-ish categorical.
  if ((base.startsWith('"') && base.endsWith('"')) || (base.startsWith("'") && base.endsWith("'"))) {
    return 'enum';
  }
  // Numeric literal → also categorical (discriminated unions).
  if (/^-?\d+(\.\d+)?$/.test(base)) return 'enum';

  return 'other';
}

/**
 * Split a compound type signature on `|` separators, preserving the
 * separator tokens so the renderer can colorize the divider with the
 * muted foreground.
 */
export function splitTypeSignature(type: string): string[] {
  return type.split(/(\s*\|\s*)/).filter((part) => part.length > 0);
}
