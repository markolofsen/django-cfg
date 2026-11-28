import {
  CheckSquare,
  Code,
  Heading1,
  Heading2,
  Heading3,
  List,
  ListOrdered,
  Map as MapIcon,
  Minus,
  Quote,
  Table as TableIcon,
  Text,
  type LucideIcon,
} from 'lucide-react';
import type { Editor, Range } from '@tiptap/react';
import { DEFAULT_MAP_PAYLOAD } from './MapNode';

export interface SlashItem {
  title: string;
  description: string;
  icon: LucideIcon;
  /** Markdown shorthand hint shown right-aligned in the menu — teaches
   *  the user that they can also type this directly (e.g. `#`, `- [ ]`). */
  hint?: string;
  /** Extra search aliases (besides `title`). */
  aliases?: string[];
  command: (ctx: { editor: Editor; range: Range }) => void;
}

/**
 * Canonical Notion-style slash menu. Each command runs `deleteRange(range)`
 * first so the typed `/verb` text is removed, then applies the block
 * transformation. `focus()` keeps the caret in the editor after the
 * popover closes.
 */
export const slashItems: SlashItem[] = [
  {
    title: 'Text',
    description: 'Plain paragraph.',
    icon: Text,
    aliases: ['p', 'paragraph'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('paragraph').run();
    },
  },
  {
    title: 'Heading 1',
    description: 'Big section heading.',
    icon: Heading1,
    hint: '#',
    aliases: ['h1', 'title'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 1 }).run();
    },
  },
  {
    title: 'Heading 2',
    description: 'Medium section heading.',
    icon: Heading2,
    hint: '##',
    aliases: ['h2', 'subtitle'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 2 }).run();
    },
  },
  {
    title: 'Heading 3',
    description: 'Small section heading.',
    icon: Heading3,
    hint: '###',
    aliases: ['h3'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setNode('heading', { level: 3 }).run();
    },
  },
  {
    title: 'Bullet list',
    description: 'Simple unordered list.',
    icon: List,
    hint: '- ',
    aliases: ['ul', 'unordered'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBulletList().run();
    },
  },
  {
    title: 'Numbered list',
    description: 'List with auto-numbering.',
    icon: ListOrdered,
    hint: '1. ',
    aliases: ['ol', 'ordered', 'numbered'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleOrderedList().run();
    },
  },
  {
    title: 'To-do list',
    description: 'Tasks with checkboxes.',
    icon: CheckSquare,
    hint: '- [ ]',
    aliases: ['todo', 'task', 'checkbox', 'check'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleTaskList().run();
    },
  },
  {
    title: 'Quote',
    description: 'Capture a quote.',
    icon: Quote,
    hint: '> ',
    aliases: ['blockquote'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBlockquote().run();
    },
  },
  {
    title: 'Code block',
    description: 'Syntax-highlighted code.',
    icon: Code,
    hint: '```',
    aliases: ['codeblock', 'pre'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleCodeBlock().run();
    },
  },
  {
    title: 'Divider',
    description: 'Horizontal rule.',
    icon: Minus,
    hint: '---',
    aliases: ['hr', 'rule', 'separator'],
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setHorizontalRule().run();
    },
  },
  {
    title: 'Table',
    description: '3×3 starter table.',
    icon: TableIcon,
    aliases: ['grid'],
    command: ({ editor, range }) => {
      editor
        .chain()
        .focus()
        .deleteRange(range)
        .insertTable({ rows: 3, cols: 3, withHeaderRow: true })
        .run();
    },
  },
  {
    title: 'Map',
    description: 'Interactive map block.',
    icon: MapIcon,
    aliases: ['map', 'location', 'geo', 'pin'],
    command: ({ editor, range }) => {
      // Drop the typed `/map`, then insert a map block seeded with a sensible
      // default payload so the user sees a live map immediately. Attrs are
      // plain JSON and round-trip through markdown (see MapNode).
      editor
        .chain()
        .focus()
        .deleteRange(range)
        .setMapBlock({ ...DEFAULT_MAP_PAYLOAD })
        .run();
    },
  },
];

/** Case-insensitive filter over title + aliases. */
export function filterSlashItems(query: string): SlashItem[] {
  const q = query.trim().toLowerCase();
  if (!q) return slashItems;
  return slashItems.filter((item) => {
    if (item.title.toLowerCase().includes(q)) return true;
    return item.aliases?.some((a) => a.toLowerCase().includes(q)) ?? false;
  });
}
