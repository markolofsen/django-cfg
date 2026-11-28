/**
 * `BookmarkNode` — a NotionEditor block ATOM node that renders a link-preview
 * "bookmark" card (the shared `common/link-preview/LinkPreviewCard`). It holds
 * a single `url` attribute and renders via a React NodeView (mirrors
 * `TaskItemView` → `ReactNodeViewRenderer`).
 *
 * Trigger — paste a BARE URL on an EMPTY line/block:
 *
 *   The `handlePaste` plugin only hijacks the paste when the clipboard is a
 *   SINGLE bare URL AND the current block is empty (an empty paragraph). In
 *   that case it replaces the empty block with a `bookmark` node. A URL
 *   pasted mid-text, a labelled link, or multi-line clipboard content all
 *   fall through to the editor's normal paste (the URL stays inline). This is
 *   the conservative Notion rule — bookmark only on an explicit empty line.
 *
 * Resolver injection:
 *
 *   `notionExtensions({ resolveLinkPreview })` threads a host resolver into
 *   the node's `options`. The NodeView reads it from `extension.options` and
 *   passes it to the card, so the host (Wails/Go, a Next.js API route) unfurls
 *   the URL exactly like chat does. Default `undefined` → the card renders its
 *   own hostname/favicon fallback.
 *
 * Serialisation (markdown fidelity):
 *
 *   `renderMarkdown` emits the bare `url`, so `getMarkdown()` yields the raw
 *   URL (NOT card markup) — same pattern the MarkdownEditor chip node uses.
 *   On the next `setContent`/paste of a bare URL on an empty line the node is
 *   re-created, so the round-trip is stable.
 */

import { Node, mergeAttributes } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import { Plugin, PluginKey } from '@tiptap/pm/state';
import type { ResolveLinkPreview } from '../link-preview';
import { BookmarkView } from './BookmarkView';

export interface BookmarkNodeOptions {
  /** Host resolver for URL unfurl. Default `undefined` → card fallback. */
  resolveLinkPreview?: ResolveLinkPreview;
  HTMLAttributes: Record<string, unknown>;
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    bookmark: {
      /** Insert a bookmark (link-preview) block for the given URL. */
      setBookmark: (url: string) => ReturnType;
    };
  }
}

const bookmarkPasteKey = new PluginKey('notion-bookmark-paste');

/** A single bare URL (http/https), nothing else on the line. */
const BARE_URL_RE = /^https?:\/\/[^\s<>]+$/i;

/** True when `text` is exactly one bare URL (no surrounding prose). */
function isBareUrl(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed || /\s/.test(trimmed)) return false;
  return BARE_URL_RE.test(trimmed);
}

export const BookmarkNode = Node.create<BookmarkNodeOptions>({
  name: 'bookmark',
  group: 'block',
  atom: true,
  draggable: true,
  selectable: true,

  addOptions() {
    return {
      resolveLinkPreview: undefined,
      HTMLAttributes: {},
    };
  },

  addAttributes() {
    return {
      url: {
        default: '',
        parseHTML: (el) => el.getAttribute('data-url') ?? '',
        renderHTML: (attrs) => (attrs.url ? { 'data-url': attrs.url as string } : {}),
      },
    };
  },

  parseHTML() {
    return [{ tag: 'div[data-type="bookmark"]' }];
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      mergeAttributes({ 'data-type': 'bookmark' }, this.options.HTMLAttributes, HTMLAttributes),
    ];
  },

  addNodeView() {
    return ReactNodeViewRenderer(BookmarkView);
  },

  addCommands() {
    return {
      setBookmark:
        (url: string) =>
        ({ commands }) =>
          commands.insertContent({ type: this.name, attrs: { url } }),
    };
  },

  // `@tiptap/markdown` reads this — emit the bare URL so a round-trip through
  // `getMarkdown()` yields the literal URL, never card markup.
  // `attrs` is optional in tiptap's `JSONContent`: a node written by hand or
  // arriving from a paste can carry none, and the narrower annotation this had
  // made the signature incompatible rather than making the object safer.
  renderMarkdown(node: { attrs?: Record<string, unknown> }) {
    return (node.attrs?.url as string) ?? '';
  },

  addProseMirrorPlugins() {
    const type = this.type;

    return [
      new Plugin({
        key: bookmarkPasteKey,
        props: {
          // Bare-URL-on-empty-line → bookmark. Conservative: only when the
          // clipboard is a SINGLE bare URL and the current textblock is empty.
          handlePaste: (view, event) => {
            const text = event.clipboardData?.getData('text/plain');
            if (!text || !isBareUrl(text)) return false;

            const { state } = view;
            const { selection } = state;
            const { $from, empty } = selection;
            // Only replace when the caret sits in an EMPTY textblock with a
            // collapsed selection — i.e. the user is on a fresh empty line.
            if (!empty) return false;
            const parent = $from.parent;
            if (!parent.isTextblock || parent.content.size !== 0) return false;

            const url = text.trim();
            // Replace the empty block with the bookmark node.
            const node = type.create({ url });
            const tr = state.tr.replaceWith(
              $from.before(),
              $from.after(),
              node,
            );
            view.dispatch(tr.scrollIntoView());
            return true;
          },
        },
      }),
    ];
  },
});

export default BookmarkNode;
