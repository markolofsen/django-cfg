'use client';

import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeExternalLinks from 'rehype-external-links';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import remarkBreaks from 'remark-breaks';
import remarkEmoji from 'remark-emoji';
import remarkGfm from 'remark-gfm';
import remarkSmartypants from 'remark-smartypants';
import type { Components } from 'react-markdown';

import { useCollapsibleContent } from '../use-collapsible-content';
import type { MarkdownMessageProps } from './types';
import { buildSchema, buildUrlTransform } from './sanitize';
import { looksLikePlainProse } from './plainText';
import { createMarkdownComponents } from './components';
import { CollapseToggle } from './CollapseToggle';
import { applyPreprocess, buildLinkRulesComponent, collectProtocols } from './linkRules';
import { renderableTail, splitStreamingBlocks } from './streamingBlocks';

/**
 * Shared remark plugin chain. Hoisted to a module constant so its
 * reference is stable across every block render in streaming mode —
 * otherwise a fresh array each render would defeat ReactMarkdown's own
 * internal memoization and force every block to re-process.
 *
 * Order is load-bearing:
 *   1. `remark-gfm` — tables, strikethrough, autolinks, task lists.
 *   2. `remark-breaks` — chat convention: single `\n` → `<br>`.
 *   3. `remark-smartypants` — typographic substitutions.
 *   4. `remark-emoji` — `:smile:` → 😄.
 */
const REMARK_PLUGINS = [remarkGfm, remarkBreaks, remarkSmartypants, remarkEmoji] as const;

/** Props for a single rendered markdown block. Kept small so the memo
 *  comparator is cheap and precise. */
interface MarkdownBlockProps {
  source: string;
  components: Partial<Components>;
  schema: ReturnType<typeof buildSchema>;
  urlTransform: ReturnType<typeof buildUrlTransform> | undefined;
}

/**
 * One memoized markdown block. In streaming mode the parent block-splits
 * the document and renders each completed block through this; the memo
 * comparator skips re-parsing any block whose `source` (and render config)
 * is unchanged — so as tokens append to the tail, blocks 0..N-1 stay put.
 */
const MarkdownBlock = memo(
  function MarkdownBlockRaw({ source, components, schema, urlTransform }: MarkdownBlockProps) {
    return (
      <ReactMarkdown
        remarkPlugins={REMARK_PLUGINS as unknown as React.ComponentProps<typeof ReactMarkdown>['remarkPlugins']}
        // rehype-raw parses inline HTML; rehype-sanitize (extended schema)
        // runs after to keep XSS guards; rehype-external-links tags <a>.
        // SAME chain as the non-streaming path → identical safety posture.
        rehypePlugins={[
          rehypeRaw,
          [rehypeSanitize, schema],
          [rehypeExternalLinks, { target: '_blank', rel: ['noopener', 'noreferrer'] }],
        ]}
        components={components}
        urlTransform={urlTransform}
      >
        {source}
      </ReactMarkdown>
    );
  },
  (a, b) =>
    a.source === b.source &&
    a.components === b.components &&
    a.schema === b.schema &&
    a.urlTransform === b.urlTransform,
);

/** Body text size class for the plain-text / prose wrapper. */
const SIZE_TO_TEXT: Record<'xs' | 'sm' | 'base', string> = {
  xs: 'text-xs',
  sm: 'text-sm',
  base: 'text-base',
};

/** Tailwind-typography modifier per size level. */
const SIZE_TO_PROSE: Record<'xs' | 'sm' | 'base', string> = {
  xs: 'prose-xs',
  sm: 'prose-sm',
  base: 'prose-base',
};

/**
 * MarkdownMessage — chat-tuned markdown renderer.
 *
 * Features:
 * - GitHub Flavored Markdown (GFM) via remark-gfm
 * - Syntax-highlighted code blocks with Copy button
 * - Mermaid diagram rendering (` ```mermaid ` fence)
 * - Tables, lists, blockquotes scaled for chat density
 * - User vs assistant styling modes (`isUser`)
 * - Plain-text fast path: skips ReactMarkdown when content has no
 *   markdown syntax (cheaper render, preserves newlines via CSS)
 * - Optional collapsible "Read more..." for long messages
 *
 * Custom URL schemes (chat mentions, deep-links, custom file viewers)
 * are best handled with the declarative `linkRules` prop — see the
 * type definition in `./types.ts` and the storybook for examples.
 *
 * @example
 * ```tsx
 * <MarkdownMessage content="# Hello\n\nThis is **bold** text." />
 *
 * // User message styling
 * <MarkdownMessage content="Some content" isUser />
 *
 * // Custom URL scheme via linkRules
 * <MarkdownMessage
 *   content="Talk to [Vps-audi](cmdop://machine/abc-123)"
 *   linkRules={[machineMentionRule]}
 * />
 * ```
 *
 * Memoised: re-renders only when props change. `content` is the main
 * trigger — all other props (className, isUser, size, etc.) are
 * compared by value/reference. `onCollapseChange` is compared by
 * reference — callers should stabilise it with useCallback.
 */
