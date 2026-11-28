import type { MentionMarkdownRenderer } from './types';

/**
 * Escape characters that have meaning in markdown link/inline contexts.
 * Conservative — covers the chars that would break `[text](url)` and
 * inline emphasis when a label contains them.
 */
const escapeMd = (s: string): string => s.replace(/([\\[\]()_*~`])/g, '\\$1');

/**
 * Built-in serializers for the `MentionConfig.renderMarkdown` callback.
 *
 * Pick one based on what consumes the markdown:
 *
 * - LLM / chat composer    → `plainAt`     (the default)
 * - Plain text export      → `plainLabel`
 * - Web app with deep-link → `markdownLink(baseUrl)`
 * - Notion / Linear-style  → `customUri(scheme, kind)`
 * - Slack-style id refs    → `slackStyle`
 * - HTML-allowing renderer → `htmlSpan(className?)`
 *
 * Or pass a custom function — the type is just `(attrs) => string`.
 */
export const mentionPresets = {
  /** "@Label" — default, ideal for chat where LLMs read the text. */
  plainAt: (({ label, id }) => `@${label || id}`) as MentionMarkdownRenderer,

  /** "Label" — bare label, no @ prefix. */
  plainLabel: (({ label, id }) => label || id) as MentionMarkdownRenderer,

  /** "[@Label](baseUrl/id)" — clickable markdown link. */
  markdownLink: (baseUrl: string): MentionMarkdownRenderer =>
    ({ label, id }) =>
      `[@${escapeMd(label || id)}](${baseUrl}${encodeURIComponent(id)})`,

  /** "@[Label](scheme://kind/id)" — Notion / Linear-style custom URI. */
  customUri: (scheme: string, kind: string): MentionMarkdownRenderer =>
    ({ label, id }) =>
      `@[${escapeMd(label || id)}](${scheme}://${kind}/${encodeURIComponent(id)})`,

  /** "<@id>" — Slack-style id-only reference (label dropped — receivers resolve it). */
  slackStyle: (({ id }) => `<@${id}>`) as MentionMarkdownRenderer,

  /** Inline HTML span — for products that consume markdown with raw HTML allowed. */
  htmlSpan:
    (className = 'mention'): MentionMarkdownRenderer =>
    ({ label, id }) =>
      `<span class="${className}" data-mention-id="${encodeURIComponent(id)}">@${escapeMd(label || id)}</span>`,
};
