# Tree

A decomposed, shadcn-styled tree for `@djangocfg/ui-tools`. Pure React engine, zero external tree libraries. Generic over `T`, slot-driven, async-friendly, **with built-in Finder/Explorer CRUD UX** when you provide an `adapter`.

Ships two entry points:

- **`<TreeRoot>`** — every prop is opt-in. Use for read-only / display trees.
- **`<FinderTree>`** — opinionated Finder/Explorer preset: multi-select, double-click activation, inline rename, indent guides, Finder hotkeys, cozy density. Override anything by passing the same prop.

## Why this exists

We tried popular headless tree engines first. They all leak React-integration bugs (state references, mounting order, click handlers desyncing from re-renders). So this tree is intentionally small and predictable: a `useReducer` holds the state, a `flattenTree` walk produces visible rows, components consume those rows. No black boxes.

## Philosophy

1. **No engine.** State lives in plain React. Every interaction goes through React's commit cycle.
2. **Generic over `T`.** Tree nodes carry your domain payload (`File`, `Project`, `JsonNode`, …). The component never assumes filesystem semantics — but it provides a Finder-shaped affordance layer (`TreeAdapter`) for those that want one.
3. **Sync or async.** Pass inline `children: TreeNode<T>[]` for sync data, or omit them and provide `loadChildren` for lazy loading. The async cache de-duplicates concurrent fetches.
4. **Slots over props.** New visual needs add a slot, not a flag: `renderRow` / `renderIcon` / `renderLabel` / `renderActions` / `renderContextMenu`.
5. **CRUD = adapter, not props.** The host app describes how to delete / rename / move / etc. through a single `TreeAdapter<T>` object. Tree owns the UX (dialogs, hotkeys, menus) and calls back into the adapter. No `onDelete`/`onRename`/... prop sprawl.
6. **Dialogs come from `<DialogProvider>`.** Tree never re-implements its own dialogs. Built-in CRUD flows resolve `window.dialog` (installed by `@djangocfg/ui-core/lib/dialog-service`). If the host app hasn't mounted it, CRUD flows silently no-op with a dev-mode warning — Tree itself still renders.
7. **CSS-variable theming.** Density, sizes, gaps, indent — all exposed as `--tree-*` variables on the root. Override in any consumer without re-implementing components.
8. **Honest empty semantics.** An empty collection is announced as a status and
   does not expose an invalid, focusable ARIA tree until at least one tree item
   exists.

## Layered architecture

