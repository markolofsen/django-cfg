# NotionEditor

Notion-style WYSIWYG markdown editor built on **TipTap v3**.

Lazy-loaded sibling of [`MarkdownEditor`](../MarkdownEditor/) — same
markdown round-trip, but with a heavier extension stack, the floating
menus (slash / bubble / drag handle) users expect from a "document"
editor, **and serializable block nodes** (a link-preview *bookmark*
card and an interactive *map* block) that round-trip through markdown.

```tsx
import { NotionEditor } from '@djangocfg/ui-tools/notion-editor';

<NotionEditor
  value={markdown}
  onChange={setMarkdown}
  onSave={(md) => writeFile(md)}
  autoFocus
  placeholder="Type '/' for commands…"
  resolveLinkPreview={unfurl}   // optional — powers bookmark cards
/>
```

> **Bundle.** The full stack (lowlight common pack + tables + drag
> handle, plus the lazy MapLibre chunk when a map block mounts) lands
> around ~350 KB minified. `@djangocfg/ui-tools/notion-editor` is the
> **lazy** entry (`lazy.tsx`) — pages that never render the editor pay
> nothing. All of it is `'use client'`.

## When to use this vs `MarkdownEditor`

| Use case                                | Pick             |
| --------------------------------------- | ---------------- |
| Chat composer, single-paragraph input   | `MarkdownEditor` |
| Note / doc surface, multi-paragraph     | `NotionEditor`   |
| `.md` file viewer with full editing     | `NotionEditor`   |
| Slim mention dropdown, no tables/tasks  | `MarkdownEditor` |
| Slash menu, drag handle, tables, hljs   | `NotionEditor`   |
| Bookmark cards / embedded map blocks    | `NotionEditor`   |

The two coexist intentionally — `NotionEditor` is heavier; don't mount
it inside a chat composer just to get features the user will never use.

## Props

`NotionEditorProps` (see `types.ts`):

