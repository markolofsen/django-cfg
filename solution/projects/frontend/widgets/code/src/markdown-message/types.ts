import type React from 'react';
import type { Components } from 'react-markdown';

/**
 * Declarative rule for handling a custom URL scheme inside markdown.
 *
 * Each rule owns one href shape (e.g. `cmdop://machine/<uuid>`,
 * `obsidian://open?path=…`) and decides:
 *
 *   1. Whether the URL scheme survives sanitize (`protocols`).
 *   2. How to massage the source markdown before render
 *      (`preprocess` — optional; useful for stripping decorative
 *      prefixes like the `@` in `@[label](href)` so the chip alone
 *      reads as the mention indicator).
 *   3. Which links it owns (`match`), and how to render them
 *      (`render`, returning JSX).
 *
 * Rules compose: pass an array, and the renderer iterates top-to-bottom
 * picking the first `match` hit per `<a>`. Anything no rule claims
 * falls through to the built-in chat-link styling (or to a custom
 * `customComponents.a` if both are provided).
 *
 * Prefer `linkRules` over `customComponents` + `extraHrefProtocols` —
 * it's the same pieces with the boilerplate removed.
 */
export interface LinkRule {
  /** Pre-process the raw markdown source before any rendering happens.
   *  Pure / synchronous; identity-return when no transform applies. */
  preprocess?: (source: string) => string;
  /** Predicate against the resolved href. */
  match: (href: string) => boolean;
  /** Render the link this rule owns. `children` is the link's label
   *  (markdown-rendered React content). */
  render: (props: {
    href: string;
    children: React.ReactNode;
    isUser: boolean;
  }) => React.ReactNode;
  /** URL scheme(s) to whitelist on the sanitize side, e.g. `['cmdop']`.
   *  Bare schemes only — no `://`. Optional; omit for `http(s)` rules. */
  protocols?: readonly string[];
  /** Diagnostic label, surfaced in dev warnings. Optional. */
  name?: string;
}

export interface MarkdownMessageProps {
  /** Markdown content to render */
  content: string;
  /** Additional CSS classes */
  className?: string;
  /** Whether the message is from the user (affects styling) */
  isUser?: boolean;
  /**
   * Body text size — drives `<p>/<li>/<table>` etc. and scales
   * headings a notch above the body.
   *
   * - `xs` — text-xs (12px), dense
   * - `sm` — text-sm (14px), default
   * - `base` — text-base (16px), large / `appearance="full"` chats
   *
   * When set, `size` wins over `isCompact`.
   * @default 'sm'
   */
  size?: 'xs' | 'sm' | 'base';
  /**
   * Use compact size (text-xs instead of text-sm).
   * @deprecated Use `size` instead — `isCompact` maps to
   * `size="xs"` (true) / `size="sm"` (false) and is ignored when
   * `size` is set explicitly.
   */
  isCompact?: boolean;
  /**
   * Force the plain-text rendering path (single `<div>` with
   * `white-space: pre-wrap`, no ReactMarkdown). Use this for
   * user-authored content where markdown shouldn't be parsed.
   *
   * When `undefined` (default) we run a small heuristic
   * (`looksLikePlainProse`): short single-paragraph text without
   * markdown markers → plain; everything else → ReactMarkdown.
   *
   * Pass an explicit `true` / `false` to opt out of the heuristic
   * entirely.
   */
  plainText?: boolean;
  /**
   * Per-tag overrides merged on top of the built-in renderers.
   *
   * Use this when you need custom rendering for a specific tag without
   * losing the chat-tuned defaults (links, code blocks with copy, etc).
   *
   * For custom URL-scheme link handling, prefer `linkRules` — it's the
   * same ergonomics with the per-consumer boilerplate removed.
   */
  customComponents?: Partial<Components>;
  /**
   * Extra URL protocols allowed in `<a href>` after sanitize.
   *
   * The default schema strips anything that isn't
   * `http(s)/mailto/xmpp/irc(s)` — your custom renderer would receive
   * `href={undefined}` for `cmdop://…` / `obsidian://…` etc. Listing
   * the bare scheme here (e.g. `'cmdop'`, NOT `'cmdop://'`) opts it in.
   *
   * Use carefully: every protocol you add increases what the rendered
   * HTML can do via clicks. Stick to schemes you control.
   */
  extraHrefProtocols?: readonly string[];
  /**
   * Declarative link rules — preferred over `customComponents` +
   * `extraHrefProtocols` for chat-style apps that want pluggable
   * URL-scheme handling without re-implementing the custom-`a`
   * boilerplate per consumer.
   *
   * If you provide both `linkRules` and `extraHrefProtocols`, the
   * effective protocol list is the union of the two.
   */
  linkRules?: readonly LinkRule[];
  /**
   * Enable collapsible "Read more..." functionality
   * @default false
   */
  collapsible?: boolean;
  /** Maximum character length before showing "Read more...". */
  maxLength?: number;
  /** Maximum number of lines before showing "Read more...". */
  maxLines?: number;
  /** Custom "Read more" button text. @default "Read more..." */
  readMoreLabel?: string;
  /** Custom "Show less" button text. @default "Show less" */
  showLessLabel?: string;
  /** Start expanded (only when `collapsible` is true). @default false */
  defaultExpanded?: boolean;
  /** Callback when collapsed state changes */
  onCollapseChange?: (isCollapsed: boolean) => void;
  /**
   * Live-streaming mode. When `true`, the content is treated as a
   * partial markdown document still receiving tokens:
   *
   * - Completed top-level blocks render as memoized markdown (blocks
   *   0..N-1 don't re-parse as new tokens land → ~O(n), not O(n²)).
   * - The trailing in-flight block is held back as raw `whitespace-pre-wrap`
   *   text until it reaches a safe boundary (a newline), so half-written
   *   `**bold` / `[link](` don't flash formatted-then-broken.
   * - An unterminated fenced code block renders as an in-progress code
   *   block instead of swallowing the rest of the message.
   *
   * Ignored when `plainText` is `true` (plain wins outright) or when
   * `collapsible` is set (collapsing is a post-stream concern). Has no
   * effect on the finished message — pass `false` (the default) once the
   * stream completes to get a single fully-parsed render.
   *
   * @default false
   */
  streaming?: boolean;
  /**
   * Code-fence surface palette.
   *
   * @default 'auto' — follow the host theme, the same resolution
   * `PrettyCode` performs on its own. `'dark'` / `'light'` PIN the palette
   * regardless of theme (e.g. printing on a light page).
   *
   * This defaulted to `'dark'`, which pinned every chat fence dark even in
   * the light theme. `PrettyCode` treats `mode` as an explicit override
   * (`mode ?? resolvedTheme`), so the pin also reached `CodePanelHeader`
   * via `dark={isDarkMode}` — the "typescript" label and copy icon rendered
   * in `text-white/40` on the panel, i.e. near-white on near-white.
   */
  codeTheme?: 'dark' | 'light' | 'auto';
}