```
types/                              public types — generic over T, no `any`, folders-per-concept
  node.ts                           TreeItemId / TreeNode / FlatRow
  selection.ts                      TreeSelectionMode
  activation.ts                     TreeActivationMode / TreeActivateOptions
  loader.ts                         TreeLoadChildren
  labels.ts                         TreeLabels + DEFAULT_TREE_LABELS (CRUD copy too)
  slots.ts                          TreeRowSlot / TreeContextMenuSlot / TreeContextMenuItem / …
  adapter.ts                        TreeAdapter / TreeBuiltinAction / TreeMovePosition
  root-props.ts                     TreeRootProps

TreeRoot.tsx                        high-level entry — Provider + shell + content
TreeDndProvider.tsx                 thin <DndContext> wrapper (no-op when DnD off)
FinderTree.tsx                      Finder/Explorer preset over TreeRoot
lazy.tsx                            LazyTree via createLazyComponent

data/                               pure helpers, zero React
  appearance.ts                     density / accent / radius / sizes → CSS vars + classes
  childCache.ts                     id → { status, children, error }
  flatten.ts                        roots + expanded + cache → FlatRow<T>[]
  persist.ts                        versioned localStorage helper
  createDemoTree.ts                 deterministic synthetic tree for stories/tests
  selection.ts                      Finder selection: anchor + shift-range + ⌘+A
  clipboard.ts                      tree-local cut/copy state
  renameUtils.ts                    splitFileName / autoSelectRange (base without ext)
  finderShortcuts.ts                Finder/Explorer keymap (mod+⌫, F2, ⌘D, …)
  dnd.ts                            resolveDropZone + defaultCanDrop (cycle / self-drop)

context/                            Provider + per-feature hooks (folders-per-feature)
  TreeContext.tsx                   thin assembly: stitches the hooks below into one value
  TreeContextValue.ts               interface TreeContextValue<T>
  hooks.ts                          public hooks: useTreeSelection / Expansion / Rename / Clipboard / Dnd / …
  state/                            reducer + initial state + action types
  async-children/                   cache + nodeById + fetchChildren + refresh / refreshAll
  expansion/                        expand / collapse / toggle / expandAll / collapseAll
  selection/                        clickSelect / moveSelect / selectAll + plain select / clear
  rename/                           startRename / cancelRename / commitRename (window.dialog.alert on error)
  clipboard/                        cutToClipboard / copyToClipboard / pasteFromClipboard
  menu/                             built-in actions registry + merged declarative resolver
  dnd/                              draggingIds / dropTarget / commitDrop / canDrop layering
  persist/                          localStorage + onSelectionChange / onExpansionChange notify

hooks/                              container-level keyboard hooks (folders-per-scope)
  keyboard/                         ↑↓ ←→ Home/End Enter/Space Esc ⌘+A (Shift extends)
  type-ahead/                       Finder-style 600 ms prefix buffer
  finder-hotkeys/                   ⌘⌫ F2 ⌘D ⌘N ⌘⇧N ⌘C ⌘X ⌘V → adapter actions

components/
  TreeRow.tsx                       default row: chevron + icon + label + actions + ctx-menu
  TreeRenameInput.tsx               inline rename input (auto-selects base name without extension)
  TreeDropIndicator.tsx             drop indicator (before / after line, inside fill)
  TreeEmptyArea.tsx                 fills space below last row — empty context menu + root drop target
  TreeChevron / TreeIcon / TreeLabel / TreeIndentGuides
  TreeSearchInput.tsx               controlled search input
  TreeContent.tsx                   iterates flatRows, default-renders TreeRow
  TreeEmpty / TreeSkeleton / TreeError
```

Dependency direction: `components → context → data → types`. `hooks/` consume `context/` and `data/`. Pure helpers (`data/`, `hooks/*/match-prefix.ts`, `hooks/keyboard/arrow-nav.ts`, …) are unit-testable without a DOM.

## Quick start

```tsx
import { TreeRoot, type TreeNode } from '@djangocfg/ui-tools/tree';

interface FsNode { name: string }

const data: TreeNode<FsNode>[] = [
  {
    id: 'src',
    data: { name: 'src' },
    children: [{ id: 'index.ts', data: { name: 'index.ts' } }],
  },
];

<TreeRoot<FsNode>
  data={data}
  getItemName={(n) => n.data.name}
  onSelectionChange={(ids) => console.log(ids)}
  onActivate={(node) => openFile(node.id)}
  enableSearch
  showIndentGuides
  persistKey="settings.fileTree"
/>
```

## Finder/Explorer preset

`<FinderTree>` is `<TreeRoot>` with sensible Finder defaults pre-set:

```tsx
import { FinderTree, type TreeAdapter } from '@djangocfg/ui-tools/tree';

const fsAdapter: TreeAdapter<FsNode> = {
  remove: async (nodes) => api.delete(nodes.map((n) => n.id)),
  rename: async (node, name) => api.rename(node.id, name),
  createFolder: async (parent, name) => api.mkdir(parent?.id ?? null, name),
  move: async (nodes, target) => api.move(nodes.map((n) => n.id), target?.id ?? null),
  // …
};

<FinderTree<FsNode>
  data={data}
  getItemName={(n) => n.data.name}
  adapter={fsAdapter}
/>
```

Equivalent to:

```tsx
<TreeRoot<FsNode>
  data={data}
  getItemName={(n) => n.data.name}
  adapter={fsAdapter}
  selectionMode="multiple"
  activationMode="double-click"
  enableInlineRename
  enableFinderHotkeys
  enableTypeAhead
  showIndentGuides
  appearance={{ density: 'cozy' }}
/>
```

Override any default by passing the prop:

```tsx
<FinderTree
  /* …data, getItemName, adapter… */
  activationMode="single-click-preview"   // VSCode/Cursor preview tabs
  selectionMode="single"                  // disable multi-select
/>
```

## Async children

