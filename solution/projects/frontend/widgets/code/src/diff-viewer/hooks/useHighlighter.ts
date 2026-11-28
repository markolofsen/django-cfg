// Adapted from jalcoui (MIT) — github.com/jal-co/ui
//
// The language answer for DiffViewer. The tokenizer and the grammar loader are
// the kit's `PrettyCode` ones, so a diff and a code block agree on which
// languages exist and what a fence name means — no second table here.

import { useMemo } from 'react';
import type { Language } from 'prism-react-renderer';
import { normalizePrismLanguage, useEnsurePrismLanguages } from '@djangocfg/widget-kit/pretty-code';

/**
 * The resolved Prism language key. The component re-renders once
 * `bash`/`ruby`/… are registered so the first paint isn't stuck on plain text.
 */
export function useDiffLanguage(language: string | undefined): Language {
  useEnsurePrismLanguages();
  return useMemo(() => normalizePrismLanguage(language), [language]);
}
