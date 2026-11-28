# JsonTree

Interactive JSON viewer with collapsible nodes, search, copy-path, and a
hover-revealed toolbar (ChatGPT-style).

```tsx
import { JsonTree } from '@djangocfg/ui-tools/json-tree';

<JsonTree data={anyJson} />
```

That covers 95% of cases. The remaining props live in `types.ts`.

## Provenance

Ported from [jalco/ui's `JsonViewer`](https://ui.justinlevine.me/docs/components/json-viewer)
(MIT, Justin Levine — full source vendored at
`packages/@sources/jalcoui-main/`). Modifications:

- Removed the Shiki theme module (65 editor palettes) — we keep one
  Tailwind-token palette that follows the host light/dark theme via
  `useResolvedTheme`. No `colorTheme` prop.
- New `toolbar` prop (`'auto' | 'always' | 'never'`). `'auto'` fades the
  toolbar in on hover or keyboard focus inside the container (the
  ChatGPT pattern). `'always'` is for debug panels; `'never'` strips it
  entirely.
- New `actions` prop selects which buttons to mount. Default omits the
  download button — file-viewer hosts shouldn't offer "Download" for
  JSON that already lives on disk.
- `bordered={false}` strips the card frame for embedded use; the second
  source of borders (`JsonContent` wrapper) is gone too.
- Toolbar buttons use ui-core `<Tooltip>` / `<Button>` / `<Input>` so
  they pick up shared focus/hover styling.

The original `react-json-tree`-based wrapper is gone; consumers that
called the legacy `<JsonTree mode="full" config={…}>` shape go through
`LegacyJsonTree` (default export) which adapts old props to the new
shape — see `legacyAdapter.tsx`.

## API

```ts
interface JsonTreeProps {
  data: unknown;
  title?: string;
  rootName?: string;                       // default 'root'
  toolbar?: 'auto' | 'always' | 'never';   // default 'auto'
  actions?: ('search' | 'expand' | 'copy' | 'download')[];
                                           // default ['search','expand','copy']
  defaultExpandedDepth?: number | true;    // default 2; true = expand all
  bordered?: boolean;                      // default true
  className?: string;
  downloadFilename?: string;               // default 'data.json'
}
```

### When to override which

| Goal | Set |
| --- | --- |
| Embed inside a pane that already draws border + bg | `bordered={false}` |
| Debug-panel feel (toolbar always visible) | `toolbar="always"` |
| Strip the toolbar entirely | `toolbar="never"` |
| Add a Download button (in-memory data) | `actions={['search','expand','copy','download']}` |
| Read-only display, no Search | `actions={['expand','copy']}` |
| Long config — open everything | `defaultExpandedDepth={true}` |

## Theme

The data-typed palette is hand-tuned per light/dark rather than wired to
semantic UI tokens — same convention as Chrome DevTools, Insomnia, and
Bruno. JSON inspectors carry their own contrast model; flattening keys
and values into theme pastels makes them illegible.

The component is **transparent by default** — no internal background,
so it inherits whatever surface the host provides. Pass `bordered`
explicitly when you want the card frame.

## Search

Hidden behind the magnifying-glass icon in the toolbar; toggling it
expands the whole tree so matches inside collapsed nodes become
visible. Matches highlight in both keys and string values; numeric and
boolean values match as text.

## Copy-path

Hover any row — a `⊕` icon appears on the right. Clicking it copies
the full JS access path (`root.dependencies["@tiptap/core"]`, including
bracket syntax for keys that aren't valid identifiers) to the clipboard.

## Legacy props (back-compat)

The default export — `LegacyJsonTree` — accepts the pre-refactor shape
so existing call sites compile unchanged:

```tsx
// Old code still works
import JsonTree from '@djangocfg/ui-tools/json-tree';
<JsonTree
  data={obj}
  mode="full"
  config={{
    maxAutoExpandDepth: 3,
    showActionButtons: true,
    autoHideToolbar: true,
  }}
/>
```

`legacyAdapter.ts` maps:

- `mode` → `bordered` + `defaultExpandedDepth` defaults
- `config.maxAutoExpandDepth` → `defaultExpandedDepth`
- `config.showExpandControls / showCopy / showDownload / showActionButtons`
  → `actions` array
- `config.autoHideToolbar` → `toolbar: 'auto'` (vs `'always'`)
- `jsonTreeProps` → silently dropped (react-json-tree-specific)

Migrate to the new API at your own pace — new code should target
`{ JsonTree }` from the named export.

## Lazy entries

`@djangocfg/ui-tools/json-tree` ships two lazy wrappers:

- `LazyJsonTree` — legacy shape, default export. Old code keeps working.
- `LazyJsonTreeNew` — new shape, for greenfield code.

Both wrap the renderer in `React.lazy` (~80KB chunk including the
toolbar UI and Tailwind utility surface).

## Related

- `@djangocfg/ui-tools/json-editor` — when you need to **edit** JSON
  (drag-reorder, JSON Schema validation, undo/redo). Lazy-loads
  `json-edit-react` (~19KB gz) on demand. Use for debug Store panels
  and config admin UIs; for read-only display always reach for
  `json-tree` first.
- `@djangocfg/widget-kit/pretty-code` — read-only syntax-highlighted code
  blocks (any language). Use when you have a JSON **string** to display
  unmodified.