```tsx
const data: TreeNode<FsNode>[] = [
  { id: 'root', data: { name: 'remote' }, isFolder: true },
];

<TreeRoot<FsNode>
  data={data}
  getItemName={(n) => n.data.name}
  loadChildren={async (node) => {
    const list = await fetchChildren(node.id);
    return list.map((it) => ({ id: it.id, data: it, isFolder: it.isDir }));
  }}
/>
```

The provider caches resolved children, de-duplicates concurrent fetches per id, and re-renders when the cache mutates. Use `useTreeActions().refresh(id)` to invalidate one node, or `refreshAll()` after a backend signal.

## Composition mode

```tsx
import {
  TreeProvider, TreeContent, TreeSearchInput,
  useTreeSelection, useTreeActions,
} from '@djangocfg/ui-tools/tree';

<TreeProvider data={data} getItemName={getName}>
  <Toolbar />
  <TreeSearchInput />
  <TreeContent>{(row) => <CustomRow {...row} />}</TreeContent>
</TreeProvider>

function Toolbar() {
  const { expandAll, collapseAll, refreshAll } = useTreeActions();
  // …
}
```

## Multi-selection (Finder / Explorer semantics)

When `selectionMode="multiple"`, Tree implements full file-manager selection:

| Gesture | Behaviour |
| --- | --- |
| **plain click** | replace selection, set anchor |
| **⌘ / Ctrl + click** | toggle row, set anchor |
| **shift + click** | range from anchor to clicked row |
| **shift + ⌘ + click** | union range with existing selection |
| **shift + ↑/↓** | extend range one row from anchor |
| **shift + Home / End** | extend range to top / bottom of visible rows |
| **⌘ / Ctrl + A** | select every visible row |
| **Esc** | clear selection (focused row stays) |

`anchor` is the pivot for shift-extend. Plain click and ⌘-click reset it to the clicked row; shift-click leaves it untouched. Access it from `useTreeSelection()`:

```tsx
const {
  selectedIds, anchor,
  clickSelect, moveSelect, selectAll,
  setSelectedIds, clear, isSelected,
} = useTreeSelection();
```

`clickSelect(id, { shift, meta })` and `moveSelect(id, { extend })` are also exposed for consumers building custom row components.

## CRUD adapter (delete / rename / new / cut+copy+paste)

```ts
import type { TreeAdapter } from '@djangocfg/ui-tools/tree';

const adapter: TreeAdapter<FsNode> = {
  remove?:        (nodes) => Promise<void>;
  rename?:        (node, nextName) => Promise<void>;
  createFile?:    (parent, name) => Promise<void>;       // parent === null → root
  createFolder?:  (parent, name) => Promise<void>;
  duplicate?:     (nodes) => Promise<void>;
  move?:          (nodes, target, position) => Promise<void>;   // DnD + cut+paste
  copy?:          (nodes, target, position) => Promise<void>;   // copy+paste
  validateName?:  (name, ctx) => string | null;          // null = ok; string = error to show
};
```

Every method is **optional**. Tree only exposes the corresponding context-menu item / hotkey when the matching method is defined. So an inspection-only tree (`adapter={{}}` or no adapter) gets no destructive actions — no greyed-out items, just nothing.

`window.dialog.confirm / prompt / alert` (from `@djangocfg/ui-core/lib/dialog-service`) drives every flow:

- **Delete** — confirms via `dialog.confirm({ variant: 'destructive' })`, then calls `adapter.remove`.
- **New file / folder** — prompts for a name via `dialog.prompt`, validates via `adapter.validateName`, then calls `adapter.createFile/createFolder`.
- **Rename (no inline)** — prompts via `dialog.prompt` and calls `adapter.rename`. When `enableInlineRename` is on, the menu item opens the in-row input instead.
- **Errors** — surface as `dialog.alert` and re-open the rename input on validation failure.

## Inline rename

Set `enableInlineRename` (requires `adapter.rename`):

- F2 opens the inline `<input>` for the focused row.
- Enter / blur commits → `adapter.rename(node, nextName)`.
- Escape cancels.
- The base name is pre-selected (Finder style — `foo.txt` highlights `foo`).
- Container hotkeys (delete / arrows / F2) are paused while the input is mounted.