function MarkdownMessageRaw({
  content,
  className = '',
  isUser = false,
  size,
  isCompact = false,
  plainText,
  customComponents,
  extraHrefProtocols,
  linkRules,
  collapsible = false,
  maxLength,
  maxLines,
  readMoreLabel = 'Read more...',
  showLessLabel = 'Show less',
  defaultExpanded = false,
  onCollapseChange,
  streaming = false,
  codeTheme = 'auto',
}: MarkdownMessageProps) {
  // Pre-process content through any rules that requested it. Done
  // before trim so a rule can rewrite multi-line shapes too.
  const preprocessed = React.useMemo(
    () => applyPreprocess(content, linkRules),
    [content, linkRules],
  );

  // Union of `extraHrefProtocols` and any `protocols` declared by rules.
  const effectiveProtocols = React.useMemo(
    () => collectProtocols(extraHrefProtocols, linkRules),
    [extraHrefProtocols, linkRules],
  );

  // Effective custom components: merge linkRules' synthesized `a`
  // renderer with any caller-provided `customComponents`. linkRules
  // wins when both target the same href (rule is the more specific
  // declarative claim by design).
  const effectiveCustomComponents = React.useMemo<Partial<Components> | undefined>(() => {
    if (!linkRules || linkRules.length === 0) return customComponents;
    const callerA = customComponents?.a;
    const aRenderer = buildLinkRulesComponent(linkRules, isUser, callerA);
    return { ...(customComponents ?? {}), a: aRenderer };
  }, [customComponents, linkRules, isUser]);

  const trimmedContent = preprocessed.trim();

  // Collapsible content logic — defaults kick in only when enabled.
  const collapsibleOptions = React.useMemo(() => {
    if (!collapsible) return {};
    return {
      maxLength: maxLength ?? 1000,
      maxLines: maxLines ?? 10,
      defaultExpanded,
    };
  }, [collapsible, maxLength, maxLines, defaultExpanded]);

  const { isCollapsed, toggleCollapsed, displayContent, shouldCollapse } =
    useCollapsibleContent(trimmedContent, collapsible ? collapsibleOptions : {});

  React.useEffect(() => {
    if (collapsible && shouldCollapse && onCollapseChange) {
      onCollapseChange(isCollapsed);
    }
  }, [isCollapsed, collapsible, shouldCollapse, onCollapseChange]);

  // `size` wins when set explicitly; otherwise fall back to the
  // legacy binary `isCompact` so existing callers keep working.
  const resolvedSize: 'xs' | 'sm' | 'base' = size ?? (isCompact ? 'xs' : 'sm');

  const components = React.useMemo(() => {
    const base = createMarkdownComponents(isUser, resolvedSize, codeTheme);
    return effectiveCustomComponents ? { ...base, ...effectiveCustomComponents } : base;
  }, [isUser, resolvedSize, codeTheme, effectiveCustomComponents]);

  const schema = React.useMemo(() => buildSchema(effectiveProtocols), [effectiveProtocols]);
  const urlTransform = React.useMemo(
    () => buildUrlTransform(effectiveProtocols),
    [effectiveProtocols],
  );

  const textSizeClass = SIZE_TO_TEXT[resolvedSize];
  const proseClass = SIZE_TO_PROSE[resolvedSize];

  // Resolve plain-vs-markdown branch:
  //   1. Caller-passed `plainText` wins outright (explicit beats clever).
  //   2. Caller-supplied non-`a` customComponents force the markdown
  //      pipeline — those overrides only matter on real markdown nodes.
  //   3. Otherwise auto-detect via `looksLikePlainProse` (short,
  //      single-paragraph, no markdown markers). This is the chat-bubble
  //      WhatsApp/Telegram heuristic — "would the human have written
  //      this in one keystroke?".
  const customComponentsBeyondLinks = React.useMemo(() => {
    if (!customComponents) return false;
    return Object.keys(customComponents).some((k) => k !== 'a');
  }, [customComponents]);
  const isPlainText = plainText !== undefined
    ? plainText
    : !customComponentsBeyondLinks && looksLikePlainProse(displayContent);

  // Streaming mode is only meaningful on the markdown path and when not
  // collapsing (collapse is a finished-message concern). `plainText` and
  // `collapsible` both win over it.
  const isStreamingMarkdown = streaming && !isPlainText && !collapsible;

  // Block-split the in-flight document. Recomputed only when content
  // changes; cheap (single string pass). Stable blocks feed memoized
  // <MarkdownBlock>s so blocks 0..N-1 don't re-parse per token.
  const split = React.useMemo(
    () => (isStreamingMarkdown ? splitStreamingBlocks(displayContent) : null),
    [isStreamingMarkdown, displayContent],
  );

  if (isPlainText) {
    // <div> + whitespace-pre-wrap: respects newlines AND collapses
    // double spaces, which is what users mean when they hit Enter
    // twice. <span> would break flow inside a flex bubble.
    //
    // leading-snug (1.375), not leading-relaxed (1.625) — `pre-wrap`
    // makes every `\n` a hard line break, so the relaxed leading
    // turns multi-line user messages into airy ladders. snug matches
    // WhatsApp/Telegram bubble density.
    return (
      // `select-text` keeps prose selectable under native-host
      // `body { user-select: none }` (Wails/Electron); no-op on web.
      <div
        className={`select-text ${textSizeClass} font-normal antialiased leading-snug break-words whitespace-pre-wrap ${className}`}
      >
        {displayContent}
        {collapsible && shouldCollapse && (
          <>
            {isCollapsed && '... '}
            <CollapseToggle
              isCollapsed={isCollapsed}
              onClick={toggleCollapsed}
              readMoreLabel={readMoreLabel}
              showLessLabel={showLessLabel}
              isUser={isUser}
              isCompact={resolvedSize === 'xs'}
            />
          </>
        )}
      </div>
    );
  }

  // Prose wrapper class — shared by the static and streaming branches so
  // typography is byte-identical whether rendered in one pass or block by
  // block.
  const proseWrapperClass = `
    prose ${proseClass} max-w-none break-words overflow-hidden ${textSizeClass} font-normal antialiased
    ${isUser ? 'prose-invert' : 'dark:prose-invert'}
    [&>*]:leading-relaxed
    [&>*:first-child]:mt-0 [&>*:last-child]:mb-0
    [&_p]:my-2
    [&_ul]:my-2 [&_ol]:my-2 [&_ul]:pl-5 [&_ol]:pl-5
    [&_li]:my-1 [&_li>p]:my-0
    [&_h1]:mt-4 [&_h1]:mb-2 [&_h1]:text-base [&_h1]:font-semibold
    [&_h2]:mt-3.5 [&_h2]:mb-1.5 [&_h2]:text-[15px] [&_h2]:font-semibold
    [&_h3]:mt-3 [&_h3]:mb-1 [&_h3]:text-sm [&_h3]:font-medium
    [&_h4]:mt-3 [&_h4]:mb-1 [&_h4]:text-sm [&_h4]:font-medium
  `;
  const proseWrapperStyle = {
    // Inherit colors from parent — fixes issues with external CSS
    // variables overriding prose tokens.
    '--tw-prose-body': 'inherit',
    '--tw-prose-headings': 'inherit',
    '--tw-prose-bold': 'inherit',
    '--tw-prose-links': 'inherit',
    color: 'inherit',
  } as React.CSSProperties;

  // ── Streaming branch ──────────────────────────────────────────────────
  // Render completed blocks as memoized markdown; hold the in-flight tail
  // as raw text (boundary buffering) — or as an in-progress code block if
  // it's inside an unterminated fence. Same sanitize/components chain, so
  // identical XSS posture; just invoked per block instead of once.
  if (isStreamingMarkdown && split) {
    const tail = renderableTail(split.tail, split.tailInOpenFence);
    return (
      <div className={`select-text ${className}`}>
        <div className={proseWrapperClass} style={proseWrapperStyle}>
          {split.blocks.map((source, i) => (
            <MarkdownBlock
              // Index keys: streaming only appends/edits the tail, so
              // earlier blocks never reorder — index keys avoid unmount
              // churn while keeping the memo identity stable.
              key={i}
              source={source}
              components={components}
              schema={schema}
              urlTransform={urlTransform}
            />
          ))}
          {tail.source &&
            (tail.asCode ? (
              // Unterminated fence → render as an in-progress code block so
              // it doesn't swallow the rest of the message. The close fence
              // is virtual (appended to a copy); stored content is untouched.
              <MarkdownBlock
                key="tail-code"
                source={tail.source}
                components={components}
                schema={schema}
                urlTransform={urlTransform}
              />
            ) : (
              // Boundary buffering: the trailing incomplete line/block stays
              // raw `whitespace-pre-wrap` until a newline promotes it — no
              // flash of half-written `**bold` / `[link](`.
              <div className="whitespace-pre-wrap break-words leading-relaxed">
                {tail.source}
              </div>
            ))}
        </div>
      </div>
    );
  }

  // ── Static branch (finished message / non-streaming) ──────────────────
  return (
    // `select-text` keeps prose + code blocks selectable under native-host
    // `body { user-select: none }` (Wails/Electron); no-op on web.
    <div className={`select-text ${className}`}>
      <div className={proseWrapperClass} style={proseWrapperStyle}>
        <MarkdownBlock
          source={displayContent}
          components={components}
          schema={schema}
          urlTransform={urlTransform}
        />
      </div>
      {collapsible && shouldCollapse && (
        <CollapseToggle
          isCollapsed={isCollapsed}
          onClick={toggleCollapsed}
          readMoreLabel={readMoreLabel}
          showLessLabel={showLessLabel}
          isUser={isUser}
          isCompact={isCompact}
        />
      )}
    </div>
  );
};

export const MarkdownMessage = memo(MarkdownMessageRaw);

export default MarkdownMessage;
