/**
 * `SlashCommandNode` — TipTap inline atom that renders a chosen slash
 * verb as a styled chip inside the editor, analogous to how
 * `@tiptap/extension-mention` renders an `@user` pill.
 *
 * Why a node (and not a mark / decoration):
 *
 * - The chip must read as one indivisible unit — pressing Backspace
 *   removes the whole `/verb`, not the trailing letter. That's
 *   exactly what `atom: true` + `inline: true` give us.
 * - The chip's text content (`/verb`) participates in `editor.getText()`
 *   and the markdown serializer's text output so the host's
 *   `composer.value` round-trips to the same plain string the plain
 *   `<SlashHighlightTextarea>` produces. The slash hook (which lives on
 *   the string buffer) stays oblivious to the node form.
 *
 * Render parity with the plain mirror:
 *
 * The chip class `markdown-slash-command` mirrors the plain textarea's
 * `bg-primary/15 text-primary` look (see `SlashHighlightTextarea.tsx`).
 * Styles live in `../styles.css`. The TipTap chip can carry a touch of
 * horizontal padding without breaking the caret — the node is atomic
 * so the caret never lands inside it — which the plain mirror cannot.
 */
import { Node, mergeAttributes } from '@tiptap/core';

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    slashCommand: {
      /**
       * Insert a slash-command atom at the given absolute document
       * position. The host normally calls this once per `pick()`
       * after the slash hook has produced the new string buffer.
       */
      insertSlashCommandAt: (
        pos: number,
        from: number,
        to: number,
        attrs: { id: string; token: string },
      ) => ReturnType;
    };
  }
}

export interface SlashCommandNodeOptions {
  /** Extra HTML attrs spread onto the rendered `<span>`. */
  HTMLAttributes: Record<string, unknown>;
}

/**
 * Inline atom node that paints a `/verb` chip inside the TipTap editor.
 *
 * - `inline: true` — lives next to text in a paragraph.
 * - `atom: true`   — caret cannot land inside it; Backspace removes it
 *   wholesale, matching the plain mirror's "the verb is one token"
 *   feel.
 * - `selectable: false` — clicking the chip does not stick a node
 *   selection on it (mention does the same).
 *
 * `renderText` returns the bare `/verb` so `editor.getText()` (and
 * therefore the host `composer.value`) reads the same string the plain
 * mirror produces. This is what keeps the slash hook — which only
 * understands strings — driving the menu correctly when the editor is
 * TipTap-backed.
 */
export const SlashCommandNode = Node.create<SlashCommandNodeOptions>({
  name: 'slashCommand',
  group: 'inline',
  inline: true,
  atom: true,
  selectable: false,
  // Higher than StarterKit text so paste rules etc. don't try to
  // re-parse our chip text as plain.
  priority: 101,

  addOptions() {
    return {
      HTMLAttributes: {},
    };
  },

  addAttributes() {
    return {
      id: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-id'),
        renderHTML: (attrs) =>
          attrs.id ? { 'data-id': attrs.id as string } : {},
      },
      token: {
        default: null,
        parseHTML: (element) => element.getAttribute('data-token'),
        renderHTML: (attrs) =>
          attrs.token ? { 'data-token': attrs.token as string } : {},
      },
    };
  },

  parseHTML() {
    return [{ tag: `span[data-type="${this.name}"]` }];
  },

  renderHTML({ node, HTMLAttributes }) {
    const token =
      (node.attrs.token as string | null) ??
      (node.attrs.id ? `/${node.attrs.id as string}` : '/');
    return [
      'span',
      mergeAttributes(
        { 'data-type': this.name, class: 'markdown-slash-command' },
        this.options.HTMLAttributes,
        HTMLAttributes,
      ),
      token,
    ];
  },

  // `editor.getText()` and the markdown text-serializer fallback read
  // this — the chip flattens to its raw `/verb` glyph so consumers
  // (slash hook, transport, backends) see plain text.
  renderText({ node }) {
    const token =
      (node.attrs.token as string | null) ??
      (node.attrs.id ? `/${node.attrs.id as string}` : '/');
    return token;
  },

  // `@tiptap/markdown` reads `renderMarkdown` off the extension at
  // registration time. We emit the bare token, NOT the default
  // shortcode `[slashCommand id="..."]`, so a round-trip through
  // `getMarkdown()` yields the same `/verb argument` string the plain
  // mirror produces. Slash commands never need re-parsed back from
  // markdown — fresh value sync handles that via
  // `syncLeadingSlashNode` after each `setContent`.
  renderMarkdown(node) {
    const attrs = node.attrs as { token?: string | null; id?: string | null };
    const token = attrs.token ?? (attrs.id ? `/${attrs.id}` : '');
    return token;
  },

  addCommands() {
    return {
      insertSlashCommandAt:
        (pos, from, to, attrs) =>
        ({ chain }) => {
          // Replace the [from, to) range (typically the leading `/verb`
          // text the user just had the menu narrow down) with the atom
          // node. `pos` is unused here but kept in the signature for
          // future use (e.g. cursor-driven insertion not anchored at
          // the start of the doc).
          void pos;
          return chain()
            .insertContentAt(
              { from, to },
              { type: 'slashCommand', attrs },
            )
            .run();
        },
    };
  },
});
