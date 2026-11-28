// Adapted from jalcoui (MIT) — github.com/jal-co/ui

'use client';

import * as React from 'react';
import { Highlight, type Language, type PrismTheme } from 'prism-react-renderer';

interface DiffLineContentProps {
  content: string;
  language: Language | null;
  /**
   * Prism palette resolved by the parent `DiffViewer` against the host
   * theme. Forwarded here so we don't run a theme-detection hook on
   * every line (a big diff can be thousands of rows).
   */
  prismTheme: PrismTheme;
}

/**
 * Single-line content cell. When `language` is non-null the line is
 * tokenized by `prism-react-renderer` (the same instance PrettyCode
 * uses). When null we render plain text — cheap path for `language`-less
 * diffs and very large lists.
 *
 * Each line tokenizes independently. For diffs > a few thousand lines
 * this can get warm; in practice the LCS already drops to context lines
 * before we get there.
 */
export const DiffLineContent = React.memo(function DiffLineContent({
  content,
  language,
  prismTheme,
}: DiffLineContentProps) {
  if (!language) {
    return <>{content || ' '}</>;
  }
  return (
    <Highlight theme={prismTheme} code={content || ' '} language={language}>
      {({ tokens, getTokenProps }) => (
        <>
          {tokens[0]?.map((token, key) => (
            <span key={key} {...getTokenProps({ token })} />
          ))}
        </>
      )}
    </Highlight>
  );
});