```tsx
const { renamingId, startRename, cancelRename, commitRename } = useTreeRename();
```

## Finder hotkeys

Set `enableFinderHotkeys` (only fires when the tree container has focus):

| Combo | Action |
| --- | --- |
| `F2` | rename |
| `⌘⌫` / `Delete` | delete |
| `⌘D` | duplicate |
| `⌘N` | new file |
| `⌘⇧N` | new folder |
| `⌘C` / `⌘X` / `⌘V` | copy / cut / paste |

Each binding is further gated by the adapter — `⌘⌫` does nothing when `adapter.remove` is undefined. Descriptions register with `useHotkeyHelp` for the global cheat sheet.

## Clipboard (cut / copy / paste)

Tree's clipboard is in-memory and tree-local (not the system clipboard) — that lets us dim cut rows the way Finder/Explorer do and gives a single source of truth across menu / hotkey / DnD entry points.

```tsx
const { clipboard, isCut, cut, copy, paste, clear } = useTreeClipboard();
```

Paste calls `adapter.move` for cut, `adapter.copy` for copy. Cut + paste clears the clipboard; copy + paste retains it. Errors → `dialog.alert`.

CSS hook for custom row styling: `[data-tree-row][data-clipboard="cut"]`.

## Drag and drop

Set `enableDnD` (requires `adapter.move`). Powered by `@dnd-kit/core` with pointer + keyboard sensors.

| Gesture | Behaviour |
| --- | --- |
| Drag a row | If it's part of the current selection, the whole selection drags together; otherwise just that row |
| Hover over top third of a row | Drop indicator above (reorder `before` sibling) |
| Hover over middle of a folder | Folder lights up (drop `inside`) |
| Hover over bottom third of a row | Drop indicator below (reorder `after` sibling) |
| Hover over empty area below the last row | Root drop target (drop into project root) |
| Drop onto self / descendant | Rejected by `defaultCanDrop` — indicator turns red |

```tsx
<TreeRoot
  adapter={adapter}
  enableDnD
  canDrop={({ source, target, position }) => {
    // Layer your domain rules on top of the built-in cycle check.
    if (target?.data.isReadonly) return false;
    return true;
  }}
/>
```

`useTreeDnd()` exposes `draggingIds`, `dropTarget`, `commitDrop`, `cancelDrag`, and `isAllowedDrop` for custom row renderers.

CSS hooks: `[data-tree-row][data-dragging="true"]` on the source row, `[data-tree-drop="before|after|inside"]` on `<TreeDropIndicator>`.

## Empty-area context menu

Tree's scroll container always ends with a `<TreeEmptyArea>` that fills the remaining vertical space. Right-clicking on whitespace below the last row opens a menu with the built-in actions that apply to "no row" — `New file`, `New folder`, and `Paste` (if clipboard has items). Items hide automatically when the matching adapter method is undefined; with no relevant items, the area renders as plain whitespace and right-click falls through to the browser default.

The empty area is also the **root drop target** during DnD — drop here to move/copy into the project root.

## Context menu

Two APIs, pick the lighter one when it fits.

**Short-form — `contextMenuActions`.** Pass a resolver that returns a flat list of actions per row. Tree builds a themed `<ContextMenu>` for you and **merges your items with built-in adapter actions** automatically. Use the string `'separator'` for dividers; mark dangerous rows with `destructive: true`.

```tsx
import { Star } from 'lucide-react';

<TreeRoot<FsNode>
  data={data}
  getItemName={(n) => n.data.name}
  adapter={fsAdapter}
  contextMenuActions={({ row, selectedNodes }) => [
    { id: 'star', label: 'Star', icon: Star,
      onSelect: () => star(selectedNodes) },
  ]}
/>
```

Built-in delete / rename / duplicate / cut / copy / paste / new-file / new-folder appear automatically based on adapter methods.

- Right-clicking a row outside the current selection switches selection to that single row first (Finder/Explorer convention), so destructive actions on multi-selection stay predictable.
- Limit / reorder the built-in items via `defaultMenuItems={['rename', 'delete']}`. Pass `[]` to suppress them entirely while still using the adapter for hotkeys / DnD.

