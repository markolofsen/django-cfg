import type { AnyExtension } from '@tiptap/core';
import { ReactNodeViewRenderer } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Highlight from '@tiptap/extension-highlight';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { Table } from '@tiptap/extension-table';
import { TableRow } from '@tiptap/extension-table-row';
import { TableHeader } from '@tiptap/extension-table-header';
import { TableCell } from '@tiptap/extension-table-cell';
import CodeBlockLowlight from '@tiptap/extension-code-block-lowlight';
import { Markdown } from '@tiptap/markdown';
import { common, createLowlight } from 'lowlight';
import GlobalDragHandle from 'tiptap-extension-global-drag-handle';
import { SlashExtension } from './SlashExtension';
import { createSlashSuggestion } from './createSlashSuggestion';
import { TaskItemView } from './TaskItemView';
import { CustomKeymap } from './CustomKeymap';
import { BookmarkNode } from './BookmarkNode';
import { MapNode } from './MapNode';
import type { ResolveLinkPreview } from '../link-preview';

// Lowlight bundle: "common" languages cover ts/js/json/py/go/rust/etc.
// The full language pack pulls in ~300KB more — opt-in case by case.
const lowlight = createLowlight(common);

export interface BuildExtensionsOptions {
  placeholder: string;
  /**
   * Host resolver for the `bookmark` (link-preview) node. Given a URL it
   * returns unfurl metadata. Threaded into `BookmarkNode.options` and read by
   * its NodeView. Default `undefined` → the card renders its own
   * hostname/favicon fallback (same seam as chat's `config.linkPreview`).
   */
  resolveLinkPreview?: ResolveLinkPreview;
}

/**
 * Assemble the Notion-flavour TipTap extension stack.
 *
 * Why a single factory rather than inline `useEditor({ extensions: [...] })`:
 *   - `useEditor` captures extensions once on first render. If we built
 *     them inline, every parent re-render would create new instances and
 *     React's deps array would force a teardown loop (or, with stable
 *     deps, we'd be hiding the problem).
 *   - All consumers want the same baseline. Splitting per-extension wires
 *     to a builder keeps the assembly readable.
 *
 * StarterKit overrides:
 *   - `codeBlock: false` — replaced by `CodeBlockLowlight` for syntax
 *     highlighting via lowlight's `common` language pack.
 *
 * Markdown serialisation:
 *   - `@tiptap/markdown` already handles starter-kit nodes + tables.
 *   - Task lists serialise as GFM `- [x]` / `- [ ]` via the same package.
 *   - `Highlight` round-trips as `==text==` (tiptap-markdown default).
 */
export function notionExtensions(opts: BuildExtensionsOptions): AnyExtension[] {
  return [
    StarterKit.configure({
      heading: { levels: [1, 2, 3, 4] },
      // Disable starter-kit's plain CodeBlock — we replace it with the
      // lowlight variant below for syntax highlighting.
      codeBlock: false,
    }),
    Placeholder.configure({
      // Per-node placeholder: empty H1 → "Heading 1", H2 → "Heading 2",
      // empty paragraph → the supplied placeholder ("Type / for…").
      // Matches Notion: an empty heading is labelled with its level so the
      // user sees structure before content; an empty body block shows the
      // command hint. The function form is supported by tiptap-extensions
      // Placeholder; the `node` arg is the block at the caret.
      placeholder: ({ node }) => {
        if (node.type.name === 'heading') {
          const level = node.attrs.level as number | undefined;
          return level ? `Heading ${level}` : 'Heading';
        }
        return opts.placeholder;
      },
      // includeChildren=true so placeholders also reach inside list items
      // and quotes (otherwise an empty bullet line shows no hint).
      includeChildren: true,
    }),
    Markdown,
    Highlight.configure({ multicolor: false }),
    TaskList,
    // React NodeView swaps Tiptap's default `<input type="checkbox">`
    // for our ui-core <Checkbox> — picks up macOS / token styling and
    // tracks the editor theme automatically. See TaskItemView.tsx.
    TaskItem.extend({
      addNodeView() {
        return ReactNodeViewRenderer(TaskItemView);
      },
    }).configure({ nested: true }),
    Table.configure({ resizable: false }),
    TableRow,
    TableHeader,
    TableCell,
    CodeBlockLowlight.configure({ lowlight }),
    // Drag handle for blocks. Renders a small grabber to the left of the
    // hovered block; clicking + dragging reorders the document. Reads CSS
    // from our styles.css (`.drag-handle`).
    GlobalDragHandle.configure({
      dragHandleWidth: 18,
      // `scrollTreshold` (sic) is the option name the upstream library
      // ships — typo and all. Spelling it correctly is silently ignored.
      scrollTreshold: 100,
    }),
    // Bookmark (link-preview) block — paste a bare URL on an empty line and
    // it becomes a card. The host resolver is threaded through options.
    BookmarkNode.configure({ resolveLinkPreview: opts.resolveLinkPreview }),
    // Map block — inserted via the `/map` slash command (see slashItems).
    MapNode,
    SlashExtension.configure({
      suggestion: createSlashSuggestion(),
    }),
    CustomKeymap,
  ];
}