| Prop                 | Type                       | Default              | Notes |
| -------------------- | -------------------------- | -------------------- | ----- |
| `value`              | `string`                   | —                    | Markdown source (required). |
| `onChange`           | `(md: string) => void`     | —                    | Fired on every keystroke with freshly-serialised markdown (required). |
| `placeholder`        | `string`                   | `"Type '/' for commands…"` | Ghost text on an empty paragraph. |
| `disabled`           | `boolean`                  | `false`              | Read-only renderer (also makes map blocks static). |
| `autoFocus`          | `boolean`                  | `false`              | Focus on mount. Pair with `key={path}` upstream for fresh focus per file. |
| `onSave`             | `(md: string) => void`     | —                    | Bound to Cmd/Ctrl+S, scoped to the editor DOM. |
| `className`          | `string`                   | `''`                 | Extra class on the outer wrapper. |
| `minHeight`          | `number`                   | `320`                | Min height of the editor surface (px). |
| `resolveLinkPreview` | `ResolveLinkPreview`       | `undefined`          | **Host URL-unfurl resolver** threaded into the bookmark node. `undefined` → cards render a hostname/favicon fallback. See [nodes.md](./@docs/nodes.md#bookmark-block). |

`resolveLinkPreview` is captured on first build (memoised on
`[placeholder, resolveLinkPreview]`) — pass a **stable reference** (a
host method), not a new closure per render.

### Imperative API

```tsx
const ref = useRef<NotionEditorHandle>(null);

ref.current?.focus();             // focus the editor surface
ref.current?.moveCursorToEnd();   // focus + caret at end
ref.current?.getEditor();         // raw TipTap Editor (escape hatch)
```

`NotionEditorHandle` is structurally compatible with `ComposerHandle`
from `@djangocfg/ui-tools/composer-registry` — the chat suite can
register a NotionEditor as a composer if you ever want to swap them in.

## Features at a glance

- **Slash menu (`/`)** — 12 commands: Text, H1-H3, Bullet/Numbered/Todo
  lists, Quote, Code block, Divider, Table, and **Map**. Filtering by
  title + aliases; each item shows its markdown shorthand as a hint.
  See [slash.md](./@docs/slash.md).
- **Block nodes** — a **bookmark** (link-preview) card from pasting a
  bare URL on an empty line, and an interactive **map** block from
  `/map`. Both round-trip through markdown. See [nodes.md](./@docs/nodes.md).
- **Interactive map editing** — drag a pin, click-to-add, remove,
  switch basemap; every edit writes back into the document via
  `useNodeAttrs`. See [interactivity.md](./@docs/interactivity.md).
- **Safe block rendering** — each block parses its attrs through a Zod
  schema; a malformed payload renders `<BlockError>` instead of
  crashing the editor. See [interactivity.md](./@docs/interactivity.md#safe-rendering).
- **Bubble menu** — floating selection toolbar (Bold, Italic, Underline,
  Strike, Code, Highlight, Link) with shortcut tooltips. Auto-hides in
  code blocks and on empty selections.
- **Cmd+K link prompt**, **drag handle**, **smart Cmd+A**,
  **heading-aware placeholder**, **forced-dark code blocks**,
  **task list** (ui-core `<Checkbox>`), **Cmd+S save hook**,
  **markdown input rules**. See [editor.md](./@docs/editor.md).

## Docs

| Doc | Covers |
|---|---|
| [nodes.md](./@docs/nodes.md) | The **bookmark** + **map** block nodes — triggers, payload shapes, the `resolveLinkPreview` injection, and markdown serialisation / round-trip. |
| [interactivity.md](./@docs/interactivity.md) | The `useNodeAttrs` write-back seam (how map edits persist) and the Zod-validator / `<BlockError>` safety net. |
| [slash.md](./@docs/slash.md) | The `/` slash menu — the command list, filtering, and how to add a command (incl. `/map`). |
| [editor.md](./@docs/editor.md) | Base editor config — the TipTap extension stack, keymap, task items, drag handle, link dialog, markdown round-trip table, and known limitations. |
| [stories.md](./@docs/stories.md) | The Storybook stories list. |

## Files

| File                          | Purpose                                                     |
| ----------------------------- | ----------------------------------------------------------- |
| `lazy.tsx`                    | Subpath entry — `React.lazy` + `forwardRef` for the handle  |
| `NotionEditor.tsx`            | Main component + `BubbleSelectionToolbar`                   |
| `extensions.ts`              | Assembled TipTap stack (factory `notionExtensions()`)       |
| `types.ts`                    | `NotionEditorProps`, `NotionEditorHandle`                   |
| `BookmarkNode.ts` · `BookmarkView.tsx` | Bookmark (link-preview) block node + NodeView      |
| `MapNode.ts` · `MapView.tsx` · `MapEditLayer.tsx` | Map block node, NodeView, editable layer |
| `SlashExtension.ts`           | TipTap extension wrapping `@tiptap/suggestion`              |
| `createSlashSuggestion.ts`    | Suggestion config — floating-ui popup mount/update/teardown |
| `SlashList.tsx`               | Popover content (listbox + keyboard nav)                    |
| `slashItems.ts`               | Command list + `filterSlashItems` helper                    |
| `CustomKeymap.ts`             | Smart Cmd+A extension                                       |
| `TaskItemView.tsx`            | React NodeView for `taskItem` (mounts ui-core Checkbox)     |
| `LinkDialog.tsx`              | Cmd+K link prompt (ui-core Dialog)                          |
| `styles.css`                  | Typography + slash/bubble menu + drag handle + lowlight     |

Shared seams used by the block nodes live under `src/common/` (outside
this folder): `common/link-preview` (the `LinkPreviewCard` +
`ResolveLinkPreview` contract), `common/blocks` (payload types, Zod
schemas, `<BlockError>`), and `common/tiptap` (the `useNodeAttrs`
write-back hook).

## Saving — dirty / pristine handling

The editor calls `onChange` on every keystroke with the freshly
serialised markdown; the host owns state and detects "dirty" however it
likes. Two gotchas:

1. **TipTap re-serialises markdown on mount** (trailing newline, CRLF →
   LF). The first `onChange` after `setContent(value)` is byte-different
   from `value` even though nobody typed. Normalise both sides before a
   dirty comparison:

   ```ts
   const norm = (s: string) => s.replace(/\r\n/g, '\n').trimEnd();
   const isDirty = norm(draft) !== norm(saved);
   ```

2. **Cmd+S only fires when focus is inside the editor.** Add a
   window-level `useHotkey('mod+s', save)` in the host as a fallback —
   both paths call the same save fn.

See `cmdop/.../document-preview/viewers/text-viewer.tsx` for the
canonical wiring. Use `key={path}` on the wrapper if you remount per
file — that's what makes `autoFocus` fire on each file open.
