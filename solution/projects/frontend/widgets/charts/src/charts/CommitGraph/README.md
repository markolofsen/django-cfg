# CommitGraph

Git-style commit rail visualisation. Computes rail topology from `parents` and renders SVG rails + edges. Lane colors come from `useStylePresets()` so every theme preset re-skins consistently.

```tsx
import { CommitGraph } from '@djangocfg/ui-tools/commit-graph';

<CommitGraph
  commits={[
    { hash: 'a1b2c3d', message: 'init', author: { name: 'Mark' }, date: '2025-01-01', parents: [] },
    { hash: 'd4e5f6g', message: 'feat: auth', author: { name: 'Mark' }, date: '2025-01-02', parents: ['a1b2c3d'] },
  ]}
/>
```

## Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `commits` | `Commit[]` | — | Commits in topological order (newest first). Merge = two+ `parents`. |
| `truncateHash` | `number` | `7` | Number of hash characters to display. |
| `railWidth` | `number` | `24` | Pixel width per rail column. |

Storybook: `apps/storybook/stories/ui-tools/visual/CommitGraph.stories.tsx`

---

Adapted from jalcoui (MIT).
