'use client';

import { code } from '@streamdown/code';
import { memo } from 'react';
import { Streamdown } from 'streamdown';

/**
 * A read-only code listing, outside any conversation.
 *
 * Rendered by feeding a fenced block to the same parser the rest of this
 * package uses, rather than by calling a highlighter directly. That is the
 * point: the transcript, the document preview and the setup wizard then share
 * ONE highlighter, one theme and one set of supported languages, and a listing
 * cannot drift from the code block beside it in a chat message.
 *
 * Replaces the retired `@djangocfg/ui-tools/pretty-code`, which was built on Prism while
 * everything else here is on shiki. Two highlighters in one console means two
 * themes to keep matched and two answers to "is this language supported".
 */

/**
 * A language name shiki understands.
 *
 * Deliberately `string` rather than a union imported from the highlighter: the
 * predecessor exported Prism's own `Language` type, so every call site named
 * its supplier in its signature and swapping the supplier became a
 * type-level breaking change. An unknown name degrades to an unhighlighted
 * listing, which is the same outcome a wrong union member would have produced.
 */
export type CodeLanguage = string;

export type CodeVariant = 'card' | 'plain';

/**
 * Listing scale.
 *
 * `sm` (12px) is the wizard's density, where a snippet sits inside a step card
 * beside prose; `base` (14px) is a standalone listing. The predecessor spelled
 * this `isCompact`, a boolean that could only ever say "not the default" —
 * naming both ends means a third density is a value rather than a second flag.
 */
export type CodeSize = 'sm' | 'base';

const SIZE_CLASS: Record<CodeSize, string> = {
  sm: 'text-xs',
  base: 'text-sm',
};

export interface CodeProps {
  /** The source. An object is JSON-serialised, as the predecessor did. */
  readonly data: string | object;
  readonly language: CodeLanguage;
  /**
   * `card` — its own surface: border, ground, copy control.
   * `plain` — no chrome, grows to fit. For embedding inside a container that
   * already scrolls, where a second scroll surface traps the wheel.
   */
  readonly variant?: CodeVariant;
  readonly size?: CodeSize;
  readonly className?: string;
}

const PLUGINS = { code };

/** Fences the source. A fence inside the source would end the block early. */
function fence(source: string, language: string): string {
  const ticks = '`'.repeat(Math.max(3, longestTickRun(source) + 1));
  return `${ticks}${language}\n${source}\n${ticks}`;
}

function longestTickRun(source: string): number {
  let longest = 0;
  let current = 0;
  for (const character of source) {
    current = character === '`' ? current + 1 : 0;
    if (current > longest) longest = current;
  }
  return longest;
}

export const Code = memo(
  ({ data, language, variant = 'card', size = 'base', className }: CodeProps) => {
    const source = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
    return (
      <div
        className={`djc-code djc-code--${variant} ${SIZE_CLASS[size]} ${className ?? ''}`}
        data-slot="code"
        data-variant={variant}
        data-size={size}
      >
        <Streamdown
          mode="static"
          // The source is complete, so the incomplete-markdown completion a
          // chat needs would only be guessing at text that will not change.
          parseIncompleteMarkdown={false}
          plugins={PLUGINS}
          // `plain` embeds in a container that already scrolls; a height cap
          // here would add the second scroll surface the variant exists to
          // avoid.
          codeBlockMaxHeight={variant === 'plain' ? Infinity : 400}
          controls={{ code: variant === 'card' }}
        >
          {fence(source, language)}
        </Streamdown>
      </div>
    );
  },
  (prev, next) =>
    prev.data === next.data &&
    prev.language === next.language &&
    prev.variant === next.variant &&
    prev.size === next.size &&
    prev.className === next.className,
);

Code.displayName = 'Code';