**Full control — `renderContextMenu`.** Drop down when you need submenus, checkbox / radio items, custom JSX, or want to compose with non-default ContextMenu primitives. `renderContextMenu` wins if both props are set.

## Localisation

Every user-facing string lives on `TreeLabels` and is overridable via the `labels` prop:

```tsx
<TreeRoot
  labels={{
    confirmDeleteTitle: (n) => n === 1 ? 'Удалить элемент?' : `Удалить ${n} элементов?`,
    actionRename: 'Переименовать',
    actionNewFolder: 'Новая папка',
    invalidNameEmpty: 'Имя не может быть пустым',
    // …all of TreeLabels is partial
  }}
/>
```

Defaults are English. Function-shaped entries (`confirmDeleteTitle(count)`, `confirmDeleteMessage(names)`, `searchMatches(n)`, `duplicateSuffix(name)`) receive runtime context for proper plurals / interpolation.

## Appearance

```tsx
<TreeRoot
  appearance={{
    variant: 'explorer',      // 'explorer' (default) | 'list'
    density: 'cozy',          // 'compact' | 'cozy' | 'comfortable'
    accent: 'default',        // 'subtle' | 'default' | 'strong'
    radius: 'sm',             // 'none' | 'sm' | 'md'
    iconStrokeWidth: 1.5,
    indentGuideOpacity: 0.4,
    showActiveIndicator: true,
    rowHeight: 30, iconSize: 18, fontSize: 14, gap: 10, indent: 20,
  }}
/>
```

### Variant — `explorer` vs `list`

`variant` is a high-level look that sets sensible defaults for three
fields (`hideLeafIcons`, `hideFolderIcons`, `rowSizing`,
`showActiveIndicator`); any of those passed explicitly still wins.

| Variant | Look | Defaults |
| --- | --- | --- |
| `'explorer'` (default) | Classic file/folder tree | leaf + folder icons, **fixed** single-line rows, active bar on |
| `'list'` | macOS-sidebar / **chat-history** list | **no icons** (chevron only on groups), **auto-height** rows (multi-line label friendly), quiet selection (no active bar) |

```tsx
// A grouped chat-history sidebar (date / topic buckets → sessions),
// multi-line rows (title + dimmed meta), no file glyphs:
<TreeRoot<Payload>
  data={groupedSessions}
  getItemName={(n) => label(n)}
  appearance={{ variant: 'list', indent: 10 }}
  showIndentGuides={false}
  renderLabel={({ node }) => /* title + meta */ null}
/>
```

Fine-grained fields (override the variant):

- `hideLeafIcons` / `hideFolderIcons` — drop the per-row icon (chevron stays).
- `rowSizing: 'fixed' | 'auto'` — `auto` turns `rowHeight` into a *minimum*
  so a multi-line label grows the row instead of overflowing.

The resolved appearance is exposed on the root container as CSS variables:

```
--tree-row-height
--tree-icon-size
--tree-icon-stroke
--tree-font-size
--tree-gap
--tree-indent
--tree-guide-opacity
```

### VSCode-style row state

| State | Look |
| --- | --- |
| Hover | subtle neutral wash |
| Focused (keyboard nav, not selected) | slightly stronger neutral |
| Selected, tree NOT focused | muted neutral block |
| Selected + tree focused-within | primary tint + colored text + left active bar |
| Search match | thin primary ring |
| Cut (clipboard) | `opacity-60`, dimmed |
| Disabled | dimmed + cursor-not-allowed |

## Activation modes

| Mode | Single click | Double click |
| --- | --- | --- |
| `'single-click'` *(default)* | activate `{ preview: false }` | activate `{ preview: false }` |
| `'double-click'` | select + focus only | activate `{ preview: false }` |
| `'single-click-preview'` *(VSCode / Cursor)* | activate `{ preview: true }` | activate `{ preview: false }` |

Folders ignore this — they always toggle on single click and never call `onActivate`. Keyboard `Enter` / `Space` always activates with `{ preview: false }`.

## Hooks

