/** Item that can be mentioned via @ trigger */
export interface MentionItem {
  id: string;
  label: string;
  description?: string;
  thumbnail?: string;
}

/**
 * Attributes available when rendering a mention to markdown.
 *
 * Same shape Tiptap stores on the `mention` node — `id` is the stable
 * identifier the suggestion popover injected, `label` is the human text
 * shown to the user. Either field may be empty if the upstream config
 * never populated it; renderers should fall back accordingly.
 */
export interface MentionAttrs {
  id: string;
  label: string;
}

/**
 * Function that converts a mention node into its markdown serialization.
 *
 * The returned string is what `@tiptap/markdown` writes into the markdown
 * output of `MarkdownEditor.getMarkdown()`.
 */
export type MentionMarkdownRenderer = (attrs: MentionAttrs) => string;

/** Mention configuration */
export interface MentionConfig {
  /** Trigger character (default: '@') */
  trigger?: string;
  /** Available items */
  items: MentionItem[];
  /** Max dropdown items (default: 5) */
  maxItems?: number;
  /**
   * Custom serializer for mentions when `MarkdownEditor.getMarkdown()` runs.
   *
   * Defaults to `mentionPresets.plainAt` which yields `@<label>` (or `@<id>`
   * when `label` is missing). Use one of `mentionPresets`, or supply your
   * own function for full control over how mentions appear in the output
   * markdown string.
   *
   * Note: this only affects the *markdown* output. `editor.getText()` and
   * the rendered DOM still go through `renderText` (`@<label>` by default).
   */
  renderMarkdown?: MentionMarkdownRenderer;
}
