# DiffViewer

Line-by-line diff viewer with unified or split layout. Reuses the `prism-react-renderer` instance from `PrettyCode` for optional syntax highlighting — no second highlighter is loaded.

Pass either `oldCode` + `newCode` (computed diff) or a pre-built `patch` string (unified format).

```tsx
import { DiffViewer } from '@djangocfg/widget-code/diff-viewer';

<DiffViewer
  oldCode="const x = 1;"
  newCode="const x = 2;\nconst y = 3;"
  language="ts"
  layout="unified"
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `oldCode` / `newCode` | `string` | — | Source pair to diff. Mutually exclusive with `patch`. |
| `patch` | `string` | — | Pre-computed unified diff. Mutually exclusive with `oldCode`/`newCode`. |
| `layout` | `'unified' \| 'split'` | `'unified'` | Single column vs side-by-side. |
| `language` | `Language \| string` | — | Prism language key for highlighting. Omit for plain monospace. |
| `oldTitle` | `string` | — | LHS file header label. |
| `newTitle` | `string` | — | RHS file header label. |

Storybook: `apps/storybook/stories/ui-tools/dev/DiffViewer.stories.tsx`

---

Adapted from jalcoui (MIT).