| Hook | What it exposes |
| --- | --- |
| `useTreeContext()` | full `TreeContextValue<T>` — use as a last resort |
| `useTreeRows()` | flat row list (visible only) |
| `useTreeSelection()` | `selectedIds`, `anchor`, `clickSelect`, `moveSelect`, `selectAll`, `setSelectedIds`, `clear`, `isSelected` |
| `useTreeExpansion()` | `expandedIds`, `expand`, `collapse`, `toggle`, `expandAll`, `collapseAll`, `isExpanded` |
| `useTreeFocus()` | `focusedId`, `setFocus` |
| `useTreeSearch()` | `query`, `setQuery`, `matchingIds`, `matchCount` |
| `useTreeRename()` | `renamingId`, `enabled`, `startRename`, `cancelRename`, `commitRename` |
| `useTreeClipboard()` | `clipboard`, `isCut`, `cut`, `copy`, `paste`, `clear` |
| `useTreeDnd()` | `active`, `draggingIds`, `dropTarget`, `beginDrag`, `setDropTarget`, `commitDrop`, `cancelDrag`, `isAllowedDrop` |
| `useTreeActions()` | imperative bag: `expand*` / `collapse*` / `refresh*` / `activate` |
| `useTreeLabels()` | resolved `TreeLabels` (with overrides applied) |

## Defaults

| Option | Default |
| --- | --- |
| `selectionMode` | `'single'` |
| `activationMode` | `'single-click'` |
| `enableSearch` | `false` |
| `enableTypeAhead` | `true` |
| `enableInlineRename` | `false` |
| `enableFinderHotkeys` | `false` |
| `enableDnD` | `false` |
| `showIndentGuides` | `false` |
| `persistSelection` | `false` |
| `appearance.density` | `'cozy'` |
| `appearance.accent` | `'default'` |
| `appearance.radius` | `'sm'` |
| `appearance.showActiveIndicator` | `true` |
| `appearance.iconStrokeWidth` | `1.5` |
| `appearance.indent` | `16` |

## Filtering nodes

`filterNode` is a single predicate that decides which nodes appear at all. Nodes returning `false` (and their descendants) are excluded from rendering, keyboard navigation, and search.

```tsx
const [showHidden, setShowHidden] = useState(false);

<TreeRoot
  data={data}
  getItemName={(n) => n.data.name}
  filterNode={(n) => showHidden || !n.data.name.startsWith('.')}
/>
```

This is intentionally minimal — Tree is generic over `T` and has no opinion on what "hidden" means in your domain. If your backend already provides flags like `entry.isHidden`, use them directly.

> **Frontend note.** From the browser you cannot read OS-level hidden attributes (`FILE_ATTRIBUTE_HIDDEN`, `kIsInvisible`). Either filter by name (Unix dot-prefix is the de-facto convention), or let your backend determine those flags and forward them in `node.data`.

## File icons

Tree is generic over `T` — it has no opinion on whether nodes are files. For a ready-made VSCode-style icon set, use the `file-icon` companion subpath:

```tsx
import { TreeRoot } from '@djangocfg/ui-tools/tree';
import { createFileIconSlot } from '@djangocfg/ui-tools/file-icon';

<TreeRoot
  data={data}
  getItemName={(n) => n.data.name}
  renderIcon={createFileIconSlot({ getName: (n) => n.data.name })}
/>
```

The icon SVGs are vendored statically from `material-file-icons` (MIT) — no runtime dependency, no install step, synchronous resolution.

## Status

| Feature | Status |
| --- | --- |
| Multi-selection (anchor / shift / ⌘+A) | ✅ |
| `TreeAdapter` + built-in CRUD via `window.dialog` | ✅ |
| `<FinderTree>` preset | ✅ |
| Inline rename (F2, auto-select base) | ✅ |
| Finder hotkeys (⌘⌫ F2 ⌘D ⌘N ⌘⇧N ⌘C ⌘X ⌘V) | ✅ |
| Clipboard (cut / copy / paste, dimmed cut state) | ✅ |
| Drag-and-drop (`@dnd-kit/core`) | ✅ |
| Empty-area context menu (`new file / new folder / paste` on background) | ✅ |
| Undo / Redo | n/a (host's job — implement in your adapter / Wails-Go layer) |
| Virtualization | out of scope (wrap with `@tanstack/react-virtual`) |
| Multi-tree cross-DnD | out of scope |
