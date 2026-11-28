'use client';

import { code } from '@streamdown/code';
import { harden } from 'rehype-harden';
import { memo } from 'react';
import { Streamdown } from 'streamdown';

import { DiagramSource, diagramPlugin } from '../diagram';

/**
 * Markdown a READER is shown, outside any conversation.
 *
 * Sibling to `chat`'s `Response`, deliberately not the same component. Both
 * wrap `streamdown`; they differ on the question that decides a markdown
 * renderer's configuration — WHO WROTE THIS.
 *
 * `Response` renders the user's own agent, on the user's own machine. What
 * reaches this component was written somewhere else: a news post from the
 * platform, a file the reader opened. The difference shows in the PROTOCOL
 * list below — this one grants no app scheme — and it is why there are two
 * components rather than one with a `trusted` prop, a boolean that silently
 * relaxes link handling being the prop most likely to be passed wrong.
 *
 * It does NOT show in `linkSafety`, which both switch off. That default turns
 * every link into a `<button>` with no `href` and an "are you sure" modal, and
 * measuring it here is what settled the question: the protocols it would guard
 * are already refused by `harden` one layer up, so on this surface it adds a
 * second click to every link in a news post and no protection at all.
 *
 * No streaming, either: this text arrives whole. `Response` carries the
 * incomplete-markdown machinery because a token-by-token fence must not throw;
 * a document has no such state to be in.
 */

/**
 * Link hardening, restated because `rehype-harden` defaults `allowedProtocols`
 * to EMPTY — an unrecognised scheme loses its `href` and the anchor renders as
 * grey `<label> [blocked]` text mid-sentence.
 *
 * The list is SHORTER than the chat's on purpose: an app scheme is absent,
 * because it is meaningful only where a host assigns it meaning, and nothing
 * rendering a news post or a file preview does.
 */
const HARDEN_OPTIONS = {
  allowedLinkPrefixes: ['*'],
  allowedImagePrefixes: ['*'],
  allowedProtocols: ['http:', 'https:', 'mailto:', 'tel:'],
  allowDataImages: true,
} as const;

const REHYPE_PLUGINS = [[harden, HARDEN_OPTIONS]] as const;

/** See the note above: the modal guards protocols `harden` has already refused. */
const LINK_SAFETY = { enabled: false } as const;

/**
 * The same renderers the transcript uses.
 *
 * A document is where a diagram most often LIVES — an agent asked to draw one
 * writes a `.md` file, and the preview is the only place that file is read. So
 * the surface that renders it needs the plugin as much as the chat does;
 * shipping the diagram on one of the two would leave a fenced diagram in a file
 * rendering as a code block, which is precisely the defect this package exists
 * to fix, reproduced one surface over.
 */
const PLUGINS = { code, mermaid: diagramPlugin };

/** A rejected diagram shows its source, never streamdown's red error box. */
const MERMAID_OPTIONS = { errorComponent: DiagramSource } as const;

/** Body scale. Headings track it a notch above, through the stylesheet. */
export type MarkdownSize = 'xs' | 'sm' | 'base';

const SIZE_CLASS: Record<MarkdownSize, string> = {
  xs: 'text-xs',
  sm: 'text-sm',
  base: 'text-base',
};

export interface MarkdownProps {
  /** The markdown source. Arrives whole — this surface does not stream. */
  readonly children: string;
  readonly size?: MarkdownSize;
  readonly className?: string;
}

export const Markdown = memo(
  ({ children, size = 'sm', className }: MarkdownProps) => (
    <div className={`djc-markdown ${SIZE_CLASS[size]} ${className ?? ''}`} data-slot="markdown">
      <Streamdown
        // Static: the source is complete, so the incomplete-markdown
        // completion that a chat needs would only be guessing at text that is
        // not going to change.
        mode="static"
        parseIncompleteMarkdown={false}
        plugins={PLUGINS}
        mermaid={MERMAID_OPTIONS}
        linkSafety={LINK_SAFETY}
        rehypePlugins={REHYPE_PLUGINS as never}
      >
        {children}
      </Streamdown>
    </div>
  ),
  // Same comparator reasoning as the chat's: parsing markdown is the expensive
  // step, and a parent re-rendering for an unrelated reason must not repeat it.
  (prev, next) =>
    prev.children === next.children &&
    prev.size === next.size &&
    prev.className === next.className,
);

Markdown.displayName = 'Markdown';
